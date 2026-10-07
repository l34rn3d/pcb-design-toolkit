# External placement handoff

Confirm current service documentation before uploading. [Quilter's pre-placed-component documentation](https://docs.quilter.ai/design-parameters/pre-placed-components) describes components inside the board boundary as fixed and those outside as available for placement. Lock flags alone do not establish service placement freedom. A valid outline, footprints and matching netlist are still required; placement freedom does not resize the outline.

For automatic placement, retain every footprint/net and stage free components fully outside the outline. For partial placement, retain only requested mechanical anchors and electrically justified support arrangements inside. Record fixed/free reference lists and connector-access implications. Preserve layers, outline, libraries and rules in a complete copy.

Compare native input/output reference, pad/net and layer inventories; do not accept lost components, changed mappings or unexpectedly altered mechanics. Inspect source-derived native previews; board-cropped views may hide staged outside components. Package the matching schematic/project and local dependencies with fresh reports. Uploading project files to a service requires user authorization.
