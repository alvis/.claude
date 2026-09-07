import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

interface Surface {
  state: string;
  headRefOid: string;
  baseRefName: string;
  baseRefOid: string;
  isDraft: boolean;
}
interface RunOptions {
  surface?: Partial<Surface>;
  afterReady?: Partial<Surface>;
  verdict?: string;
  reviewedHead?: string;
  reviewedBase?: string;
  isMissing?: boolean;
  metadata?: string;
}
const headOid = "1".repeat(40);
const baseOid = "2".repeat(40);
const surface: Surface = {
  state: "OPEN",
  headRefOid: headOid,
  baseRefName: "master",
  baseRefOid: baseOid,
  isDraft: true,
};
const direction = readFileSync(
  join(import.meta.dirname, "../directions/review-loop.md"),
  "utf8",
);
const blocks = Array.from(
  direction.matchAll(/```bash\n([\s\S]*?)```/g),
  (match) => match[1]!,
);

describe("PR review lifecycle commands", () => {
  it.each([
    { isMissing: true },
    { metadata: "null" },
    { metadata: "{}" },
    { metadata: JSON.stringify({ ...surface, isDraft: "true" }) },
    { surface: { isDraft: false } },
    { surface: { headRefOid: "3".repeat(40) } },
    { surface: { baseRefOid: "3".repeat(40) } },
    { surface: { baseRefName: "other" } },
    { surface: { state: "CLOSED" } },
  ])(
    "should refuse review dispatch for an unavailable or unpinned draft %j",
    (options) => {
      expect(runBlock("dispatch", options).status).not.toBe(0);
    },
  );
  it("should admit a published draft matching the expected revision", () => {
    expect(runBlock("dispatch").status).toBe(0);
  });
  it.each([
    { verdict: "COMMENT" },
    { isMissing: true },
    { metadata: "null" },
    { metadata: "{}" },
    { metadata: JSON.stringify({ ...surface, isDraft: "true" }) },
    { reviewedHead: "3".repeat(40) },
    { reviewedBase: "3".repeat(40) },
    { surface: { headRefOid: "3".repeat(40) } },
    { surface: { baseRefOid: "3".repeat(40) } },
    { surface: { baseRefName: "other" } },
    { surface: { state: "CLOSED" } },
  ])(
    "should preserve draft status when approval is absent or stale %j",
    (options) => {
      const result = runBlock("ready", options);
      expect(result.status).not.toBe(0);
      expect(result.surface).toEqual(
        options.metadata === undefined
          ? { ...surface, ...options.surface }
          : JSON.parse(options.metadata),
      );
    },
  );
  it("should promote a substantively approved pinned draft", () => {
    const result = runBlock("ready");
    expect(result).toMatchObject({
      status: 0,
      surface: { ...surface, isDraft: false },
    });
  });
  it("should accept an already ready approved surface", () => {
    expect(runBlock("ready", { surface: { isDraft: false } }).status).toBe(0);
  });
  it.each([
    { isDraft: true },
    { baseRefName: "other" },
    { state: "CLOSED" },
    { headRefOid: "3".repeat(40) },
    { baseRefOid: "3".repeat(40) },
  ])("should reject failed readiness readback %j", (afterReady) => {
    expect(runBlock("ready", { afterReady }).status).not.toBe(0);
  });
});

function runBlock(
  phase: "dispatch" | "ready",
  options: RunOptions = {},
): { status: number | null; surface: Surface } {
  const root = mkdtempSync(join(tmpdir(), "pr-review-lifecycle-"));
  try {
    const metadata = join(root, "surface.json");
    writeFileSync(
      metadata,
      options.metadata ?? JSON.stringify({ ...surface, ...options.surface }),
    );
    writeFileSync(
      join(root, "after.json"),
      JSON.stringify({ ...surface, isDraft: false, ...options.afterReady }),
    );
    writeFileSync(
      join(root, "gh"),
      `#!/bin/bash
set -eu
case "$1 $2" in
  "pr view") [ "$IS_MISSING" = false ] || exit 1; cat "$METADATA" ;;
  "pr ready") cp "$AFTER_READY" "$METADATA" ;;
  *) exit 2 ;;
esac
`,
      { mode: 0o755 },
    );
    const completed = spawnSync(
      "bash",
      ["-eu", "-c", phase === "dispatch" ? blocks[0]! : blocks.at(-1)!],
      {
        encoding: "utf8",
        env: {
          ...process.env,
          PATH: `${root}:${process.env.PATH}`,
          METADATA: metadata,
          AFTER_READY: join(root, "after.json"),
          IS_MISSING: String(options.isMissing ?? false),
          PR_URL: "https://github.com/example/repo/pull/1",
          HOST: "github.com",
          OWNER: "example",
          REPO: "repo",
          EXPECTED_HEAD_OID: headOid,
          EXPECTED_BASE_OID: baseOid,
          EXPECTED_BASE_REF: "master",
          REVIEWED_HEAD_OID: options.reviewedHead ?? headOid,
          REVIEWED_BASE_OID: options.reviewedBase ?? baseOid,
          REVIEWED_BASE_REF: "master",
          SUBSTANTIVE_VERDICT: options.verdict ?? "APPROVE",
        },
      },
    );
    return {
      status: completed.status,
      surface: JSON.parse(readFileSync(metadata, "utf8")),
    };
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}
