# Communication Guidelines

**Purpose**: Define clear communication patterns for development tasks, progress reporting, and stakeholder interactions
**Scope**: All development activities requiring communication with team members, stakeholders, or external parties
**Category**: Project Standards

## Communication Principles

### 1. Clarity First
- Use precise technical language when communicating with developers
- Translate technical concepts to business language for stakeholders
- Avoid ambiguity - be specific about what you're doing and why

### 2. Progress Transparency
- Report progress proactively, not just when asked
- Communicate blockers immediately when discovered
- Set realistic expectations and update them if circumstances change

### 3. Context Awareness
- Tailor communication style to your audience
- Include relevant context without overwhelming with details
- Link to detailed documentation rather than explaining everything inline

## Communication Patterns

### During Development

#### Status Updates
```
✅ Good: "Implemented user authentication with JWT tokens. All tests passing. Moving to authorization layer next."
❌ Bad: "Working on auth stuff"
```

#### Blocker Communication
```
✅ Good: "Blocked: Need clarification on password complexity requirements. Current implementation supports 8+ chars. Should we enforce special characters?"
❌ Bad: "Having issues with passwords"
```

#### Progress Reporting
- **Starting work**: "Beginning implementation of [feature]. Estimated completion: [timeframe]"
- **Mid-progress**: "Completed [X of Y] tasks. [Current focus]. On track for [deadline]"
- **Completion**: "Completed [feature]. All tests passing. Ready for review"

### Code Review Communication

#### Requesting Review
Include:
- What changed and why
- Testing performed
- Areas needing special attention
- Any trade-offs made

Example:
```
PR: Add user authentication

Changes:
- Implemented JWT-based authentication
- Added login/logout endpoints
- Created auth middleware

Testing:
- Unit tests: 98% coverage
- Integration tests: All auth flows tested
- Manual testing: Verified with Postman

Please review:
- Security implementation in auth.service.ts
- Token expiration strategy
```

#### Providing Feedback
- Be specific and actionable
- Suggest improvements, don't just criticize
- Acknowledge good patterns you see

```
✅ Good: "Consider extracting this validation logic into a separate function for reusability. See validateUserInput in user.service.ts for a similar pattern."
❌ Bad: "This code is messy"
```

### Documentation Communication

#### Inline Comments
Only when necessary:
- Complex algorithms needing explanation
- Non-obvious business logic
- Temporary workarounds with context

#### Commit Messages
Follow conventional commits:
```
feat(auth): implement JWT token refresh
fix(api): handle null response in user endpoint
docs(readme): update installation instructions
refactor(service): extract validation logic
```

#### PR Descriptions
Structure:
1. **What**: Brief description of changes
2. **Why**: Business or technical rationale
3. **How**: High-level implementation approach
4. **Testing**: How it was verified
5. **Screenshots**: For UI changes

### Stakeholder Communication

#### Technical to Non-Technical Translation
```
Technical: "Implemented Redis caching layer with 5-minute TTL for user sessions"
Translated: "Added a system to remember user information for 5 minutes, making the app respond faster"
```

#### Risk Communication
- Present the risk clearly
- Explain potential impact
- Propose mitigation strategies
- Request decisions when needed

Example:
```
Risk: Third-party API rate limits may impact feature performance
Impact: Users might experience delays during peak hours
Mitigation options:
1. Implement request queuing (2 days work)
2. Cache responses more aggressively (1 day work)
3. Upgrade API plan ($X/month)
Please advise on preferred approach.
```

## Communication Channels

### Synchronous Communication
Use for:
- Urgent blockers
- Complex discussions requiring back-and-forth
- Pair programming sessions
- Quick clarifications (< 5 min resolution)

### Asynchronous Communication
Use for:
- Progress updates
- Code reviews
- Documentation
- Non-urgent questions
- Detailed technical discussions

## Anti-Patterns to Avoid

### 1. **Information Hoarding**
❌ Working in isolation without updates
✅ Regular progress communication

### 2. **Assumption Making**
❌ "I think they want X, so I'll build that"
✅ "Let me confirm the requirements for X"

### 3. **Vague Communication**
❌ "It's mostly done"
✅ "Completed 3 of 4 components. Final component in progress, ETA 2 hours"

### 4. **Delayed Bad News**
❌ Waiting until deadline to report issues
✅ Immediate communication when problems arise

### 5. **Over-Communication**
❌ Constant updates on minor details
✅ Meaningful updates at logical checkpoints

## Communication Templates

### Daily Standup
```
Yesterday: [Completed tasks]
Today: [Planned tasks]
Blockers: [Any impediments]
```

### Technical Decision
```
Context: [Background information]
Problem: [What needs to be solved]
Options considered:
1. [Option 1] - Pros/Cons
2. [Option 2] - Pros/Cons
Recommendation: [Your suggestion and why]
```

### Bug Report
```
Summary: [Brief description]
Steps to reproduce:
1. [Step 1]
2. [Step 2]
Expected: [What should happen]
Actual: [What actually happens]
Environment: [Browser/OS/Version]
```

## Quality Checklist

Before communicating:
- [ ] Is the message clear and unambiguous?
- [ ] Have I included necessary context?
- [ ] Is the level of detail appropriate for the audience?
- [ ] Have I checked for typos and clarity?
- [ ] Am I using the right channel for this message?

## Related Standards

- [Documentation Standards](../code/documentation.md)
- [Git Workflow Standards](./git-workflow.md)
- [Code Review Workflow](../../workflows/quality/review-code.md)