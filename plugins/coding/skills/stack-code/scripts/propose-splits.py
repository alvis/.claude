#!/usr/bin/env python3
"""Cluster `jj diff` paths into PR-shaped slices for stack-code's split-mode.

Emits a proposal JSON: {slug, base, prs:[{n, scope, files, loc, bookmark, summary}]}
plus a human-readable summary table on stderr.

The PR-type taxonomy was removed; bookmark scopes derive from the cluster's
path prefix instead. Reviewers handle zone enforcement via `GIT-PR-SIZE-01..04`,
not this script.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lib import (
    bookmark_name,
    cluster_by_path,
    derive_scope_from_paths,
    emit_json,
    jj,
    jj_diff_files,
    run,
    split_test_paths,
)


def file_loc(path: str, *, dry_run: bool) -> int:
    """Approx LOC churn for one file, using `jj diff --git -- <path>` line count."""
    res = jj("diff", "--git", "--", path, dry_run=dry_run)
    out = res.stdout
    if not out:
        out = run(["git", "diff", "HEAD", "--", path], dry_run=dry_run).stdout
    n = 0
    for line in out.splitlines():
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            n += 1
    return n


def order_clusters(clusters: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    """Order clusters lexicographically by path prefix.

    Without the type taxonomy there is no canonical ordering signal here;
    reviewers re-order in the proposal JSON if needed.
    """
    return sorted(clusters.items(), key=lambda kv: kv[0])


def render_table(prs: list[dict[str, object]]) -> str:
    rows = ["#  SCOPE                FILES  LOC   BOOKMARK"]
    for pr in prs:
        rows.append(
            f"{pr['n']:<2} {pr['scope']:<20} "
            f"{len(pr['files']):<6} {pr['loc']:<5} {pr['bookmark']}"  # type: ignore[arg-type]
        )
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="propose split plan for chunky working copy")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--depth", type=int, default=2, help="path-prefix depth for clustering")
    ap.add_argument("--base", default="main@origin")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    paths = jj_diff_files(dry_run=args.dry_run)
    if not paths:
        print("no working-copy changes to split", file=sys.stderr)
        emit_json({"slug": args.slug, "base": args.base, "prs": []})
        return 0

    clusters = cluster_by_path(paths, depth=args.depth)
    prs: list[dict[str, object]] = []
    for n, (key, group) in enumerate(order_clusters(clusters), start=1):
        impl, tests = split_test_paths(group)
        files = impl + tests
        scope = derive_scope_from_paths(files)
        loc = sum(file_loc(p, dry_run=args.dry_run) for p in files)
        prs.append(
            {
                "n": n,
                "scope": scope,
                "files": files,
                "loc": loc,
                "bookmark": bookmark_name(args.slug, n, scope),
                "summary": f"changes under {key}",
            }
        )

    print(render_table(prs), file=sys.stderr)
    emit_json({"slug": args.slug, "base": args.base, "prs": prs})
    return 0


if __name__ == "__main__":
    sys.exit(main())
