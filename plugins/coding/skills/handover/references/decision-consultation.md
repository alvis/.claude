# Consult the user on key decisions

Use this reference when the handover workflow consults on open decisions. Before documenting the handover, identify and consult the user on every material decision requiring input. Low-impact reversible assumptions may be recorded with evidence and a recheck trigger; architectural, technical, product, security, data, destructive, or strategic choices are never decided unilaterally.

**Actions**:

1. **Identify Decision Points**:
   - Review all gathered context from Steps 0-4
   - Extract any technical choices mentioned in:
     - TODO comments requiring decisions (e.g., "TODO: decide between Redis vs Memcached")
     - Architecture patterns pending selection
     - Library/framework choices not yet finalized
     - Implementation approaches with multiple valid options
     - Feature scope or priority decisions
     - Configuration or deployment strategy choices
   - Identify assumptions, their evidence, impact, reversibility, and recheck
     triggers; promote material assumptions to decisions

2. **Categorize Decisions**:
   - **Architectural Decisions**: System design patterns, component structure, data flow
   - **Technology Choices**: Libraries, frameworks, tools, services
   - **Implementation Approaches**: Algorithm choices, optimization strategies, design patterns
   - **Scope Decisions**: Feature prioritization, MVP boundaries, phasing
   - **Configuration**: Environment setup, deployment strategies, scaling approaches

3. **Consult User with AskUserQuestion**:
   - For EACH identified decision:
     - Present the decision clearly with context
     - Provide 3-5 viable options with brief pros/cons
     - ALWAYS include these TWO special options:
       - **"Defer decision"** - Document under Pending Decisions with an owner
         and decision deadline
       - **"Perform research"** - Launch deep research subagent, save results
     - Use AskUserQuestion tool with format:

       ```
       Decision: [Clear statement of what needs to be decided]
       Context: [Why this decision matters, from project analysis]

       Options:
       1. [Option 1] - [Brief rationale and trade-offs]
       2. [Option 2] - [Brief rationale and trade-offs]
       3. [Option 3] - [Brief rationale and trade-offs]
       4. Perform research - Launch deep research on this topic
       5. Defer decision - Document as open question in handover
       ```

   - Record user's choice for each decision
   - Handle user selections appropriately

4. **Process Decision Outcomes**:

   **For finalized decisions:**
   - Store decision with rationale for CONTEXT.md "Key Decisions & Patterns" section
   - Note technical choices for CONTEXT.md "Dependencies & Configuration" section
   - Prepare implementation tasks for PLAN.md

   **For "Perform research" selections:**
   - Route the bounded investigation to the best available research specialist
   - Provide comprehensive research prompt including:
     - Decision context and importance
     - Key questions to answer
     - Trade-offs to explore
     - Best practices to identify
   - Save research output as `research-[topic-slug].md` in working directory
   - Add to PLAN.md: "📊 **RESEARCH AVAILABLE**: Review research-[topic].md and decide on [topic]"
   - Reference the research file in NOTES.md under "Pending Decisions"

   **For "Defer decision" selections:**
   - Mark for inclusion in NOTES.md "Pending Decisions" with owner and deadline
   - Prepare for PLAN.md: "⚠️ **DECISION REQUIRED**: [Topic] - See NOTES.md Pending Decisions"
   - Identify tasks blocked by this decision

5. **Handle Multiple Decisions**:
   - If 5+ decisions identified, prioritize:
     - Critical architectural decisions first
     - Technology choices affecting multiple components
     - Decisions blocking immediate next steps
     - Lower priority decisions can be batched or deferred
   - Group related decisions together when presenting to user
   - Process decisions sequentially to allow informed choices

**Example Decision Consultation**:

```
Decision: Caching Strategy for User Sessions
Context: Analysis shows 3 TODO comments about session management.
System has high read load (from git commit messages mentioning performance).

Options:
1. Redis - Industry standard, persistent, supports clustering (requires Redis setup)
2. Memcached - Simpler, faster for pure caching (loses data on restart)
3. In-memory with Node - No external deps (doesn't scale across instances)
4. Perform research - Launch deep research on caching strategies
5. Defer decision - Document as open question, use simple approach for now

[If user selects option 1: Redis]
→ Store in decisions: "Use Redis for session caching - provides persistence and clustering"
→ Prepare for CONTEXT.md: "Key Decisions & Patterns" and "Dependencies & Configuration"
→ Prepare for PLAN.md: "Set up Redis for session caching"

[If user selects "Perform research"]
→ Launch research agent on "session caching strategies for high-load Node.js applications"
→ Save results to research-session-caching.md
→ Prepare for PLAN.md: "📊 Review research-session-caching.md and decide on caching strategy"
→ Prepare for NOTES.md: Link to research file in "Pending Decisions"

[If user selects "Defer decision"]
→ Prepare for NOTES.md: "Pending Decisions - Session Caching Strategy: Redis vs Memcached vs in-memory"
→ Prepare for PLAN.md: "⚠️ DECISION REQUIRED: Session caching strategy - See NOTES.md"
→ Identify blocked tasks: "Implement session persistence - ⏸️ Blocked by caching decision"
```

**Important Notes**:

- NEVER skip this step even if "decisions seem obvious"
- ALWAYS provide both "Perform research" and "Defer decision" options
- If user is unavailable/non-responsive, treat ALL decisions as "Deferred"
- Prefer asking 3-4 focused questions over making assumptions
- Document both the decision AND the alternatives considered
- For research requests, ensure comprehensive investigation and save results
