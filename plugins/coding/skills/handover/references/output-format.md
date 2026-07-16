# Step 7: Output Format

Use this format for the final summary after handover documents are generated/updated.

```
[✅] Handover: $ARGUMENTS

## Summary
- Context file: [path to CONTEXT.md]
- Notes file: [path to NOTES.md]
- Plan file: [path to PLAN.md]
- Files classified: [count]
- Completed: [count] | In Progress: [count] | Planned: [count]
- Implementation notes: [X issues resolved, Y workarounds, Z tips]
- Plan tasks: [count] across [phases] phases
- Recent commits analyzed: [count]
- Todos incorporated: [count from TodoRead] ([completed]/[in_progress]/[pending])
- **Decisions consulted: [count identified] ([finalized]/[deferred]/[researched])**
- **Plan updates: [count decision-driven tasks added], [count blocked tasks identified]**
- **Research files generated: [count] - [list of research-[topic].md files]**

## Document Sections

### CONTEXT.md
- Background & Context: ✓/X
- Goals & Objectives: ✓/X
- Reference Documents: ✓/X
- Current State: ✓/X
- File Status: ✓/X
- Recent Changes: ✓/X
- Key Decisions: ✓/X
- Accepted Assumptions: ✓/X
- Next Steps: ✓/X

### NOTES.md
- Implementation Issues: ✓/X
- Discoveries: ✓/X
- Deviations: ✓/X
- Pending Decisions: ✓/X
- Invalidated Plan Steps: ✓/X
- Quick Workarounds: ✓/X
- Quick Tips: ✓/X

### PLAN.md
- Goals & Success Criteria: ✓/X
- Task Breakdown: ✓/X
- Dependencies: ✓/X
- Timeline: ✓/X
- Risks & Mitigation: ✓/X
- Pivot Signals: ✓/X

## File Status Breakdown
### ✅ Completed ([count])
[first 3 files...]

### 🚧 In Progress ([count])
[all in-progress files...]

### 📋 Planned ([count])
[all planned files...]

## Next Steps Identified
1. [immediate next action]
2. [following action]

## Notes
- [Any important observations]
- [Suggestions for continuation]
```
