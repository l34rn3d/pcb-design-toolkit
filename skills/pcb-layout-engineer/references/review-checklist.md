# Final layout review checklist

Every item needs evidence and a status, not merely a tick. PASS is automatically verified within a stated scope; REVIEW is engineering judgement (include conclusion/reviewer/evidence if done); UNKNOWN is insufficient information. Not-applicable items need a reason and must not masquerade as PASS.

## Authority/electrical correspondence
- Current project baseline, complete hierarchy, rules/net classes, layer stack/copper and mechanical constraints identified.
- Source identity/hash, tool versions and checkpoints recorded; unrelated original work preserved.
- Exact MPN/package pin numbers/functions, pad mapping, footprint dimensions, polarity/pin-1 and connector mating orientation verified against authoritative documents.
- PCB/schematic parity independently checked; no unintended connectivity/values/pin swaps. No-net pads and unused pins inspected, not hidden by zero assigned-net opens.
- Required ERC after schematic edits; otherwise disclose baseline ERC or why not run. Inspect each error, warning, excluded finding and disabled/ignored check category; record justification for disabled coverage.

## Placement/routing/power
- Coherent functional groups; connectors, protection, decoupling, crystals, switchers and termination correctly placed.
- Power widths/planes/vias/reliefs justified from load/stackup/rise/drop, bottlenecks checked; regulator feedback/hot loops and oscillator layout reviewed.
- Sensitive analogue/RF and Kelvin paths isolated from noise geographically without arbitrary ground splits.
- Fast returns continuous across planes/transitions; pair width/gap/skew/impedance assumptions tied to real protocol and fabricator stackup.
- Every intended connection complete; opens zero or explicitly incomplete with exact affected pins/nets. No unexpected orphan tracks/islands/narrow necks.
- Conventional understandable trace geometry; no pointless vias/zig-zags/tuning/stubs; necessary exceptions justified.
- Saved/refilled zones reviewed as actual copper; custom rules/net classes and differential constraints retained.

## Native checks and visual proof
- DRC on exact final board with correct project context; all warnings/exclusions reviewed. Zero errors is not enough.
- Review silkscreen/edge/courtyard/keep-out issues, drill/via dimensions, outline and mechanical constraints.
- Native 2D layout inspected: actual pads, copper, outline, references visible. Native 3D/mechanical inspection includes packages/heights/enclosure; missing model limitations stated.
- Probe/debug/connector/rework access and mounting/screw/cable clearances checked.
- Required full-review analyses accounted for: schematic/PCB/cross-domain, EMC, simulation where simulator available, thermal, existing fabrication artifacts and lifecycle where applicable. Heuristics cross-verified; skipped analyses disclosed.

## Manufacturing/report
- Applicable blockers resolved and engineering sign-offs documented before final manufacturing exports.
- Gerber/drill/layer/BOM/position/drawing consistency and viewer sanity checks completed; final source/check/export identities match.
- Report dimensions, copper-layer count, routing status/unconnected count, DRC/ERC counts and exclusions, via count, rules/impedance evidence, unresolved concerns and human checks before ordering.

## Report template
Source path/hash; KiCad/backend/version; operation scope; baseline → final change summary.

Item | PASS/REVIEW/UNKNOWN | result/count/requirement | evidence | unresolved action.

Include explicit sections: automatic checks, engineering review conclusions, unknown/blocking requirements, analyses not performed, manufacturing-output inventory if generated, and human decisions before ordering. Never describe a script exit 0 as a full-board approval.
