# Private Product-Design Workspace

This directory separates private product-design work from Django runtime media.
Nothing here is approved for either public deployment, and the ignored source
trees must not be committed to Git.

## Layout

- `active/treadjoy-heritage-court-v3/` is the current editable Blender design,
  engineering-document, script, and QA evidence workspace.
- `archive/treadjoy-modular-v1/` preserves the superseded Joyline generation.
- `archive/treadjoy-modular-v2/` preserves the superseded Heritage Court V2
  generation.

`media/` remains reserved for Django uploads and development-only website media.
Moving a design generation into `archive/` records lifecycle status; it does not
make the material disposable or authorize deletion.

## Evidence And Paths

Keep generated reports, provenance records, and historical command transcripts
unchanged when they record the path used during an earlier run. Current scripts,
instructions, and pending commands must use the `design/` locations above.
Moving a generation must preserve every file, relative path, byte count, and
content hash before the old directory is considered retired.

Do not publish renders or copy them into website media without separate owner
approval, rights review, factual-copy review, metadata inspection, and the
release-content checks required by `AGENTS.md`.
