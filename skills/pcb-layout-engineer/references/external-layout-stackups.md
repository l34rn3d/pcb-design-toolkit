# External stackup handoff

Distinguish intended layer role, reference-net identity and connected plane geometry. A ground net or layer name does not prove a continuous plane. Inspect actual filled connected copper and the returned service stackup table.

[Quilter's stackup documentation](https://docs.quilter.ai/design-parameters/stackups) describes imported layer naming: intended ground layers use `ground`/`gnd`, power layers use `power`/`pwr`. Keep the actual circuit net identity rather than inventing another ground net. Verify current documentation and UI before changing a handoff; choosing a fabricator preset does not establish reference connectivity.

Where the current UI offers layer-class controls, use them for Signal/Ground/Power roles and inspect the resulting table. Do not infer editability from cell appearance. Record layer count/order, reference nets, material/copper/thickness and fabricator evidence. A change in layer count affects cost/design scope and requires a decision within the user's authorization. An unrouted input without zones must disclose missing reference-plane implementation.
