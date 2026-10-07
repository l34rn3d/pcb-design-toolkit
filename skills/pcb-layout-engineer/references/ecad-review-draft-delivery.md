# Editable ECAD review drafts

## Purpose
Deliver an actual editable design when topology, measurements or manufacturing approval are incomplete. A review draft is not a fabrication release; incomplete placement/routing and unverified mappings must remain conspicuous.

## Artifact-first sequence
1. Resolve only scope differences that change the design: number of channels, external versus integrated ADC, prototype passive style, and intended deliverable maturity.
2. Read project authority and preserve originals. Inventory existing CAD: a repaired PCB with assigned nets is not a matching schematic or evidence of circuit validation.
3. Check native authoring options. If raw schematic/board serialization is necessary, follow the skill entrypoint's version-aware copy/check procedure.
4. Establish a net-level circuit and create project + real-symbol wired schematic first. Add a corresponding placed, net-aware PCB. Checkpoint these artifacts before extended sourcing/routing work.
5. Document all provisional choices. If time expires, return the real schematic and placed board as UNROUTED and state what remains incomplete.
6. Run native checks and inspect the PDF/layout. Assemble a self-contained archive and test its integrity.

## Verification evidence
Use the installed CLI's help to confirm flags. Typical KiCad 10 commands:

```sh
kicad-cli sch erc --format json --output reports/ERC.json design.kicad_sch
kicad-cli sch export netlist --format kicadxml --output reports/native_netlist.xml design.kicad_sch
kicad-cli pcb drc --all-track-errors --severity-all --schematic-parity --format json --output reports/DRC.json design.kicad_pcb
```

Parse ERC findings from each schema-defined sheet's violations, not arbitrary metadata arrays. Report DRC violations, unconnected items and schematic parity independently.

Independently compare native XML netlist nodes `(ref, pin) -> net name` to PCB footprint/pad assignments `(ref, pad) -> net name`, using a version-aware parser or native API. Require identical keys and values; detect missing pads, extra pads and mismatched nets. This establishes connectivity correspondence, not physical package correctness, routing completion or analogue performance.

A useful honest report can state: schematic/ERC clear; all pin-pad assignments match; PCB placed but unrouted with opens; exact device mapping unresolved. Do not summarise this as “DRC clean” or “complete PCB.”

## Visual and archive acceptance
- Real symbols must be visible, with readable net labels, component values and pin text. Label-only connectivity is acceptable for a draft but should not scatter every passive as an isolated island. Inspect the full sheet at readable resolution; keep components out of borders/title blocks.
- Include same-stem `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, local libraries/tables, BOM, README, native reports/netlist and schematic PDF. Use `${KIPRJMOD}` rather than absolute host library paths.
- Exclude probes, caches and editor-local state from the archive by filtering; do not clean/delete retained work as part of verification.
- Verify ZIP integrity and required file presence. Check local-library references and rebuild paths after extraction; regeneration invalidates old reports and must rerun native checks.
- Lead delivery with the attachment and precise maturity: editable schematic + placed/unrouted board, or routed draft if actually verified. List unresolved blockers compactly and do not generate manufacturing files merely to make the package look complete.
