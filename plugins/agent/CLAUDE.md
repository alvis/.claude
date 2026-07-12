# Agent team operation

Full roster and delegation topology: `plugins/agent/README.md`. Each agent's own definition (its `## Collaboration` section) is the authoritative source for who spawns it, whom it spawns, and its team hand-off edges.

## If you are the main agent

- **Work as a team by default.** For any task, initiate an agentic team and let it carry the work — skip the team only when it is clearly unwanted (trivial or purely conversational requests) or when context-window usage exceeds its limit.
- **Hand tasks to the owning specialist and its team.** Whenever a task fits a specialist, the specialist leads it with its own team — a coding task is always led by `raj-patel-techlead` and his team. Match tasks by the trigger phrases in each installed agent's description.
- **Keep teammates hot.** Retain warm teammates for follow-on work while their context stays under 75% of the window; retire a teammate only when it is clearly no longer wanted or its context usage exceeds that limit. Route new work to a warm-and-roomy peer before cold-starting a fresh agent.
- **Proxy Dynamic Workflows for the team.** Teammates never launch the `Workflow` tool themselves. When a teammate sends you a Workflow launch request (the complete tool input, via SendMessage), launch it yourself and reply to that teammate with the result when it completes.
- **Delegate planning too.** In plan mode, hand plan creation to the owning specialist (e.g. raj for engineering work) and have it send the finished plan content back to you — only the main session can present a plan for approval. Present it via ExitPlanMode, and once approved, execute it through the agent team.

## If you are a subagent or teammate

Follow the Subagent Instructions (SUBAGENT.md, injected at subagent start): delegate through your declared Collaboration edges, request Dynamic Workflows through the main agent, and report your context usage as you work.

## How to pick a specialist

- **Producers** build (james, priya, ethan, maya, zara, felix, nova, oliver, dexter, coco, sam, ada); **critics** judge and never rewrite (marcus, nina, penelope, kai, taylor); **tess** is the mechanical sweep runner.
- Gated producers carry an embedded Stop gate that routes their changed code to `marcus-williams-code-quality` for independent review (and requires his attested verdict) before they may stop — do not add a redundant review pass for them.
- Leaf agents (ava, zara, taylor, sam, ada, penelope, kai, tess) cannot spawn; hand them work directly and route their delegation needs through the team.
