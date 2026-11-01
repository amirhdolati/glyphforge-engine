# Third-party notices

## RendASCII

The code under `src/glyphforge/_vendor/rendascii/` derives from RendASCII.

Copyright 2018–2020 Garrett Russell Fairburn. Licensed under the MIT License.

The complete, original notice is included at
[`src/glyphforge/_vendor/rendascii/LICENSE.txt`](src/glyphforge/_vendor/rendascii/LICENSE.txt)
and is included in built wheels. Existing upstream file notices are retained.

Changes in this extraction include package namespace relocation, removal of the
`pkg_resources` version lookup, formatting, and small resource-loading fixes.
The public `glyphforge.mesh` facade adds validation, in-memory mesh registration,
cell conversion and deterministic worker cleanup. This backend is not presented
as an independently invented rasterizer.

## Glyph City extraction

The ray caster, procedural shading, billboard art, furnished window rendering,
ANSI encoding and terminal lifecycle were adapted from Glyph City: Afterlight.
See [architecture and provenance](docs/architecture.md) for source mapping.

New extraction code, documentation and demo geometry are covered by the repository
MIT license. The donation QR image was supplied by the project owner.
