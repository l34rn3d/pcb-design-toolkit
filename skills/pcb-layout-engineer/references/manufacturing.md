# Mechanical, assembly and manufacturing review

## Gate before output
Complete applicable review checklist and resolve/sign off blockers first. An incomplete board may be delivered with review artifacts, but do not issue manufacturing files as a final fabrication package merely to satisfy completion. Native clean DRC and zero opens do not establish production readiness.

Verify chosen manufacturer's current capabilities: track/space, drills/annular rings, copper-to-edge, slots/cutouts, plating, stackup/copper/material/tolerances, soldermask dams/expansion, finish, via treatment and assembly rules. Record evidence; no universal manufacturer minima. Inspect rules in project/custom-rule files against actual choices; exclusions need explicit reasons and reviewer disposition.

## Mechanical and assembly
Check outline closure/size/layers/thickness, holes/NPTH/PTH classification, screw/washer and edge spacing, enclosure mating surfaces, heights and cable/tool access. Wrong or missing 3D models remain UNKNOWN. Inspect front/back mounting orientation, connector mating-face numbering, polarity, pin-1 and exact package land pattern. Review courtyard overlap, DNP variants, heat-sensitive neighbours and accessible probe points.

Silkscreen: legible consistent orientation/size per assembler capabilities; no pad/mask/edge overlap, visible connector labels, polarity, test-point identities, name/revision without clutter. Check post-assembly visibility.

Paste/mask: verify exposed-pad segmentation, via wicking mitigation, component solderability and small passive thermal balance. Filled/capped via-in-pad is an ordered manufacturing option, not a cosmetic setting. Fiducials, tooling holes and panelization are assembler/process-dependent; do not invent mandatory counts.

## Deterministic export
Use saved/refilled final KiCad project with its libraries/rules/variables. Capture source hashes, tool version, exact options, intended layer list, units, drill origin and assembly variants in a manifest. Check installed `kicad-cli pcb export --help` and subcommand help before selecting flags. Generate Gerbers, Excellon, BOM, positions when needed, fabrication and assembly drawings as applicable. BOM/position requirements and export commands vary by version. Preserve fresh per-revision output directories; no hand editing of Gerber data. Do not install missing exporters without approval.

## Output sanity check
- Expected copper layer count/names, mask, silk, outline and applicable paste/fab/assembly files exist and contain expected geometry; nonempty alone is not sufficient.
- Native Gerber viewer inspection proves outline, holes, pads and tracks are aligned across layers. Check Excellon units, drill sizes/counts, origin, plating and slots against board coordinates.
- Correct mask/paste openings, bottom-side mirroring/assembly rotation conventions and placement units/origin. Do not mirror manufacturing files ad hoc.
- BOM quantities/reference coverage/DNP/package/MPN match actual project; position files include intended populated SMD/THT scope, side and rotations agreed with assembler.
- Drawings state revision, dimensions/tolerances, stackup, finish, drill/plating/via details and special notes where applicable.
- Export source identity matches final checked board; any edit requires renewed refill/check/export.

Report verification basis and remaining human sign-offs. Human purchasing approval is separate from file generation. Never order boards implicitly.
