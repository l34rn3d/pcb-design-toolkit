# PCB Design Toolkit

A project-independent KiCad instruction set and installable AI-agent skill for PCB placement, routing, review, verification and manufacturing handoff.

The package contains reusable guidance and Python/Bash helpers. Install KiCad and its libraries separately. No board designs, personal configuration, credentials, downloaded binaries or fabrication files are included.

## Included tools

| Tool | Purpose |
| --- | --- |
| `skills/pcb-layout-engineer/SKILL.md` | Agent instructions; usable as a plain instruction set too |
| `references/` within the skill | Placement, routing, power/returns, mechanics, review, drafts, manufacturing and external handoffs |
| `scripts/verify-board.sh` within the skill | Native DRC, schematic parity, optional ERC, source hashes and scoped reports |
| `scripts/inspect-tools.py` within the skill | Portable PATH/version discovery |
| `scripts/verify-exports.py` within the skill | Native Gerber-job inventory/hashes; does not replace viewer/DFM review |
| `scripts/kicad/install.py` within the skill | Optional pinned Konnect download with SHA-256 verification; Linux x86-64 |
| `scripts/kicad/gateway.py` within the skill | Configurable trial-copy preparation, MCP probing, tool discovery and stdio launch |

## Install the skill

Copy the complete `skills/pcb-layout-engineer` folder into the skill directory supported by your agent. For Codex's conventional user skill folder:

```sh
mkdir -p "$HOME/.codex/skills"
cp -R skills/pcb-layout-engineer "$HOME/.codex/skills/"
```

If that destination already exists, review it before replacing it. A custom agent home may use a different skills directory. The skill folder is self-contained: its references and helpers move with it. Other agents can load `SKILL.md` directly and follow its linked references without Codex-specific tools.

Example request:

> Use $pcb-layout-engineer to review my KiCad project, preserve its connectivity and mechanical anchors, improve placement/routing, and return editable files with fresh verification reports. Mark unresolved requirements clearly.

## Requirements and first checks

Install [KiCad](https://www.kicad.org/download/) with matching symbol, footprint and optional 3D libraries. Use a currently supported version and validate CLI capabilities. Native wrapper compatibility was smoke-tested with KiCad 10.0.6; older/newer versions must pass capability/schema checks. Bash and Python 3 are required for the verifier; the Python helpers use only the standard library. Python 3.10+ is the tested baseline.

From this checkout:

```sh
python3 skills/pcb-layout-engineer/scripts/inspect-tools.py
bash skills/pcb-layout-engineer/scripts/verify-board.sh /path/to/design.kicad_pcb /path/to/design.kicad_sch
python3 skills/pcb-layout-engineer/scripts/verify-exports.py /path/to/exports/design-job.gbrjob --expected-layers 4
```

Paths are examples; use your own project and expected layer count. The verifier creates fresh reports under the board directory's `temp/` without saving the board. Exit 0 means only its declared automated scope passed; 1 means findings need review; 2 means a required check failed or is unknown. Engineering judgment, real package mappings, reference paths and fabrication approval remain separate.

For optional live PCB MCP access, follow [integration.md](skills/pcb-layout-engineer/references/integration.md). The installer pins Konnect v0.13.0 and is optional; GUI/CLI workflows do not require it. No Java autorouter, simulator or paid external service is required by this package.

## Validation and release

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check-package.py
python3 scripts/build-release.py
```

The builder creates `dist/pcb-design-toolkit.zip` for the repository and `dist/pcb-layout-engineer.zip` for skill installation, plus SHA-256 checksums. It uses a source allowlist and excludes caches, configuration and Git history. [Validation notes](docs/VALIDATION.md) describe test scope and limitations. [Tool inventory](docs/TOOLS.md) records packaged capabilities and external dependencies.

To publish, create a GitHub repository with your chosen name/visibility, then push this directory's reviewed source. This package does not embed an account, repository URL or project-specific remote. Generated ZIPs may be attached to a GitHub release.

## License

The instructions and helper code are MIT licensed; see [LICENSE](LICENSE). KiCad, its libraries, Konnect and external services retain their own licenses/terms. Third-party programs are downloaded from upstream or installed separately, not redistributed here.
