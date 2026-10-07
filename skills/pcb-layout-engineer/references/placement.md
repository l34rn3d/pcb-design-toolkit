# Placement engineering

## Inspection and plan
Establish current project authority, schematic hierarchy/netlist, board rules, outline, holes and enclosure. Read exact MPN/package drawings, vendor recommended layouts and mechanical connector documentation. Record fixed coordinates, orientations and keep-outs; do not move locked work without approval. Grid size follows pad pitch/mechanics, not a universal value.

Build a functional-group map and a placement table: references, role, constraints, anchor IC/pins, power domain, noise sensitivity, thermal/mechanical needs, and evidence. Start with outline/mounts/connectors, then power/protection, major ICs and support parts. Decide layer/reference and routing corridors early.

## Critical placements
- Protection: shortest sensible entry-to-protection-to-protected-device path; discharge return must not traverse sensitive ground regions. Verify protector ratings/topology from design authority.
- Decoupling: locate for the actual supply/ground pins, short complete current loop and suitable reference connection; geometric centre-to-centre distance alone is insufficient. Keep power pin path from bypass pad direct; evaluate inductance of vias and shared return segments. Do not invent a capacitor count/value.
- Switchers: identify topology-specific high-di/dt loops from vendor documentation, not the visually largest power trace. Group required input/output caps, switches/diodes and inductor accordingly. Respect bootstrap, feedback, exposed-pad and keep-out instructions.
- Crystals: compact oscillator pins/crystal/load network, controlled ground return and vendor keep-outs; avoid passing unrelated signals beneath the sensitive area.
- Analogue: order by signal flow, protect high-impedance nodes and references from coupling, separate physical noise sources without forcing arbitrary ground splits. Kelvin sense paths must use actual sense connection points.
- Dense ICs: deliberately arrange support components by pin/function, reserve fanout and escape corridors. Do not scatter them merely to reduce ratsnest length.
- Termination: source/load position determined by topology and interface requirements.

## Human readability and access
Align groups and repeated channels; consistent orientations where electrically/mechanically sensible. Connector orientation and cable approach override appearance. Check probe tip/clip space, test-point ground companions where useful, programmer access, rework tools, screw heads/washers and heatsink access. Labels remain visible after connectors are fitted. Thermal neighbours must respect ambient and component ratings.

## Placement acceptance
Inspect actual native 2D copper/pad view and 3D/mechanical view. Confirm clearances/courtyards/height models, no back-to-front orientation errors, and low critical-loop inductance. Record evidence per block and checkpoint before routing. If fanout forces zig-zags, unnecessary vias or plane cuts, revisit placement rather than concealing the cause.
