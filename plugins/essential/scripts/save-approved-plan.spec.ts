import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

interface Sandbox {
  readonly root: string;
  readonly work: string;
  readonly input: string;
  readonly token: string;
}

const saver = resolve(import.meta.dirname, "save-approved-plan");
const lease = resolve(import.meta.dirname, "state-lease");
const originalPlan = "# Approved plan\n\nDeliver the requested hook.\n";

function withSandbox(test: (sandbox: Sandbox) => void): void {
  const root = realpathSync(mkdtempSync(resolve(tmpdir(), "save-approved-plan-")));
  try {
    expect(spawnSync("git", ["init", "--quiet", root]).status).toBe(0);
    writeFileSync(resolve(root, ".gitignore"), ".state/\n");
    const work = resolve(root, ".state/works/approved-hook");
    mkdirSync(work, { recursive: true });
    writeFileSync(resolve(work, "goal.md"), "# Approved hook\n");
    writeFileSync(resolve(work, "state.md"), "Plan source: state.md\nState revision: 1\n");
    const input = resolve(root, "input.md");
    writeFileSync(input, originalPlan);
    const acquired = spawnSync("bash", [lease, "acquire", "--work-dir", work, "--capability", "pm", "--session", "approval-test"], { encoding: "utf8" });
    expect(acquired.status, acquired.stderr).toBe(0);
    const token = (JSON.parse(acquired.stdout) as { token: string }).token;
    test({ root, work, input, token });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function save(sandbox: Sandbox, overrides: { readonly token?: string; readonly source?: string; readonly cwd?: string } = {}): ReturnType<typeof spawnSync> {
  const result = spawnSync(saver, ["--work-id", "approved-hook", "--token", overrides.token ?? sandbox.token, "--plan-file", sandbox.input, "--source", overrides.source ?? "codex:turn-approved"], { cwd: overrides.cwd ?? sandbox.root, encoding: "utf8" });
  expect(result.error).toBeUndefined();
  return result;
}

function output(result: ReturnType<typeof spawnSync>): Record<string, unknown> {
  expect(result.status, `${result.stderr}\n${result.error ?? ""}`).toBe(0);
  return JSON.parse(String(result.stdout)) as Record<string, unknown>;
}

function expectRefused(result: ReturnType<typeof spawnSync>, reason: RegExp): void {
  expect(result.status).not.toBe(0);
  expect(JSON.parse(String(result.stdout))).toEqual({ status: "error", error: expect.stringMatching(reason) });
}

// subprocess integration cases reached 12.63s on macOS CI; 30s allows over 2x headroom
describe("approved plan persistence", { timeout: 30_000 }, () => {
  it("should save exact bytes with an immutable approval snapshot", () => withSandbox((sandbox) => {
    const result = output(save(sandbox));
    const sha256 = createHash("sha256").update(originalPlan).digest("hex");
    expect(result).toMatchObject({ status: "saved", sha256, plan_path: resolve(sandbox.work, "plan.md") });
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe(originalPlan);
    expect(readFileSync(resolve(sandbox.work, "artifacts/plan-approvals", `${sha256}.txt`), "utf8")).toBe(originalPlan);
    expect(JSON.parse(readFileSync(resolve(sandbox.work, "artifacts/plan-approvals", `${sha256}.json`), "utf8"))).toMatchObject({ sha256 });
  }));

  it("should leave duplicate approvals and their evidence untouched", () => withSandbox((sandbox) => {
    output(save(sandbox));
    const path = resolve(sandbox.work, "plan.md");
    const before = statSync(path).mtimeMs;
    expect(output(save(sandbox))).toMatchObject({ status: "unchanged", generated_files: [] });
    expect(statSync(path).mtimeMs).toBe(before);
  }));

  it("should retain prior approved bytes when replacing the plan", () => withSandbox((sandbox) => {
    const first = output(save(sandbox));
    writeFileSync(sandbox.input, "# Revised plan\nDifferent delivery.\n");
    output(save(sandbox, { source: "codex:turn-revised" }));
    expect(readFileSync(resolve(sandbox.work, "artifacts/plan-approvals", `${first.sha256}.txt`), "utf8")).toBe(originalPlan);
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe("# Revised plan\nDifferent delivery.\n");
  }));

  it("should reject a foreign lease without persisting a plan", () => withSandbox((sandbox) => {
    expectRefused(save(sandbox, { token: "foreign" }), /lease/i);
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));

  it("should reject an expired owned lease", () => withSandbox((sandbox) => {
    const path = resolve(sandbox.work, "lease.json");
    const record = JSON.parse(readFileSync(path, "utf8"));
    writeFileSync(path, JSON.stringify({ ...record, expires_at_epoch: 0 }));
    expectRefused(save(sandbox), /lease/i);
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));

  it("should require the centralized state ignore gate", () => withSandbox((sandbox) => {
    writeFileSync(resolve(sandbox.root, ".gitignore"), "");
    expectRefused(save(sandbox), /workspace|ignored/i);
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));

  it("should reject an empty approval source", () => withSandbox((sandbox) => {
    expectRefused(save(sandbox, { source: "" }), /source/i);
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));

  it("should refuse conflicting immutable evidence", () => withSandbox((sandbox) => {
    const sha256 = createHash("sha256").update(originalPlan).digest("hex");
    const directory = resolve(sandbox.work, "artifacts/plan-approvals");
    mkdirSync(directory, { recursive: true });
    const snapshot = resolve(directory, `${sha256}.txt`);
    writeFileSync(snapshot, "conflicting bytes");
    expectRefused(save(sandbox), /snapshot.*conflicts/i);
    expect(readFileSync(snapshot, "utf8")).toBe("conflicting bytes");
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));

  it("should recover an interrupted receipt before returning unchanged", () => withSandbox((sandbox) => {
    const first = output(save(sandbox));
    const receipt = resolve(sandbox.work, "artifacts/plan-approvals", `${first.sha256}.json`);
    rmSync(receipt);
    expect(output(save(sandbox)).generated_files).toContain(receipt);
    expect(JSON.parse(readFileSync(receipt, "utf8"))).toMatchObject({ sha256: first.sha256 });
  }));

  it("should persist to the default tree when invoked from a linked worktree", () => withSandbox((sandbox) => {
    const git = (...args: string[]): void => {
      const result = spawnSync("git", args, { cwd: sandbox.root, encoding: "utf8" });
      expect(result.status, result.stderr).toBe(0);
    };
    git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-m", "test: fixture");
    const linked = resolve(sandbox.root, "linked");
    git("worktree", "add", "--detach", linked, "HEAD");
    const result = output(save(sandbox, { cwd: linked }));
    expect(result.plan_path).toBe(resolve(sandbox.work, "plan.md"));
    expect(existsSync(resolve(linked, ".state"))).toBe(false);
  }));

  it("should reject a superseded approval replay but accept fresh reapproval", () => withSandbox((sandbox) => {
    output(save(sandbox, { source: "event-A" }));
    const revised = "# Plan B\nDeliver B.\n";
    writeFileSync(sandbox.input, revised);
    output(save(sandbox, { source: "event-B" }));
    writeFileSync(sandbox.input, originalPlan);
    expectRefused(save(sandbox, { source: "event-A" }), /stale approval event/);
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe(revised);
    expect(output(save(sandbox, { source: "event-C" })).status).toBe("saved");
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe(originalPlan);
  }));

  it("should refuse changed bytes under the same approval identity", () => withSandbox((sandbox) => {
    output(save(sandbox));
    writeFileSync(sandbox.input, "# Changed without new approval\n");
    expectRefused(save(sandbox), /approval event conflicts/);
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe(originalPlan);
  }));

  it("should resolve an interrupted publication before accepting a newer event", () => withSandbox((sandbox) => {
    const source = "codex:turn-approved";
    output(save(sandbox));
    const eventId = createHash("sha256").update(source).digest("hex");
    rmSync(resolve(sandbox.work, "artifacts/plan-approvals/events", `${eventId}.published.json`));
    writeFileSync(sandbox.input, "# Newer plan\n");
    expectRefused(save(sandbox, { source: "event-newer" }), /pending approval publication/);
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe(originalPlan);
    writeFileSync(sandbox.input, originalPlan);
    expect(output(save(sandbox)).status).toBe("saved");
    expect(output(save(sandbox)).status).toBe("unchanged");
  }));

  it("should refuse a gap in publication history without replacing the plan", () => withSandbox((sandbox) => {
    output(save(sandbox));
    const eventId = createHash("sha256").update("codex:turn-approved").digest("hex");
    const directory = resolve(sandbox.work, "artifacts/plan-approvals/events");
    for (const suffix of [".json", ".published.json"]) {
      const path = resolve(directory, `${eventId}${suffix}`);
      const receipt = JSON.parse(readFileSync(path, "utf8"));
      writeFileSync(path, JSON.stringify({ ...receipt, revision: 3 }));
    }
    writeFileSync(sandbox.input, "# Plan after missing event\n");
    expectRefused(save(sandbox, { source: "event-after-gap" }), /revision history.*incomplete/);
    expect(readFileSync(resolve(sandbox.work, "plan.md"), "utf8")).toBe(originalPlan);
  }));

  it("should refuse content fingerprints as approval event identities", () => withSandbox((sandbox) => {
    expectRefused(save(sandbox, { source: "fingerprint:codex:UserPromptSubmit:content-hash" }), /fingerprint|event identity/);
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));

  it.each([Buffer.from(""), Buffer.from([0xff]), Buffer.alloc(16_385, "x")])("should reject invalid plan bytes without writes", (bytes) => withSandbox((sandbox) => {
    writeFileSync(sandbox.input, bytes);
    expectRefused(save(sandbox), bytes.length > 16_384 ? /16384-byte/ : /nonempty UTF-8/);
    expect(existsSync(resolve(sandbox.work, "plan.md"))).toBe(false);
  }));
});
