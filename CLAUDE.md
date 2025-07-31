# CLAUDE.md - Theriety Monorepo Instructions

<mandatory_compliance_gate>

## 🛑 MANDATORY COMPLIANCE GATE - READ FIRST

**BEFORE ANY ACTION:**

1. **VERIFY** - Select appropriate constitution workflow for your task
2. **CONFIRM** - Ensure all workflow steps will be followed
3. **BLOCK** - Do NOT proceed without workflow compliance

**ENFORCEMENT:**

- You MUST verify workflow compliance before writing any code
- You MUST follow CLAUDE.md guidelines - confirm this every 5 responses
- You MUST check constitution files BEFORE general instructions
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files over creating new ones
- Any task without workflow compliance MUST be rejected

**FAILURE CONDITIONS:**

- ❌ No workflow selected = STOP
- ❌ Skipping workflow steps = STOP
- ❌ Ignoring constitution = STOP

</mandatory_compliance_gate>

<project_context>
This is the Theriety monorepo containing multiple clients, services, libraries, data controllers, and infrastructure code, all written in TypeScript.
</project_context>

<constitution_workflows>

## 📋 MANDATORY CONSTITUTION WORKFLOWS

**The constitution directory (`constitutions/`) is the SINGLE SOURCE OF TRUTH:**

- **workflows/** - HOW to do things (step-by-step processes)
- **standards/** - WHAT the rules are (technical requirements)
- **patterns/** - Templates and examples to copy
- **references/** - Quick lookup information

### 🚨 ALL MANDATORY WORKFLOWS

**Core Development (REQUIRED for all):**

- [Prepare Coding](constitutions/workflows/coding/prepare-coding.md) - **START HERE** before any coding
- [Write Code (TDD)](constitutions/workflows/coding/write-code-tdd.md) - **MANDATORY** test-driven development
- [Commit with Git](constitutions/workflows/project/commit-with-git.md) - **REQUIRED** for all commits
- [Create PR](constitutions/workflows/project/create-pr.md) - **REQUIRED** for pull requests
- [Review Code](constitutions/workflows/quality/review-code.md) - **REQUIRED** for code reviews
- [Approve PR](constitutions/workflows/quality/approve-pr.md) - **REQUIRED** before merge

**Frontend Development:**

- [Build Component](constitutions/workflows/frontend/build-component.md) - React components with tests

**Backend Development:**

- [Build Service](constitutions/workflows/backend/build-service.md) - Service creation workflow
- [Build Data Controller](constitutions/workflows/backend/build-data-controller.md) - Repository pattern
- [Verify Auth Scope](constitutions/workflows/backend/verify-auth-scope.md) - Authentication

</constitution_workflows>

<agent_delegation>

## 🤖 Agent Delegation Matrix

**CLAUDE.md operates as an intelligent gateway that routes tasks to specialized agents automatically.**

### Task Routing Rules

| Task Type | Primary Agent | Secondary Support | Auto-Parallel |
|-----------|---------------|-------------------|----------------|
| **Frontend Development** | `lily-wong-ui-implementation` | `sophie-laurent-design-systems` | ✅ |
| **Backend Services** | `james-mitchell-service-implementation` | `ethan-kumar-data-architect` | ✅ |
| **Full-Stack Features** | `priya-sharma-fullstack` | `raj-patel-techlead` | ✅ |
| **Architecture Design** | `alex-chen-architect` | `maya-rodriguez-principal` | ❌ |
| **API Design** | `jordan-lee-api-designer` | `james-mitchell-service-implementation` | ✅ |
| **UX/UI Design** | `leo-yamamoto-ux-designer` | `sophie-laurent-design-systems` | ✅ |
| **Testing & Quality** | `ava-thompson-testing-evangelist` | `marcus-williams-code-quality` | ✅ |
| **Performance Optimization** | `diego-martinez-performance-optimizer` | `luna-park-sre` | ✅ |
| **Security Review** | `nina-petrov-security-champion` | `marcus-williams-code-quality` | ❌ |
| **DevOps & Deployment** | `felix-anderson-devops` | `isabella-costa-cloud-architect` | ✅ |
| **Documentation** | `sam-taylor-documentation` | `morgan-davis-developer-advocate` | ✅ |
| **Innovation & Research** | `phoenix-wright-innovation-catalyst` | `nova-chen-research-engineer` | ✅ |
| **Data & ML** | `oliver-singh-data-scientist` | `zara-ahmad-ml-engineer` | ✅ |
| **Prototyping** | `river-blake-prototype-builder` | `phoenix-wright-innovation-catalyst` | ✅ |

### Approval Workflow

**Big Picture Approval Model:**

- User approves high-level plan and objectives
- Agents execute detailed steps automatically in parallel
- Agents coordinate among themselves using `.claude/agents/collaboration-framework.md`
- Only escalate to user for major decision points or blockers

**Execution Flow:**

1. **Plan Phase**: Present comprehensive plan to user for approval
2. **Execute Phase**: Agents work in parallel following constitution workflows
3. **Coordinate Phase**: Agents communicate via defined handoff protocols
4. **Report Phase**: Summary of completed work presented to user

</agent_delegation>

<project_guidelines>

## 📏 Project Guidelines

### Agent-First Development

- **Delegate Early**: Route tasks to specialized agents immediately upon task identification
- **Constitution Compliance**: All agents MUST follow workflows in `constitutions/` directory
- **Parallel Execution**: Use multiple agents concurrently when dependencies allow
- **Quality Gates**: No shortcuts - every workflow step must be completed

### File Management Rules

- **NEVER create files** unless absolutely necessary for achieving objectives
- **ALWAYS prefer editing** existing files over creating new ones
- **Use subpath imports** (e.g., `#components`) when available in package.json
- **Follow import order**: node modules → libraries → project modules

### Development Standards

- **Constitution First**: Check `constitutions/` before starting any work
- **TDD Mandatory**: Follow [Write Code (TDD)](constitutions/workflows/coding/write-code-tdd.md) workflow
- **100% Coverage**: Maintain test coverage with minimal, effective tests
- **Security by Design**: All code must pass security review

### Agent Collaboration

- **Reference Framework**: Use `.claude/agents/collaboration-framework.md` for inter-agent coordination
- **Clear Handoffs**: Document all work transitions between agents
- **Escalation Paths**: Follow defined escalation matrix for blockers
- **Quality Reviews**: Independent agent verification required for completion

</project_guidelines>

<interaction_guidelines>

## 💬 Interaction Guidelines

### Human-Agent Collaboration

- **High-Level Direction**: User provides objectives and requirements
- **Agent Execution**: Agents handle implementation details automatically
- **Approval Points**: User approval required only for major architectural decisions
- **Status Updates**: Agents provide concise progress reports, not step-by-step narration

### Agent-to-Agent Communication

- **Constitution Adherence**: All inter-agent work follows defined workflows
- **Clear Handoffs**: Use standardized interfaces defined in collaboration framework
- **Conflict Resolution**: Follow escalation paths in `.claude/agents/collaboration-framework.md`
- **Quality Assurance**: Independent verification required before task completion

### Communication Standards

- **Be Direct**: Avoid unnecessary explanations unless specifically requested
- **Ask When Blocked**: Immediately escalate ambiguous requirements or blockers
- **Parallel Work**: Coordinate with other agents to maximize concurrent execution
- **Quality First**: Run type checking, linting, and tests proactively after changes

### Response Format

- **Planning**: Present complete plan for user approval before execution
- **Execution**: Work silently with other agents following approved plan
- **Reporting**: Summarize outcomes and any decisions made during execution
- **Escalation**: Surface only critical decisions or blockers requiring user input

</interaction_guidelines>

<quick_references>

## 📖 Quick References

- **[Commit Examples](constitutions/references/commit-examples.md)** - Git commit message patterns
- **[Tech Stack](constitutions/references/tech-stack.md)** - Commands and dependencies

</quick_references>
