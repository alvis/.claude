# Review Service Operation

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Orchestrate comprehensive validation of service operations in Notion for completeness and coding standards compliance. This workflow produces detailed validation reports with actionable recommendations for improving service operation documentation.
**When to use**: When reviewing service operations for standards compliance, validating completeness before implementation, or conducting quality assurance on service operation specifications in Notion
**Prerequisites**: Access to Notion workspace with Services and Service Operations databases, valid service name that exists in the Services database, appropriate permissions to read operation pages

### Your Role

You are a **Service Operations Quality Director** who orchestrates the workflow like a quality assurance director overseeing comprehensive service reviews. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex work into parallel tasks if necessary (e.g. > 10 resources) and assign to the right specialist subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously when dependencies allow
- **Quality Oversight**: Review work objectively without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and review results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Service Name**: The name of the service to review as it appears in the Services database in Notion

#### Optional Inputs

- **Operation Filter**: Optional specific operation name for selecting specific operations belonging to the target service for focused review (default: review all operations)
- **Area Filter**: Optional area name for selecting specific operations belonging to the target service for focused review by functional domain (default: review all areas)

#### Expected Outputs

- **Validation Report**: Comprehensive markdown report detailing all service operations reviewed, issues found, and actionable recommendations
- **Service Context**: Extracted service metadata, operation list, and data operation dependencies for downstream workflows
- **Compliance Status**: Pass/fail status for each operation against coding standards and completeness criteria

#### Data Flow Summary

The workflow takes a service name and optional filters, discovers all related operations through Notion database queries, then distributes detailed validation tasks across multiple subagents working in parallel. Each operation is analyzed for use case completeness, requirements alignment, pseudo code standards compliance, and data operation consistency, with results consolidated into a comprehensive validation report.

### Visual Overview

#### Main Workflow Flow

```plaintext
    YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
     |                                   |
     v                                   v
  [START]
     |
     v
[Step 1: Service Operation Review] ───→ (Phase 1: Planning)
     |                                   |
     |                                   v
     |                            Subagent A: Service Discovery
     |                            ├─ Locate Services database
     |                            ├─ Extract service context
     |                            └─ List operations & data ops
     |
     v
 [Planning Complete] ←─────────────── (Report service context)
     |
     v
[Phase 2: Execution] ───────────→ (Parallel Operation Reviews)
     |               ├─ Subagent B: Operation 1 Review      ─┐
     |               ├─ Subagent C: Operation 2 Review      ─┼─→ [Decision: Issues?]
     |               ├─ Subagent D: Operation 3 Review      ─┤     ↓
     |               └─ Subagent E: Operation 4 Review      ─┘  [Handle Issues]
     |
     v
[Phase 3: Decision] ───────────→ (Consolidate Results)
     |                            └─ Generate validation report
     |
     v
   [END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute validation tasks in parallel  
• ARROWS (───→): You assign work to subagents
• DECISIONS: You halt on issues, continue on success
═══════════════════════════════════════════════════════════════════

Note:
• You: Orchestrate service discovery, batch operation reviews, handle issues
• Discovery Subagent: Extract service context and operation lists (<1k tokens)
• Review Subagents: Validate individual operations in parallel (<1k tokens)
• Max 4 operations reviewed simultaneously for optimal throughput
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Service Operation Review

### Step 1: Service Operation Review

**Step Configuration**:

- **Purpose**: Orchestrate comprehensive validation of all service operations for the specified service through parallel subagent execution
- **Input**: Service name (from workflow input), optional operation and area filters
- **Output**: Validation report with service context, compliance status, and actionable recommendations
- **Sub-workflow**: None
- **Parallel Execution**: Yes - service discovery followed by parallel operation validation (max 4 simultaneous)

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** service name and optional filters from workflow inputs
2. **Identify standards** to apply: documentation standards and general coding principles
3. **Delegate service discovery to subagent** by:
    - Spawn a discovery subagent with ultrathink mindset
    - Request the subagent to:
      - Use Notion search to locate the `Services` database (with type database)
      - Fetch the `Services` database and locate the service page for the specified service name
      - Extract service-level context via Notion Fetch from the service page
      - From the service page extract metadata (name and id BUT NOT content) of all Service Operations belonging to the service from the link to the database view via Notion Fetch
      - From the service page extract metadata (name and id BUT NOT content) of all Data Operations belonging to the service from the link to the database view via Notion Fetch
      - Apply any optional filters to the operations list
      - Return the following discovery template:
        ```yaml
        status: success|failure|partial
        summary: 'Service discovery and context extraction completed'
        modifications: [] # No modifications in discovery phase
        outputs:
          service_context: 'Service summary and metadata'
          service_operations: ['op1_name:op1_id', 'op2_name:op2_id', ...]
          data_operations: ['data_op1_name:data_op1_id', ...]
          filtered_operations: ['filtered list if filters applied']
        issues: ['issue1', 'issue2', ...]  # only if problems encountered
        ```
4. **Create operation batches** from discovered operations following these rules:
   - Generate batches at runtime based on operations found
   - Limit each batch to max 2 operations for optimal validation throughput
   - Assign validation subagents to perform individual operation reviews
5. **Use TodoWrite** to create validation task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare validation instructions** including complete service context for each subagent
7. **Queue all validation batches** for parallel execution by subagents

**OUTPUT from Planning**: Task batch assignments as todos

**Phase 1 Output Specification**:
After Planning completes successfully, the discovery phase produces:

- **Service Summary and Context**: Complete service metadata, description, and context information
- **Service Operations List**: Complete list of service operations with name:id pairs belonging to the target service
- **Data Operations List**: Complete list of data operations with name:id pairs used by the target service  
- **Filtered Operations List**: Final list of operations to review (after applying optional operation and area filters)

#### Phase 2: Execution (Subagents)

**What You Send to Validation Subagents**:

In a single message, you spin up validation subagents to perform operation reviews in parallel, up to **2** operations at a time:

- **[IMPORTANT]** When any issues are reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** Pass complete service context from planning phase to each validation subagent
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Service Operation Validator mindset**

    - You're a **Service Operation Validator** with deep expertise in service operation documentation who follows these technical principles:
      - **Standards Compliance**: Rigorously validate against coding and documentation standards
      - **Completeness Verification**: Ensure all required sections are present and complete
      - **Consistency Checking**: Verify alignment between use cases, requirements, and pseudo code
      - **Quality Assurance**: Identify gaps and provide actionable recommendations

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - documentation.md
    - error-handling-logging.md
    - typescript.md
    - functions.md
    - general-principles.md

    **Assignment**
    You're assigned to validate this service operation:

    - **Operation**: [operation name and ID from discovery]
    - **Service Context**: [complete service context from discovery phase]
    - **Data Operations Available**: [list of data operations from discovery]
    - **Service Operations Available**: [list of all service operations from discovery]

    **Steps**

    1. **Fetch Operation Content**: Use Notion fetch to retrieve complete operation page content
    2. **Validate Use Cases**: Verify documented use cases exist, check sync block alignment, suggest missing scenarios
    3. **Check Requirements**: Verify input parameters, output interfaces, functional requirements completeness
    4. **Validate Pseudo Code**: Check structure, import order, naming conventions, TypeScript usage, comments formatting
    5. **Verify Data Operations**: Compare pseudo code data operation calls with Data Operations field, check consistency
    6. **Check Requirements Alignment**: Ensure use cases are covered by requirements
    7. **Validate Permissions**: Verify permission checks in pseudo code match permission field
    8. **Assess Code-Requirements Consistency**: Confirm business logic implements all requirements

    **Validation Criteria**
    Apply these specific validation rules:

    **Use Case Validation**:
    - [IMPORTANT] DO NOT complain about template placeholders in use case section
    - Verify at least one documented use case exists
    - Check sync block alignment with service page scenarios
    - Suggest missing user scenarios if needed

    **Requirements Completeness**:
    - Verify input parameters with types and constraints
    - Check output interfaces documentation
    - Validate functional requirements for business logic
    - Suggest missing interface definitions

    **Pseudo Code Standards**:
    - Validate structure follows createOperation pattern using this template:
    
    ```typescript
    import { ... } from 'node:xxx';
    
    import { ... } from 'xxx';
    
    import { createOperation } from '#factory';
    
    export default createOperation.<operationName in camelCase>(
    async ({ inputParam1, inputParam2 }, { verifyAccess, data: { entityName }, integration: { library }, service: { self, otherService } }) => {
       // check permission
       verifyAccess(`<resource>:<identifier>:<action>`);
    
       // business logic implementation
       const result = await entityName.dataOperation({ parameters });
    
       // additional processing
       // ...
    
       return result;
    },
    );
    ```
    
    - Check import order: built-in → third-party → project modules
    - Verify variable naming: camelCase variables, PascalCase constants
    - Confirm TypeScript strict typing, avoid any
    - Check comments: always in lower case except for tags such as `// NOTE:` or references to variable/type/interface/acronym names such as `// assume UTC timezone`
    - Verify arrow functions, destructuring, async/await usage
    - [IMPORTANT] Only check imports that are definitely needed
    - [IMPORTANT] Pseudo code is meant to be incomplete - focus on business logic

    **Data Operations Consistency**:
    - Extract data operation calls from pseudo code
    - Map with data operations from Data Operations field (may be ID or URL)
    - [IMPORTANT] Data Operations field is PascalCase, pseudo code is camelCase
    - [IMPORTANT] DO NOT fetch related data operation pages
    - Suggest updates for consistency

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Operation validation status (pass/issues found)
    - Detailed list of issues with specific locations and fix suggestions (with code implementation if code related)
    - Code snippets around issues where applicable
    - Display content diffs for changes
    - Actionable recommendations for improvements
    - If no issue is found, the subagent should simply report a ✅ for the operation page

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Operation validation completed for [operation name]'
    modifications: [] # No modifications in validation phase
    outputs:
      operation_name: '[operation name]'
      validation_status: 'pass|issues_found'
      issues_found: ['issue1 with location and fix', 'issue2', ...]
      recommendations: ['improvement1', 'improvement2', ...]
    issues: ['critical_issue1', ...]  # only critical problems that block validation
    ```
    <<<

**Issue Escalation Process**:

When issues are found by any validation subagent:

1. **Pause Further Validation**: Management agent stops dispatching further subagents until all issues have been rectified
2. **Present Detailed Issues Report**: The subagent presents detailed issues report (including code snippet around the issue) and fix suggestions to the management agent, which may include:
   - Use Cases content changes
   - Permission field updates
   - Requirement modifications
   - Pseudo Code corrections (with code implementation if code related)
   - Display content diffs for changes
3. **Present to User**: Primary agent presents in full detail the issues (including code snippet around the issue) and fix suggestions (with code implementation if code related) to the user
4. **Await Approval**: Wait for user approval before continuing
5. **Resolution Confirmation**: Verify fixes applied correctly, resume validation process, and continue to next operation

#### Phase 3: Decision (You)

**What You Do**:

1. **Collect all validation reports** from Phase 2 execution subagents
2. **Consolidate validation results**:
   - Analyze all individual operation validation reports
   - Identify common issue patterns across operations
   - Categorize operations by functional domain and status
   - Assess overall service operation quality and compliance
3. **Use TodoWrite** to update task list and mark all 'in_progress' items as 'completed'
4. **Generate comprehensive validation report** with consolidated findings including:
     - Service summary and context
     - Operations reviewed count and status
     - Common issue patterns identified across operations
     - Issues found organized by operation and type
     - Actionable recommendations for each issue
     - Overall service operation quality assessment
     - Next steps and manual actions required

**Report Template**:

```markdown
Operation Validation Report

## Summary
- Service: [service-name]
- Operations checked: [count]
- Issues found: [count]
- Status: [PASS/ISSUES_FOUND]

## Operations by Functional Domain

### [Domain Group]

✅ Operation: [Operation Name]
   Status: No issues found

❌ Operation: [Operation Name]
   - **Issue Type**: [Use Cases/Requirements/Pseudo Code/Data Ops/Alignment]
   - **Problem**: [Specific issue description with location]
   - **Detailed Fix Suggestion**: [Actionable recommendation with code if applicable]

## Next Steps
- [Required manual actions]
- [Recommended improvements]
```

### Workflow Completion

**Report the workflow output as specified**:

```yaml
validation_report:
  location: "path/to/validation_report.md"
  format: "structured_markdown"
  completeness: "complete|partial"
service_context:
  service_name: "service-name"
  service_summary: "brief service description"
  service_operations: ["op1_name:op1_id", "op2_name:op2_id", "..."]
  data_operations: ["data_op1_name:data_op1_id", "data_op2_name:data_op2_id", "..."]
  filtered_operations: ["filtered list if filters applied"]
compliance_status:
  total_operations_reviewed: 5
  operations_with_issues: 2
  operations_passing: 3
  overall_quality: "excellent|good|needs_improvement|poor"
  standards_compliance: "pass|fail"
quality_assessment:
  functional_domains: ["domain1: status", "domain2: status", "..."]
  common_issue_patterns: ["pattern1", "pattern2", "..."]
  critical_issues_found: ["critical1", "critical2", "..."]
  actionable_recommendations: ["recommendation1", "recommendation2", "..."]
workflow_status: "success|partial|failure"
summary: "Brief description of service operation review completion"
```
