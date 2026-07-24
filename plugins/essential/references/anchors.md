# Workspace anchors and initiatives

Read this when a work stream is anchored by anything beyond one Git/jj
workspace, or when several streams share one initiative.

## Anchor declarations

`goal.md` carries a `## Workspace anchors` list. Each anchor declares:

- `kind:` `git | jj | media-project | asset-store | requirements-authority`
- `locator:` how to reach it (repository + revision, application + project and
  timeline ids, manifest path, authority URL)
- `revision semantics:` how an immutable revision is named — commit SHA for
  git/jj, timeline revision for a media project, content hash for a stored
  asset, version id or timestamp for a requirements authority.

The default anchor is the resolved git/jj workspace. Work anchored only in Git
declares nothing extra.

## Adapter contract

Every anchor kind must be able to answer, in its own terms, what the Git
adapter answers natively:

1. Identity — what uniquely names this workspace.
2. Current revision — what state it is at now.
3. Immutable revision — how a point-in-time is named so evidence and
   approvals can bind to it.
4. Isolation gate — the equivalent of the `.gitignore` bootstrap gate: where
   operational files may be written without polluting the record of record.
5. Receipt reachability — how a receipt names it so a takeover on another
   machine, holding a copy of the work directory, can reach the same code.

A stream whose anchor cannot answer these is indexed at handover with its code
marked non-transferable, exactly like a Git stream with no reachable revision;
its state still travels by copying the work directory.

## Initiative manifest

When one initiative spans multiple streams (product change, landing page,
launch video…), a versioned manifest at `docs/initiatives/<slug>/index.md` —
a plugin-owned durable document under the contract's `docs/<domain>/<slug>/`
clause — is the shared surface: dependencies and milestones only, never
detailed state:

- participating streams with their workspace anchors;
- shared contracts (briefs, voice, naming) by path;
- cross-stream dependency edges, each recording the revision it was last
  validated against;
- milestones with the streams they gate;
- `last_verified` / `revalidate_on` front matter per `approvals.md`.

Each stream stays authoritative in its own tree; the manifest tells a
coordinator which streams a decision's blast radius crosses. Asset-heavy
streams version an asset manifest per `templates/asset-manifest.md` — media
bytes stay outside Git, their identity and lineage do not.
