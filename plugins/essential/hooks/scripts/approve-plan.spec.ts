import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const pluginRoot = resolve(import.meta.dirname, "../..");
const script = resolve(import.meta.dirname, "approve-plan");

function runHook(input: Record<string, unknown>, harness = "codex", root?: string, automation?: string): ReturnType<typeof spawnSync> {
  const environment = { ...process.env };
  delete environment.CLAUDE_PLUGIN_ROOT;
  delete environment.PLUGIN_ROOT;
  delete environment.GROK_PLUGIN_ROOT;
  delete environment.ESSENTIAL_APPROVED_PLAN_AUTOMATION;
  if (automation !== undefined) environment.ESSENTIAL_APPROVED_PLAN_AUTOMATION = automation;
  environment[harness === "claude" ? "CLAUDE_PLUGIN_ROOT" : harness === "grok" ? "GROK_PLUGIN_ROOT" : "PLUGIN_ROOT"] = pluginRoot;
  if (root) environment.TMPDIR = root;
  const result = spawnSync("bash", [script], { env: environment, encoding: "utf8", input: JSON.stringify(input) });
  expect(result.status, result.stderr).toBe(0);
  return result;
}

function parse(result: ReturnType<typeof spawnSync>): Record<string, unknown> {
  return JSON.parse(String(result.stdout)) as Record<string, unknown>;
}

function withRoot(test: (root: string) => void): void {
  const root = mkdtempSync(resolve(tmpdir(), "approve-plan-"));
  try { test(root); } finally { rmSync(root, { recursive: true, force: true }); }
}

describe("approved plan hook delivery", () => {
  it.each(["codex", "claude"])("should inject approval context under %s", (harness) => {
    const result = parse(runHook({ hook_event_name: "UserPromptSubmit", prompt: "Implement the plan." }, harness));
    expect(result).toMatchObject({ hookSpecificOutput: { hookEventName: "UserPromptSubmit", additionalContext: expect.stringContaining("directions/approve-plan.md") } });
    expect((result.hookSpecificOutput as { additionalContext: string }).additionalContext.length).toBeGreaterThan(0);
  });

  it.each(["codex", "claude", "grok"])("should disable approval automation under %s for off and malformed values", (harness) => withRoot((root) => {
    for (const automation of ["0", "invalid", ""]) {
      const result = runHook({ hook_event_name: "UserPromptSubmit", session_id: "disabled", prompt: "Implement the plan." }, harness, root, automation);
      expect(result.stdout).toBe("");
      expect(runHook({ hook_event_name: "PreToolUse", session_id: "disabled", tool_name: "read_file" }, harness, root, automation).stdout).toBe("");
    }
  }));

  it("should discard pending Grok delivery when automation is disabled", () => withRoot((root) => {
    runHook({ hook_event_name: "UserPromptSubmit", session_id: "pending", prompt: "Implement the plan." }, "grok", root, "1");
    expect(runHook({ hook_event_name: "PreToolUse", session_id: "pending", tool_name: "read_file" }, "grok", root, "0").stdout).toBe("");
    expect(runHook({ hook_event_name: "PreToolUse", session_id: "pending", tool_name: "read_file" }, "grok", root, "1").stdout).toBe("");
  }));

  it.each(["codex", "claude"])("should explicitly enable approval automation under %s", (harness) => {
    const result = parse(runHook({ hook_event_name: "UserPromptSubmit", prompt: "Implement the plan." }, harness, undefined, "1"));
    expect(result).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("directions/approve-plan.md") } });
  });

  it("should retain verified OpenCode approval provenance", () => {
    const result = parse(runHook({ hook_event_name: "UserPromptSubmit", prompt: "Implement the plan.", approval_origin: "opencode-v1", approval_reference: "session-current:call-approved" }));
    expect(result).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("opencode-v1:UserPromptSubmit") } });
    expect(result).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("session-current:call-approved") } });
  });

  it("should ignore an unrecognized provenance override", () => {
    const result = parse(runHook({ hook_event_name: "UserPromptSubmit", prompt: "Implement the plan.", approval_origin: "unrecognized-harness" }));
    expect(result).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("codex:UserPromptSubmit") } });
  });

  it("should identify Codex approval by its session and turn rather than payload bytes", () => {
    const input = { hook_event_name: "UserPromptSubmit", prompt: "Implement the plan.", session_id: "session-current", turn_id: "turn-approved" };
    const first = parse(runHook(input));
    const repeated = parse(runHook({ ...input, incidental_metadata: "changed" }));
    const later = parse(runHook({ ...input, turn_id: "turn-later" }));
    expect(repeated).toEqual(first);
    expect(first).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("session:session-current:turn:turn-approved") } });
    expect(later).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("session:session-current:turn:turn-later") } });
    expect(later).not.toEqual(first);
  });

  it("should mark an approval without a native event identity as a fingerprint", () => {
    const result = parse(runHook({ hook_event_name: "UserPromptSubmit", prompt: "Implement the plan.", session_id: "unresolved-session", transcript_path: "/session/current-transcript.jsonl" }));
    expect(result).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("fingerprint:codex:UserPromptSubmit") } });
    expect(result).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("/session/current-transcript.jsonl") } });
  });

  it("should identify Claude approval by tool use rather than incidental result metadata", () => {
    const input = { hook_event_name: "PostToolUse", tool_name: "ExitPlanMode", tool_use_id: "tool-approved", tool_response: { isAgent: false, plan: "# Goal\nDeliver." } };
    expect(parse(runHook({ ...input, incidental_metadata: "changed" }, "claude"))).toEqual(parse(runHook(input, "claude")));
  });

  it.each([
    "yes", "Do not implement the plan.", "Explain 'Implement the plan.'", "`Implement the plan.`", "Implement the following plan:\n\n", "PLEASE IMPLEMENT THIS PLAN:\n",
  ])("should ignore non-approval submission %s", (prompt) => {
    expect(runHook({ hook_event_name: "UserPromptSubmit", prompt }).stdout).toBe("");
  });

  it.each([
    "Implement the following plan:\n\n# Goal\nDeliver.",
    "PLEASE IMPLEMENT THIS PLAN:\n# Goal\nDeliver.",
    "The user approved the plan. Implement the plan in plan.md.",
    "A previous agent produced the plan below to accomplish the user's task. Implement the plan in a fresh context. Treat the plan as the source of user intent, re-read files as needed, and carry the work through implementation and verification.\n\n# Goal\nDeliver.",
  ])("should recognize a verified implementation submission %s", (prompt) => {
    expect(parse(runHook({ hook_event_name: "UserPromptSubmit", prompt }))).toMatchObject({ hookSpecificOutput: { additionalContext: expect.stringContaining("directions/approve-plan.md") } });
  });

  it("should deliver successful Claude plan approval context", () => {
    expect(parse(runHook({ hook_event_name: "PostToolUse", tool_name: "ExitPlanMode", tool_response: { plan: "# Goal\nDeliver.", isAgent: false } }, "claude"))).toMatchObject({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: expect.stringContaining("directions/approve-plan.md") } });
  });

  it("should ignore Claude teammate plans still awaiting leader approval", () => {
    expect(runHook({ hook_event_name: "PostToolUse", tool_name: "ExitPlanMode", tool_response: { plan: "# Goal\nDeliver.", isAgent: true, awaitingLeaderApproval: true, requestId: "pending" } }, "claude").stdout).toBe("");
  });

  it("should never treat Grok PlanReady as user approval", () => {
    expect(runHook({ hookEventName: "PostToolUse", toolName: "exit_plan_mode", toolResult: { plan: "# Goal\nDeliver." } }, "grok").stdout).toBe("");
  });

  it("should deliver a pending Grok approval exactly once to its session", () => withRoot((root) => {
    expect(runHook({ hookEventName: "UserPromptSubmit", sessionId: "approved", prompt: "Implement the plan." }, "grok", root).stdout).toBe("");
    expect(runHook({ hookEventName: "PreToolUse", sessionId: "other", toolName: "read_file" }, "grok", root).stdout).toBe("");
    expect(parse(runHook({ hookEventName: "PreToolUse", sessionId: "approved", toolName: "read_file" }, "grok", root))).toMatchObject({ decision: "deny", reason: expect.any(String) });
    expect(runHook({ hookEventName: "PreToolUse", sessionId: "approved", toolName: "read_file" }, "grok", root).stdout).toBe("");
  }));

  it("should clear Grok pending approval when a new ordinary prompt arrives", () => withRoot((root) => {
    runHook({ hookEventName: "UserPromptSubmit", sessionId: "approved", prompt: "Implement the plan." }, "grok", root);
    runHook({ hookEventName: "UserPromptSubmit", sessionId: "approved", prompt: "Explain the alternatives first." }, "grok", root);
    expect(runHook({ hookEventName: "PreToolUse", sessionId: "approved", toolName: "read_file" }, "grok", root).stdout).toBe("");
  }));

  it("should provide the Grok Stop fallback before any tool call", () => withRoot((root) => {
    runHook({ hookEventName: "UserPromptSubmit", sessionId: "approved", prompt: "Implement the plan." }, "grok", root);
    expect(parse(runHook({ hookEventName: "Stop", sessionId: "approved" }, "grok", root))).toMatchObject({ decision: "block", reason: expect.any(String) });
    expect(runHook({ hookEventName: "Stop", sessionId: "approved" }, "grok", root).stdout).toBe("");
  }));
});
