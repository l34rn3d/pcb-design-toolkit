# Native tools and optional MCP

Use the native KiCad editor for placement/routing and `kicad-cli` for supported checks/exports. New integrations should prefer the [KiCad IPC API](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/); inspect version-specific capabilities rather than assuming editor and CLI versions match.

The included Python-standard-library gateway supports the optional [Konnect v0.13.0 release](https://github.com/mixelpixx/Konnect/releases/tag/v0.13.0). Its installer targets Linux x86-64 and verifies the GitHub release asset SHA-256 before copying only the executable. It does not modify global configuration. KiCad 10.0.3+ is the gateway's minimum; confirm the needed tool's requirements separately. Other platforms may use native KiCad tools or their upstream Konnect package; this installer does not promise cross-platform MCP support.

From the skill directory:

```sh
python3 scripts/kicad/install.py
python3 scripts/kicad/gateway.py prepare --project /path/to/design.kicad_pro
python3 scripts/kicad/gateway.py doctor --project /path/to/temp/konnect-pilot/design.kicad_pro
python3 scripts/kicad/gateway.py probe --project /path/to/temp/konnect-pilot/design.kicad_pro
python3 scripts/kicad/gateway.py tools --project /path/to/temp/konnect-pilot/design.kicad_pro
python3 scripts/kicad/gateway.py tools --project /path/to/temp/konnect-pilot/design.kicad_pro --name TOOL_NAME
```

`prepare` copies the project directory with libraries/hierarchy, excluding temp/cache/repository/editor-state folders, and refuses existing destinations or symlinks. Use `--destination /path/to/trial` for a different destination. It cannot detect/remap every absolute or external relative dependency: inspect sheet/library references and prove native resolution in the copy before editing. Reusing the same board stem preserves associated project rules.

Open the trial PCB in the native editor and enable its API before probing. Socket discovery uses upstream behavior or `KICAD_API_SOCKET`; no user-specific socket is assumed. Read the probe results to establish the actual open project identity. An MCP handshake alone does not prove live IPC access. `probe` now exits nonzero unless the requested board is confirmed open over IPC. With several KiCad instances, inspect the actual editor socket and set `KICAD_API_SOCKET` to its `ipc://` endpoint; the default socket may belong to a manager or another editor. If the sandbox denies socket access, use the host's authorized local execution mechanism rather than weakening socket permissions. The gateway exposes upstream tools without a safety filter; inspect schemas and prefer IPC operations, avoiding schematic raw edits or silent headless fallback when native mechanisms exist.

An MCP host can launch the stdio endpoint with this command (replace paths):

```sh
python3 /path/to/skill/scripts/kicad/gateway.py serve --project /path/to/trial/design.kicad_pro
```

Registration is specific to the host. Install or change configuration only within the user's authorized scope. The endpoint uses `--client codex`; compatibility with other host identities needs separate validation. For a schema-reviewed explicit call, `gateway.py call --project PROJECT TOOL_NAME /path/to/arguments.json` accepts a JSON object file. Calls may mutate the open board; use a disposable copy and verify undo/save/reload, nets/rules, parity and DRC before trusting an editing integration.

Downloaded binaries/receipts live in the skill's `.cache/konnect/v0.13.0`. Receipt checks detect subsequent changes, not independent trust in GitHub metadata. Konnect is separately licensed under its upstream AGPL/commercial terms; it is not bundled or covered by this package's license. Recheck upstream release documentation before changing the pinned version.

The local live test successfully deleted and recreated one existing copper segment through IPC and saved it, with original trace geometry and native DRC counts restored. This verifies direct segment routing. It does not qualify automatic whole-board routing or obstacle-aware shove behavior; inspect the relevant tool/backend before relying on those capabilities.
