---
allowed-tools: Bash, Read, Write, Glob, Task
argument-hint: <name> --howto="step-by-step instructions"
description: Create a new workflow file from the standard template
---

# Create Workflow

Create a new workflow file ("/create-workflow <name> --howto='...'") following the /create-workflow.md workflow. The --howto parameter describes WHAT the workflow does (the steps it will contain), not HOW the AI creates it. Generates workflow files in constitution/workflows/ directory from template:workflow template.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Modify existing workflows (use update-workflow)
- Create non-workflow documentation
- Override existing files without confirmation
- Create workflow files outside constitution/workflows/
- Create workflows from scratch (MUST use template:workflow)

**When to REJECT**:

- Empty or unclear workflow purpose
- Workflow already exists
- Invalid workflow name format
- Updating existing workflows
- Creating regular documentation instead of workflows
- Attempting to create without using the template

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Create Workflow Workflow

- Execute workflow:create-workflow

### Step 2: Reporting

**Output Format**:

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Workflow created: [name].md
- Location: [plugin]/constitution/workflows/[category]/[name].md
- Category: [category]

## Actions Taken
1. Generated workflow from template
2. Structured step-by-step instructions
3. Added verification and rollback procedures
4. Created file at specified location

## Workflow Structure
- Purpose defined
- Steps: [count]
- Verification items: [count]
- Related workflows referenced: [list]

## Next Steps
- Review workflow content
- Test workflow execution
- Update related documentation
```

## 📝 Examples

### Basic Workflow Creation

```bash
/create-workflow "deploy-service" --howto="Build Docker image, push to registry, update Kubernetes deployment, verify health checks"
# Generates: deploy-service.md
# Creates workflow with steps for containerized deployment process
# Category: backend (auto-detected from content)
```

### Frontend Workflow with Category

```bash
/create-workflow "frontend/test-component" --howto="Set up test environment, write unit tests with Jest, run tests, verify coverage meets 100% threshold"
# Generates: test-component.md
# Creates workflow with TDD approach for React components
# Category: frontend (explicitly specified)
```

### Quality Workflow

```bash
/create-workflow "verify-dependencies" --howto="Run npm audit, check license compatibility, identify outdated packages, update to latest stable versions, test after updates"
# Generates: verify-dependencies.md
# Creates workflow for dependency management and security
# Category: quality (auto-detected)
```

### Backend API Workflow

```bash
/create-workflow "build-rest-endpoint" --howto="Design API contract, implement controller, add validation middleware, write integration tests, document in OpenAPI"
# Generates: build-rest-endpoint.md
# Creates workflow following API design standards
# Includes task tracking and agent delegation
```

### Error Case - Existing Workflow

```bash
/create-workflow "review-code"
# Error: Workflow already exists
# Location: review-code.md
# Suggestion: Use /update-workflow to modify existing workflow
```

### Empty Howto Parameter

```bash
/create-workflow "analyze-performance"
# Prompt: "What process steps should this workflow document?"
# Waits for user to provide the workflow steps before proceeding
```

### Complex Multi-Phase Workflow

```bash
/create-workflow "migrate-database" --howto="Phase 1: Analyze current schema and data. Phase 2: Create migration scripts with rollback. Phase 3: Test migration in staging. Phase 4: Execute production migration with monitoring. Phase 5: Verify data integrity and update documentation"
# Generates: migrate-database.md
# Creates comprehensive workflow with multiple phases
# Includes verification steps and rollback procedures
```

### Collaboration Workflow

```bash
/create-workflow "collaboration/onboard-developer" --howto="Set up development environment, grant access permissions, assign buddy, complete orientation checklist, first PR review"
# Generates: onboard-developer.md
# Creates workflow for team onboarding process
# References multiple existing workflows
```
