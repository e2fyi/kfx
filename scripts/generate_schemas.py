#!/usr/bin/env python
"""Script to generate json schemas."""
import kfx.vis.models

with open("schema/kfp-ui-metadata.schema.json", "w") as fout:
    fout.write(kfx.vis.models.KfpUiMetadata.schema_json(indent=2))
