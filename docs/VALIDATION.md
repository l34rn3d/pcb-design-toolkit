# Validation evidence

Validated locally on 7 October 2026. No test modified original project files or installed a new dependency.

## Automated checks

The Python unittest suite covers MCP initialize/notifications/pagination/error handling, child timeout cleanup, complete trial copying, overwrite/recursive-copy/symlink refusal, pinned release identity/digest requirements and archive extraction that copies only the executable.

Verifier regressions use a mock CLI to exercise clear scoped checks, hierarchical ERC findings, DRC errors/warnings/exclusions, opens, parity mismatches, disabled checks, omitted ERC, unknown schemas, incomplete severity coverage, malformed/missing reports, process failures, source changes, absent project context and conflicting schematic roots. These tests establish adapter behavior, not KiCad's own electrical correctness.

Gerber inventory tests cover file hash/size reporting, mismatched layer count, truncated files and export-directory escape rejection. Source packaging checks verify skill metadata, local links, allowed file types and absence of user-specific absolute paths. The local release review also scanned source and ZIP members for the removed originating project's name/domain and specific board/path names, with no matches. That review does not store those names in the public package.

The bundled skill-creator validator accepted the skill's frontmatter and structure. Release ZIPs are CRC-tested and every archived file is compared with its source.

## Native KiCad smoke tests

A disposable copy of the installed `interf_u` demo exercised trial preparation and KiCad 10.0.6 DRC, same-stem schematic parity and hierarchical ERC JSON parsing. The verifier returned 1 (review required), retaining actual DRC/parity findings and disabled checks rather than claiming a clean board. Source hashes remained unchanged. This demo is not a qualified production design or a deliberately injected parity fixture; the mock regression independently covers the known mismatch branch.

Native Gerber export produced seven requested layer files and a two-layer Gerber job in the disposable test directory. The inventory helper accepted them and reported hashes with its explicit geometry/DFM limitations. Demo CAD and generated reports/exports are excluded from this release.

## Not established

No new download/install, cross-platform run, component-pin verification, simulation, geometric Gerber/drill registration or manufacturing approval was performed. Optional MCP functionality must still be probed on each target user's disposable project. GitHub Actions configuration is included but has not run remotely. Native tests used KiCad 10.0.6; other versions are guarded by runtime capability/schema checks rather than claimed compatible without testing.

## Live API routing test

The packaged gateway connected to a separate KiCad 10.0.6 PCB Editor instance holding the disposable demo. It verified the exact requested board over IPC. One existing 13.97 mm bottom-copper trace was deleted, saved, then recreated with its original net, endpoints and 0.4318 mm width through `route_trace`, and saved again. Live readback matched the original 731-trace geometry inventory (the replacement has a new UUID).

Native DRC/parity checks showed one open connection after deletion and zero after recreation. The final findings matched the live-test baseline: 3 geometric findings and 22 parity findings remained in the demo; this was not a clean production board. The earlier refill-in-memory smoke test had 2 geometric findings, so comparisons here use the same live-test command/options throughout.

This establishes native copper creation and save persistence, not automatic whole-board routing or obstacle-aware shove behavior. Interactive undo and reopening the editor were not separately exercised.

Two integration behaviors mattered: multiple KiCad instances used different IPC sockets, and the sandbox denied access to the test socket. The test used the editor's actual socket via `KICAD_API_SOCKET` and an authorized process outside the sandbox. No global agent configuration was changed. The gateway probe was corrected to require positive IPC availability and exact requested-board identity, including a regression for transport-success/live-access-failure results.
