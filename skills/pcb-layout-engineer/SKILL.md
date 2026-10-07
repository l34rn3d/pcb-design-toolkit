---
name: pcb-layout-engineer
description: Design, modify, review, and verify KiCad PCB layouts and editable ECAD drafts, including placement, routing, return paths, native checks, and manufacturing handoff. Use with an existing project or explicit new circuit requirements.
metadata:
  short-description: KiCad PCB layout, review, and verification
---

# PCB Layout Engineer

Produce editable, understandable KiCad designs with verified electrical constraints. Prioritize electrical correctness, power/signal integrity, mechanics, assembly and service access before visual cleanliness. A floorplan without a verified schematic/netlist is a mechanical mock-up, not an electrically validated design.

## Establish authority and tools

Inspect the project's instructions, working-tree changes, schematic hierarchy, PCB correspondence, local libraries, net classes/custom rules, outline, mechanical anchors and layer stack. Preserve unrelated work and good existing placement/routing. Use a complete project trial copy for substantial experiments, preserving same-stem project files, hierarchy, rules and library resolution. Coordinate competing editor saves.

Check installed `kicad-cli version` and operation-specific `--help`. Prefer verified native IPC for live PCB edits, the native editor for interactive work, and CLI for checks/exports. CLI export commands do not place components or route tracks. Read [integration.md](references/integration.md) for the optional pinned Konnect gateway and capability checks. The skill does not require MCP or a particular agent host.

Verify exact orderable part/package pin-to-pad mapping, connector mating orientation, dimensions, ratings, voltage/current requirements and manufacturer rules against project authority and authoritative datasheets. Record revision/page/figure where useful. Unknowns remain UNKNOWN. Seek a decision only when a proposed change exceeds authorized scope or changes circuit functionality; continue unaffected work. Tool availability does not authorize external uploads, purchases or configuration changes.

Use supported native mechanisms for writes. If file serialization is necessary, first establish format/version support and preserve a full copy; use a version-aware parser/serializer and reopen/check/diff with KiCad. Regex edits or merely parseable files do not prove integrity. Never silently relax rules, suppress findings, change connectivity, or substitute parts to make layout easier.

## Plan and place

Before moving components, identify fixed mechanics, functional groups, critical nets, reference/plane strategy, routing corridors and unknown requirements. Read [placement.md](references/placement.md) when arranging components.

Place connectors for cable/access constraints, protection near entry, bypass components for short actual pin-to-capacitor return loops, crystals around oscillator pins, and switcher hot-loop parts per vendor guidance. Keep sensitive analogue/RF and high-impedance nodes away from switching/current paths. Avoid arbitrary ground splits. Preserve probe, mounting, debug and rework access. Check native copper/pad and mechanical views before routing.

## Route and review

Read [routing.md](references/routing.md) for topology/critical-net decisions and [power-integrity.md](references/power-integrity.md) for current, return and thermal constraints. Establish reference continuity and filled-plane connections early. Prioritize constrained power/hot loops, RF/clocks, fast interfaces, sensitive analogue, high-current paths, then general signals; actual dependencies determine order.

Use purposeful routing, consistent widths/corners and deliberate vias; revisit placement when it causes detours or plane cuts. Length tuning requires real delay/skew requirements. Controlled impedance requires the actual fabricator stackup and reference geometry. Autorouting trials must preserve critical work and receive independent review. Stitch only for an electrical purpose, never across isolation barriers.

For requested external layout handoffs, read [external-layout-placement.md](references/external-layout-placement.md) and [external-layout-stackups.md](references/external-layout-stackups.md). Verify current service behavior; a ground layer's name/class, its assigned net and its actual connected copper are separate facts. Upload only within the user's authorization.

## Verify exact deliverables

Read [review-checklist.md](references/review-checklist.md). Run fresh native DRC on the exact final board, inspect warnings/exclusions and disabled checks, verify routing completion and same-project schematic parity. Run ERC after schematic edits; otherwise disclose its scope. Visually inspect the schematic and native PCB/mechanical views. Neither ERC nor parity establishes datasheet correctness.

```sh
bash <skill-directory>/scripts/verify-board.sh /path/to/design.kicad_pcb /path/to/design.kicad_sch
```

The helper requires Bash, Python 3 and a compatible KiCad CLI. `KICAD_CLI` may select one executable/wrapper. Reports go to a fresh board-directory `temp/pcb-verify-*` folder. Exit 0 covers requested native checks, parity, project-file presence and enumerated-file integrity only; exit 1 means findings/disabled checks need review; exit 2 means required verification failed or is unknown. Omitted ERC and manual engineering review are outside exit scope. It refills zones in memory without saving them and does not generate manufacturing outputs. Read [native-check-report-contract.md](references/native-check-report-contract.md) when changing report adapters.

Record source hashes, tool versions, dimensions/layers, routing status, DRC/ERC/parity findings and exclusions, via count when measured, rule/impedance evidence, and unresolved checks. Use PASS for scoped automated evidence, REVIEW for engineering judgment with a conclusion/evidence, and UNKNOWN for missing evidence. A clean DRC is not fabrication approval. Any final edit invalidates prior verification/export evidence.

## Deliver drafts or manufacturing packages

For an editable draft, read [ecad-review-draft-delivery.md](references/ecad-review-draft-delivery.md). Deliver real same-stem schematic/project/PCB files with local libraries and fresh reports; label unverified mappings and incomplete routing prominently. Verify the extracted archive resolves its own dependencies.

For manufacturing outputs, read [manufacturing.md](references/manufacturing.md). Resolve applicable blockers and engineering sign-offs, save/refill the final board, then export deterministic Gerbers/drills/BOM/positions/drawings as required. Inspect them in native viewers, verify registration/origins/assembly conventions and retain source/options evidence. Ordering boards requires explicit user instruction.
