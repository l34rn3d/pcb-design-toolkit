# Native KiCad report contracts and verifier tests

## Scope
Use when implementing, modifying or diagnosing DRC/ERC wrappers. These contracts were observed with native KiCad 10.0.3; validate current CLI help and emitted schema before extending support. Do not assume all KiCad versions emit identical metadata.

## JSON adapters
- DRC schema: `https://schemas.kicad.org/drc.v1.json`. Findings are in `violations`, `unconnected_items`, and `schematic_parity`.
- ERC schema: `https://schemas.kicad.org/erc.v1.json`. Findings are nested in `sheets[].violations`; retain each sheet's `path`/`uuid_path` for actionable diagnostics.
- `included_severities` is metadata containing strings, not findings. `ignored_checks` is disabled-check inventory, not a violation list. Never flatten every top-level array into findings.
- Validate object root, supported schema, required finding arrays, severity coverage and disabled-check inventory. Missing data or unfamiliar structures become UNKNOWN, not empty/clean results.
- Exclusions and disabled checks are different: requesting all severities includes excluded findings but does not enable disabled checks. Record both and require reviewer disposition.
- With `--exit-code-violations`, observed native return codes were 0 for normal completion and 5 for reported violations. Unexpected codes or missing/malformed reports are failed verification, not proof of no errors. Reconfirm this contract for the installed version.

## Source and check scope
Native schematic parity uses the board's associated same-stem schematic. An explicitly supplied ERC root may differ: detect that conflict and identify both sources, rather than presenting the checks as correspondence evidence for one project.

Report exact requested checks and distinguish automated exit-code scope from manual engineering review and omitted optional checks. Omitted ERC can be outside a layout-only script's exit scope, but is never acceptable after schematic changes. A zero script exit is not overall board approval.

Hash claims cover only enumerated inputs. Existing files below the board directory do not necessarily include external hierarchy/library dependencies, symlinked directories or newly introduced context files. State inventory boundaries; use dependency resolution and membership rescans before claiming complete source-context integrity.

## Regression matrix
Test at least:
1. Valid DRC and hierarchical ERC with zero findings.
2. Errors, warnings and excluded findings.
3. Nonzero unconnected items and parity mismatches.
4. Disabled checks with otherwise clean reports.
5. Native process failure, missing/malformed report and unknown schema.
6. Incomplete severity coverage.
7. Missing project context and conflicting ERC/parity roots.
8. Optional omitted ERC with explicit scope wording.
9. Source changes and unreadable inputs.

Use mocked CLI responses for branch coverage, then run native checks on disposable, format-valid project fixtures. Confirm originals and copied input files remain unchanged. Mocks alone cannot establish native compatibility.

## Fixture validity and honesty
A native rejected schematic tests failure handling, not successful ERC parsing. Diagnose the native log before changing the wrapper. Replace or repair only a disposable fixture through a supported mechanism; preserve original inputs.

Do not combine a board from one project with an unrelated blank schematic and interpret zero parity findings as real correspondence proof. Such a fixture can smoke-test invocation/schema handling only. Use an actually corresponding populated schematic/PCB pair plus a deliberate known mismatch to validate parity detection. An empty schematic or a board without meaningful net assignments can produce zero counts without verifying intended electrical connectivity.

Keep native report examples and regression evidence separate from the fabrication verdict. Document exactly which behavior each test proved and which engineering checks remain untested.
