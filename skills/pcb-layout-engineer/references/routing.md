# Routing and topology

## Select a backend
Use a verified native editor/API for copper edits. CLI checks and exports are separate capabilities. Read [integration.md](integration.md) for optional MCP setup. Test any new backend on a complete disposable project and verify project identity, native reads, reversible edits, undo/save/reload, nets/rules, parity and DRC. Unsupported capabilities must not silently fall back to raw file edits.

## Routing sequence and topology
Safety spacing/constrained power; hot loops; RF; clocks; fast differential; controlled impedance; timing/memory; sensitive analogue; high-current; general digital; slow control. Reserve reference planes and corridors first; document justified order changes. Never use bulk autorouting for power-stage/RF/analogue/safety routes by default. Autorouting trials retain full project rules and protect good existing copper.

Use clean 45-degree geometry unless vendor RF/curved geometry requires otherwise. Orderly bus escapes and meaningful parallelism, minimal segments, consistent width/corners, documented pad neckdowns. Remove pointless detours/stubs but retain intentional series/component topology. Do not route through isolation/antenna keep-outs. Every layer transition needs a deliberate return strategy.

## Fast interfaces
Record exact transmitter/receiver, topology, protocol speed/edge rate, required impedance/skew and authoritative spec. Confirm fabricator stackup/material/copper, width/gap, actual reference planes, vias/stubs and connector transition. Match electrical delay only where required; unrelated buses do not get decorative meanders. Tight meander coupling changes effective delay. Differential pairs are not two independently shortest paths. Check reference continuity and return via placement; ground stitching cannot substitute for a valid reference transition across incompatible power domains.

## Review
Inspect copper and filled planes at usable zoom, net by net for critical nets. Trace return paths explicitly. Compare via/length/layer-transition counts against baseline; lower via count is not universally better. Validate schematic parity, routing completion and native DRC after cleanup. Refill/save native zones before final export; CLI in-memory refill checks do not persist fills.
