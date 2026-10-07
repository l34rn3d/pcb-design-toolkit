# Power, return paths and thermal engineering

## Required evidence
For each power path record source/load, continuous/peak/inrush/fault current, duty cycle, copper thickness, external/internal layer, length/width, allowable temperature rise/voltage drop and local thermal environment. Identify connector/contact/pad/via/fuse/shunt bottlenecks. UNKNOWN current or stackup prevents a justified final conductor dimension.

Use a documented IPC-2152/vendor method or validated solver for thermal sizing; record assumptions and limits. IPC-2221 formulas are preliminary estimates, not universal proof. Compute resistance/drop/loss with tools using documented copper dimensions/resistivity/temperature assumptions. Evaluate neckdowns and return conductors as well as main tracks. Via current/thermal sharing depends on plated barrel geometry and placement; do not divide load by an invented amps-per-via rule. Confirm plating specifications with fabricator.

## Switching supplies
Read exact regulator datasheet/reference layout. Identify topology-specific hot loops and switching nodes; follow critical capacitor, switch/diode, inductor, bootstrap, feedback and exposed-pad placements. Keep switch-node copper only as large as electrically/thermally justified. Route feedback from the prescribed quiet sense point, away from switch-node capacitance/inductor fields; keep its return clean. Do not change compensation, filtering or topology merely to ease layout.

## Planes and returns
Establish a continuous reference strategy before routing. Do not split AGND/DGND based on names; follow explicit circuit/vendor needs and separate noisy/sensitive current geography. Inspect actual filled copper, not zone boundary artwork. Avoid islands, narrow necks and reference voids under fast signals; verify plane connections/priority/clearances after refill. Stitch only for stated electrical purpose and never across a safety barrier. Evaluate reference continuity at every fast transition; a random GND via is not always an adequate return.

Verify relief-spoke width/count and connection type against actual current and assembly solderability. Direct plane connections may improve current flow but complicate hand soldering; record trade-off. Assess decoupling impedance from the full loop and supported component data, not a generic distance threshold alone.

## Thermal and safety
Estimate dissipation/ambient and review package/vendor thermal guidance. Datasheet theta-JA is board/test-context dependent; do not treat it as a guaranteed result on this layout. Justify thermal via array, copper spread and sinks; coordinate exposed-pad paste, via-in-pad filling/capping and solder-wicking controls with assembler/fabricator. Avoid random via fields or excessive paste that floats a package.

Determine applicable safety standard, working voltage/transients, insulation class, pollution degree, material group/altitude, required creepage/clearance and slots/keep-outs. Do not reuse signal clearances as safety distances. Track width cannot cure an unsafe connector spacing. Missing safety evidence blocks completion of affected areas.

## Evidence table
Path/block | verified requirements/source | calculated dimensions/loss/rise | actual geometry | return/thermal review | PASS/REVIEW/UNKNOWN | unresolved human action.
