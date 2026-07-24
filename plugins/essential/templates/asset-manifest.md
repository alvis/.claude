# Asset manifest template

Version this manifest as text; keep the media bytes outside Git. A filesystem
path is not identity — every asset and render is named by a stable id and an
immutable content reference, so "reproduce v12" is an operation, not
archaeology. See `references/anchors.md` for anchor kinds and
`references/checkpoints.md` for approval binding.

```yaml
assets:
  - id: <stable-kebab-id>            # never renamed or reused
    kind: footage|audio|image|font|lut|template|subtitle|other
    uri: <asset-store locator>
    sha256: <content hash>
    provenance:                      # inputs this asset was derived from
      - <input-id>@<revision|hash>   # omit for captured originals
    rights:
      owner: <holder>
      consent_ref: <ref|null>
      license_ref: <ref|null>
      expires: <date|null>

renders:
  - id: <deliverable-id>-v<n>        # a new revision is a new entry
    timeline: <project/timeline id> @ <timeline revision>
    inputs_manifest_sha256: <hash of the assets section it was built from>
    settings: <render preset id + fonts/luts/plugins by id>
    output_sha256: <hash>
    approvals:
      - reviewer: <capability_id|user>
        scope: <what was approved, incl. timecode range when partial>
        at: <ISO-8601>
        ref: <review/checkpoint ref>
    delivered_to: <destination|null>
```

An approval binds to exactly one render id and revision; it never carries to
the next render. When a decision invalidates a render, mark it
`validity: stale (<decision-id>)` in place — the entry itself is history and
stays.
