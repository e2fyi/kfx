#!/usr/bin/env python
"""Script to generate json schemas."""
import kfx.lib.vis

with open("schema/kfp-ui-metadata.schema.json", "w") as fout:
    fout.write(kfx.lib.vis.KfpUiMetadata.schema_json(indent=2))
