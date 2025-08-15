---
allowed-tools: Read, Write, Glob, Task
argument-hint: <name> --howto="step-by-step instructions"
description: Create a new workflow file from the standard template
---

# Create Workflow

Create a new workflow file ("/create-workflow <name> --howto='...'") following the constitutions/workflows/project/create-workflow.md workflow. The --howto parameter describes WHAT the workflow does (the steps it will contain), not HOW the AI creates it. Generates workflow files in constitutions/workflows/ directory from @templates/workflow.md template.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify existing workflows (use update-workflow)
- Create non-workflow documentation
- Override existing files without confirmation
- Create workflow files outside constitutions/workflows/
- Create workflows from scratch (MUST use templates/workflow.md)

**When to REJECT:**

- Empty or unclear workflow purpose
- Workflow already exists
- Invalid workflow name format
- Updating existing workflows
- Creating regular documentation instead of workflows
- Attempting to create without using the template

## 📊 Dynamic Context

- **[IMPORTANT]** You must carefully remember all the context defined below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`

## 🔄 Workflow

**🔴 CRITICAL: This command MUST follow constitutions/workflows/project/create-workflow.md exactly**

### Phase 1: Planning (Following create-workflow.md Steps 1-3)

1. **Analyze Need for New Workflow**
   - Parse $ARGUMENTS to extract name and --howto description
   - Search existing workflows in `constitutions/workflows/` for overlap
   - Identify specific tasks this workflow will standardize
   - Determine category: coding/, frontend/, backend/, quality/, project/, collaboration/
   - Confirm workflow addresses a repeatable process
   - If howto empty, ask: "What process steps should this workflow document?"

2. **Copy and Customize Template**
   - **MANDATORY**: Use templates/workflow.md as base - never create from scratch
   - Copy template to appropriate category directory
   - Replace `[Workflow Title]` with clear, action-oriented title
   - Keep ALL AI instruction comments for future maintenance
   - Ensure workflow name uses kebab-case
   - Preserve exact section structure from template

3. **Define Expert Role**
   - Choose expert title relevant to workflow domain
   - Define domain of expertise required
   - Create 3-5 key principles that guide decision-making
   - Write clear justification for each principle
   - Format principles as bold labels with explanations

### Phase 2: Execution (Following create-workflow.md Steps 4-7)

1. **Document Workflow Steps**
   - Create numbered, action-oriented titles
   - Write brief description of what each step accomplishes
   - Break complex steps into checklist items
   - Add code examples showing concrete implementation
   - Include anti-patterns showing what to avoid
   - Ensure examples use actual code, not placeholders
   - Include task tracking requirements per template

2. **Link Required Standards**
   - Add red circle emoji (🔴) with "MANDATORY" text
   - Include statement that all standards must be followed
   - Create links to relevant standards using relative paths
   - Write brief descriptions of what each standard covers
   - Group by category if many standards
   - Verify all linked standard files exist

3. **Document Common Issues**
   - Format each issue with bold type
   - Write clear problem descriptions
   - Use arrow (→) separator between problem and solution
   - Cover environment setup problems
   - Include tool configuration issues
   - Document dependency conflicts
   - Address permission errors

4. **Add Output Template (If Applicable)**
   - Determine if workflow produces a deliverable
   - Specify type of output (e.g., "Review Report Template")
   - Define expected format and structure
   - List required sections with example content
   - Skip this section if no output is produced

### Phase 3: Verification (Following create-workflow.md Steps 8-9)

1. **Validate Workflow Completeness**
   - **VERIFY**: Final file follows templates/workflow.md structure exactly
   - All template sections filled or intentionally removed
   - Every step has clear instructions
   - Complex steps include examples
   - Both good (✅) and bad (❌) practices shown
   - All referenced standards and workflows exist
   - Tool recommendations included
   - Common issues documented
   - Output template provided if applicable
   - AI instruction comments removed
   - Section order matches template
   - Heading hierarchy follows template pattern

2. **Update Workflow Index**
   - Update `constitutions/workflows/README.md` with link and description
   - Update category-specific README if exists
   - Add references in related workflows that might use this

3. **Quality Assurance**
   - Confirm workflow follows template structure
   - Validate all mandatory sections present
   - Check examples are concrete, not placeholders
   - Verify anti-patterns show both problem and solution

4. **Side Effect Validation**
   - File saved to correct location
   - Category directory created if needed
   - No existing files overwritten without consent
   - Index files updated appropriately

### Phase 4: Reporting

**Output Format:**

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Workflow created: [name].md
- Location: constitutions/workflows/[category]/[name].md
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
# Generates: constitutions/workflows/backend/deploy-service.md
# Creates workflow with steps for containerized deployment process
# Category: backend (auto-detected from content)
```

### Frontend Workflow with Category

```bash
/create-workflow "frontend/test-component" --howto="Set up test environment, write unit tests with Jest, run tests, verify coverage meets 100% threshold"
# Generates: constitutions/workflows/frontend/test-component.md
# Creates workflow with TDD approach for React components
# Category: frontend (explicitly specified)
```

### Quality Workflow

```bash
/create-workflow "verify-dependencies" --howto="Run npm audit, check license compatibility, identify outdated packages, update to latest stable versions, test after updates"
# Generates: constitutions/workflows/quality/verify-dependencies.md
# Creates workflow for dependency management and security
# Category: quality (auto-detected)
```

### Backend API Workflow

```bash
/create-workflow "build-rest-endpoint" --howto="Design API contract, implement controller, add validation middleware, write integration tests, document in OpenAPI"
# Generates: constitutions/workflows/backend/build-rest-endpoint.md
# Creates workflow following API design standards
# Includes task tracking and agent delegation
```

### Error Case - Existing Workflow

```bash
/create-workflow "review-code"
# Error: Workflow already exists
# Location: constitutions/workflows/quality/review-code.md
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
# Generates: constitutions/workflows/backend/migrate-database.md
# Creates comprehensive workflow with multiple phases
# Includes verification steps and rollback procedures
```

### Collaboration Workflow

```bash
/create-workflow "collaboration/onboard-developer" --howto="Set up development environment, grant access permissions, assign buddy, complete orientation checklist, first PR review"
# Generates: constitutions/workflows/collaboration/onboard-developer.md
# Creates workflow for team onboarding process
# References multiple existing workflows
```
