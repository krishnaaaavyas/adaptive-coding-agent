# Two distinct discovery layers

1. **Raw audit:** later insert the exact external output under `raw/`, preserving
   bytes verbatim. It is immutable historical evidence, may contain editorial prose,
   and must never be input to Step 8K-B candidate gates or experimental models.
   Never silently edit an archived audit; corrections are separate versioned records.
2. **Normalized record:** later create a separate derived JSON artifact under
   `normalized/` conforming to `normalization_schema.json`. Only this neutral record
   may feed the later human/Codex methodology audit. It is also model-invisible.

At the initial contract stage, neither layer was populated and no discovery hashes
existed. Step 8K-A raw and normalized artifacts are now populated and provenance-hashed.
Raw and normalized artifacts are not interchangeable.
Use `normalization_procedure.md` version 1 and a separate manifest conforming to
`normalization_manifest_schema.json`.

The manifest records SHA-256 of exact raw and normalized file bytes, relative artifact
paths, schema/procedure versions, UTC creation time and draft/frozen status. Serialize
JSON as UTF-8, sorted keys, two-space indentation and one final LF. Freeze by committing
the reviewed artifact/manifest pair. Verify both hashes before using a frozen record;
any later derivation receives a new artifact and manifest referencing its raw source.
Schemas describe the contract; they do not perform archival or enforce immutability.
