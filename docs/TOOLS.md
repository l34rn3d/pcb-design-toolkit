# Tool inventory and portability

The workstation survey found KiCad 10.0.6, its manager, Schematic Editor (`eeschema`), PCB Editor (`pcbnew`), Gerber Viewer (`gerbview`), PCB Calculator, bitmap converter and drawing-sheet editor. Symbol/footprint/template packages were from the 7.0 series; install compatible current library packages on a fresh machine and verify exact part footprints rather than assuming the survey's library versions are suitable.

A Konnect v0.13.0 standalone binary and receipt were present locally. This package retains the reusable installer/gateway, not the binary or receipt. No independently verified live IPC session is claimed. The libngspice shared library was installed, but no standalone `ngspice` or `freerouting` executable was found on PATH. Presence of libngspice alone does not prove schematic simulation works.

Reusable resources included layout engineering references, native DRC/ERC report handling, project trial copying, pinned release verification and MCP stdio plumbing. An additional one-board fabrication validator embedded geometry, file counts and board hashes; its reusable inventory concept is replaced here by `verify-exports.py`. Its project-specific registration assertions and generated outputs are not suitable as general rules.

Core GUI/CLI tools and libraries must be installed using the operating system's official KiCad packages. Check CLI/editor versions, library resolution and operation-specific help. The included skill makes no assumption about project directory, board stem, circuit, manufacturer, layer count, service subscription or agent host. Its native Bash verifier needs a Bash environment; the optional Konnect installer currently supports Linux x86-64 only.

Upstream documentation:

- [KiCad downloads](https://www.kicad.org/download/)
- [KiCad IPC API](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/)
- [Pinned Konnect release](https://github.com/mixelpixx/Konnect/releases/tag/v0.13.0)

No local user settings, design files, hardware specifications, logs, conversation history or account details belong in a public package. Runtime reports may contain the current user's local project paths; keep them out of this source repository.
