#!/usr/bin/env python3
"""Repo-local Konnect launcher and stdio MCP client; Python standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[2]
VERSION = "v0.13.0"
BINARY = ROOT / ".cache" / "konnect" / VERSION / "konnect"


def version_tuple(value):
    match = re.search(r"\b(\d+)\.(\d+)\.(\d+)", value)
    return tuple(map(int, match.groups())) if match else (0, 0, 0)


def require_kicad():
    result = subprocess.run(["kicad-cli", "version"], capture_output=True, text=True, timeout=15, check=True)
    version = result.stdout.strip()
    if version_tuple(version) < (10, 0, 3):
        raise RuntimeError(f"KiCad {version} is too old for this integration; install 10.0.3 or newer")
    return version


def verified_binary():
    receipt = json.loads(BINARY.with_name("receipt.json").read_text())
    if receipt["tag"] != VERSION or hashlib.sha256(BINARY.read_bytes()).hexdigest() != receipt["binary_sha256"]:
        raise RuntimeError("Konnect binary does not match its installation receipt")
    return str(BINARY)


IGNORED_DIRS = {"temp", ".git", ".cache", "__pycache__", ".venv", "node_modules"}


def ignored(directory, names):
    return [name for name in names if name in IGNORED_DIRS
            or name.endswith(("-backups", ".lck", ".kicad_prl"))]


def hashes(directory):
    result = {}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignored(root, dirs)]
        for name in files:
            if name not in ignored(root, files):
                p = Path(root) / name
                if p.is_symlink():
                    raise RuntimeError(f"Symlink dependency must be resolved before copying: {p}")
                result[str(p.relative_to(directory))] = hashlib.sha256(p.read_bytes()).hexdigest()
        for name in dirs:
            if (Path(root) / name).is_symlink():
                raise RuntimeError(f"Symlink directory must be resolved before copying: {name}")
    return result


def project_path(value):
    project = Path(value).expanduser().resolve()
    if project.suffix != ".kicad_pro" or not project.is_file():
        raise RuntimeError("Project must be an existing .kicad_pro file")
    return project


def prepare(project, destination=None):
    project = project_path(project)
    source = project.parent
    trial = Path(destination).expanduser().resolve() if destination else source / "temp/konnect-pilot"
    if trial == source or (source in trial.parents and trial.relative_to(source).parts[0] != "temp"):
        raise RuntimeError("Nested trial must be inside source/temp to avoid recursive copying")
    if trial in source.parents:
        raise RuntimeError("Trial cannot contain the source directory")
    if trial.exists():
        raise RuntimeError(f"Trial already exists; preserving it: {trial}")
    for suffix in (".kicad_pro", ".kicad_sch", ".kicad_pcb"):
        if not project.with_suffix(suffix).is_file():
            raise RuntimeError(f"Missing project file: {project.stem}{suffix}")
    before = hashes(source)
    trial.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, trial, ignore=ignored)
    copied = hashes(trial)
    if before != copied or before != hashes(source):
        raise RuntimeError("Source changed during copy; review the retained trial")
    (trial / "gateway-source-manifest.json").write_text(json.dumps({"source": str(source), "sha256": copied}, indent=2) + "\n")
    return {"project": str(trial / project.name), "board": str(trial / project.with_suffix(".kicad_pcb").name), "copied_files": len(copied)}


def configuration(directory, project):
    project = project_path(project)
    path = Path(directory) / "konnect.json"
    path.write_text(json.dumps({"transport": "stdio", "project_dir": str(project.parent),
                                "kicad_cli": shutil.which("kicad-cli"),
                                "kicad_binary": shutil.which("kicad"),
                                "log_level": "warn", "eager_toolsets": True}))
    return str(path)


class Client:
    def __init__(self, command, timeout=30):
        self.timeout = timeout
        self.inbox = queue.Queue()
        self.next_id = 0
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=None, text=True, bufsize=1)
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            for line in self.process.stdout:
                self.inbox.put(json.loads(line))
        except (ValueError, OSError) as exc:
            self.inbox.put(exc)
        finally:
            self.inbox.put(EOFError("Konnect closed its output"))

    def send(self, message):
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", **message}) + "\n")
        self.process.stdin.flush()

    def request(self, method, params):
        import time
        self.next_id += 1
        request_id = self.next_id
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Timed out waiting for {method}")
            try:
                message = self.inbox.get(timeout=remaining)
            except queue.Empty:
                raise TimeoutError(f"Timed out waiting for {method}") from None
            if isinstance(message, Exception):
                raise message
            if message.get("id") != request_id or "method" in message:
                # Notifications do not have response IDs. Refuse unsolicited
                # server requests rather than acknowledging capabilities we lack.
                if "method" in message and "id" in message:
                    self.send({"id": message["id"], "error": {"code": -32601, "message": "Unsupported client method"}})
                continue
            if "error" in message:
                raise RuntimeError(json.dumps(message["error"]))
            return message["result"]

    def initialize(self):
        result = self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                             "clientInfo": {"name": "pcb-kicad-gateway", "version": "1.0"}})
        if result.get("protocolVersion") not in ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"):
            raise RuntimeError(f"Unsupported MCP protocol: {result.get('protocolVersion')}")
        self.send({"method": "notifications/initialized"})
        return result

    def tools(self):
        tools, params = [], {}
        while True:
            result = self.request("tools/list", params)
            tools.extend(result["tools"])
            if not result.get("nextCursor"):
                return tools
            params = {"cursor": result["nextCursor"]}

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdout.close()


def probe_access(result):
    """Require positive native IPC and requested-board identity, not only MCP success."""
    if result.get("isError"):
        return False
    try:
        payload = json.loads(next(item["text"] for item in result.get("content", [])
                                  if item.get("type") == "text"))
        return payload.get("ipc_available") is True and payload.get("requested_open") is True
    except (StopIteration, ValueError, TypeError, AttributeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("doctor", "prepare", "serve", "probe"):
        action = sub.add_parser(name)
        action.add_argument("--project", required=name != "doctor", help="Path to .kicad_pro; use the trial project for live operations")
        if name == "prepare":
            action.add_argument("--destination", help="Trial directory; defaults to PROJECT_DIRECTORY/temp/konnect-pilot")
    tool_parser = sub.add_parser("tools")
    tool_parser.add_argument("--project", required=True)
    tool_parser.add_argument("--name", help="Show one tool's full schema; otherwise list names/descriptions")
    call_parser = sub.add_parser("call")
    call_parser.add_argument("--project", required=True)
    call_parser.add_argument("name")
    call_parser.add_argument("arguments", help="Path to JSON arguments file; inspect the tool schema first")
    args = parser.parse_args()
    if args.action == "prepare":
        print(json.dumps(prepare(args.project, args.destination), indent=2))
        return 0
    if args.action == "doctor":
        report = {"project": args.project, "project_exists": bool(args.project and Path(args.project).is_file())}
        for name, check in (("kicad", require_kicad), ("konnect", verified_binary)):
            try:
                report[name] = {"status": "PASS", "value": check()}
            except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as exc:
                report[name] = {"status": "BLOCKED", "reason": str(exc)}
        report["live_ipc"] = "UNKNOWN: run probe with the trial PCB open and KiCad API enabled"
        print(json.dumps(report, indent=2))
        return 0 if (not args.project or report["project_exists"]) and all(report[k]["status"] == "PASS" for k in ("kicad", "konnect")) else 2
    require_kicad()
    binary = verified_binary()
    with tempfile.TemporaryDirectory(prefix="pcb-konnect-") as directory:
        command = [binary, "--client", "codex", "--config", configuration(directory, args.project)]
        if args.action == "serve":
            if sys.stdin.isatty():
                raise RuntimeError("serve is an MCP stdio endpoint; use probe from a terminal")
            return subprocess.call(command)
        client = Client(command)
        try:
            initialized = client.initialize()
            tools = client.tools()
            if args.action == "probe":
                names = {tool["name"] for tool in tools}
                results = {"initialize": initialized, "tool_count": len(tools), "results": {}}
                for name in ("get_installation_info", "open_project"):
                    if name not in names:
                        raise RuntimeError(f"Missing required read-only tool: {name}")
                    arguments = {"path": str(project_path(args.project))} if name == "open_project" else {}
                    results["results"][name] = client.request("tools/call", {"name": name, "arguments": arguments})
                print(json.dumps(results, indent=2))
                print("Read the open_project result: handshake success alone does not prove live board access.", file=sys.stderr)
                return 0 if (not any(r.get("isError") for r in results["results"].values())
                             and probe_access(results["results"]["open_project"])) else 1
            if args.action == "tools":
                result = [t for t in tools if t["name"] == args.name] if args.name else [
                    {"name": t["name"], "description": t.get("description", "")} for t in tools]
                if args.name and not result:
                    raise RuntimeError(f"Unknown tool: {args.name}")
            else:
                if args.name not in {t["name"] for t in tools}:
                    raise RuntimeError(f"Unknown tool: {args.name}")
                arguments = json.loads(Path(args.arguments).read_text())
                if not isinstance(arguments, dict):
                    raise ValueError("Arguments must be a JSON object")
                result = client.request("tools/call", {"name": args.name, "arguments": arguments})
            print(json.dumps(result, indent=2))
            return 1 if isinstance(result, dict) and result.get("isError") else 0
        finally:
            client.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, EOFError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as exc:
        print(f"Gateway stopped: {exc}", file=sys.stderr)
        sys.exit(2)
