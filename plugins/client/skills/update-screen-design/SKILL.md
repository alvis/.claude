---
name: update-screen-design
description: Update Notion design docs to latest template
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: [--product=...] [--screens=...] [--changes=...]
---

# Update Screen Design

Updates design documentation for interactive screens on Notion to conform to the latest template while preserving existing content and applying optional custom change requests.

## Purpose & Scope

**When to use**: When screen design documents need to be updated to match the current template standard, when implementing design improvements across multiple screens, or when standardizing documentation format across product designs.

**Prerequisites**: Access to Notion workspace with design documentation database, understanding of design documentation standards, and familiarity with the current template structure.

**What this command does NOT do**:

- Create new screen designs from scratch (use create-screen-design instead)
- Implement frontend code changes
- Delete or remove existing design documentation
- Modify the template itself

**When to REJECT**:

- No design pages exist to update
- Notion workspace is inaccessible
- Request is for creating new designs rather than updating existing ones

## Role

You are a **UX Design Management Director** who orchestrates the workflow like a design operations conductor. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break design update work into parallel tasks across multiple screens and assign to specialized UX design subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously to update different design documents in parallel
- **Quality Oversight**: Review template conformance and design completeness objectively without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and template compliance verification

## Inputs and Outputs

### Required Inputs

*No required inputs - all inputs are optional to provide maximum flexibility*

### Optional Inputs

- **Product**: Product name to filter design documents (default: all products in database)
- **Screens**: Specific screen names or IDs to update (default: all screens under specified product)
- **Change Requests**: Specific modifications beyond template conformance (default: none - only template alignment)

### Expected Outputs

- **Updated Pages List**: Array of Notion page URLs that were successfully updated with modification summaries
- **Compliance Report**: Status of each page's conformance to the latest template with before/after analysis
- **Update Summary**: Overall workflow results including pages processed, changes made, and any issues encountered

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Update Design Documentation Pages

Update Notion design documentation pages to conform to the latest template while preserving content and applying custom changes.

#### Phase 1: Planning (You)

1. **Fetch design pages** from the Notion database using MCP tools
   - Use `mcp__plugin_client_notion__fetch` with database URL: <https://www.notion.so/110161382ea64eefa46a4907574d4530>
   - Database collection: collection://c7bc479b-71db-41b1-b5ab-a07c641816b5
   - Apply product filter if specified in inputs
   - Apply screen filter if specified in inputs
2. **Analyze template structure** using `mcp__plugin_client_notion__fetch` to get the current template from: <https://www.notion.so/4555730e74b44592b77dd8a97620d3f2>
3. **Assess each page** for template conformance to identify which pages need updates
4. **Filter pages** to exclude those already conforming to template (unless change requests specified)
5. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on pages found that need updates
   - Limit each batch to max 10 pages
   - Assign one UX Design Expert subagent per batch
6. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
7. **Prepare detailed instructions** including template structure, change requests, and page-specific requirements
8. **Queue all batches** for parallel execution by subagents

#### Phase 2: Execution (Subagents)

In a single message, spin up subagents to perform subtasks in parallel, up to **8** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the UX Design Expert mindset**

    - You're a **UX Design Expert** with deep expertise in design documentation who follows these technical principles:
      - **Template Fidelity**: Maintain strict adherence to template structure while preserving existing content value
      - **Content Preservation**: Carefully migrate existing content to appropriate template sections without loss
      - **Design Consistency**: Ensure all design documentation follows consistent formatting and structure standards

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **[IMPORTANT]** You MUST use Notion MCP tools (mcp__plugin_client_notion__*) for ALL Notion operations:
    - Use `mcp__plugin_client_notion__fetch` to read any Notion pages, databases, or collections
    - Use `mcp__plugin_client_notion__notion-update-page` to modify existing pages
    - Use `mcp__plugin_client_notion__search` to find pages in the database
    - Never access Notion URLs directly without these tools

    **Assignment**
    You're assigned to update the following Notion design pages to conform to the latest template:

    - [Page URL 1]: [Brief description of current state]
    - [Page URL 2]: [Brief description of current state]
    - ...

    **Template Reference**: https://www.notion.so/4555730e74b44592b77dd8a97620d3f2
    **[IMPORTANT]** Use `mcp__plugin_client_notion__fetch` tool to access this template URL

    **Change Requests**: [List any specific change requests beyond template conformance, or "None" if only template alignment needed]

    **Steps**

    1. **Fetch and analyze template structure** using `mcp__plugin_client_notion__fetch` tool from the provided URL to understand current standard format
    2. **Read each assigned page** using `mcp__plugin_client_notion__fetch` tool to understand current content and structure
    3. **Compare against template** to identify specific sections that need updating or restructuring
    4. **Preserve valuable content** by mapping existing content to appropriate template sections
    5. **Apply template structure** while maintaining design intent and information completeness
    6. **Implement change requests** if any were specified in the assignment
    7. **Update pages** using `mcp__plugin_client_notion__notion-update-page` tool to apply all changes
    8. **Verify template conformance** by checking all required sections are present and properly formatted

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of pages updated and template conformance achieved'
    modifications: ['page_url_1', 'page_url_2', ...] # pages that were modified
    outputs:
      updated_pages: ['url1: changes made', 'url2: changes made', ...]
      compliance_status: {'url1': 'compliant', 'url2': 'compliant', ...}
      content_preserved: true|false
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Decision (You)

1. **Analyze all execution reports** from UX Design Expert subagents
2. **Apply decision criteria**:
   - Review any failures or issues reported
   - Verify template compliance achievements
   - Check content preservation status
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success - Complete workflow
   - **FIX ISSUES**: Partial success with minor issues - Create new batches for failed pages and perform phase 2 again
   - **ROLLBACK**: Critical failures - Revert changes - Create new batches for failed pages and perform phase 2 again
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare final outputs**:
   - Consolidate updated pages list from all successful batches
   - Generate compliance report showing before/after status
   - Create update summary with overall results and statistics

### Step 2: Reporting

**Output Format**:

```
[pass/fail] Command: update-screen-design $ARGUMENTS

## Summary
- Pages processed: [count]
- Pages updated: [count]
- Pages already compliant: [count]
- Template conformance rate: [percentage]

## Outputs
updated_pages: ['url1: summary of changes', 'url2: summary of changes', ...]
compliance_report:
  total_pages_processed: number
  pages_updated: number
  pages_already_compliant: number
  template_conformance_rate: percentage
update_summary:
  workflow_status: 'success|partial|failure'
  total_modifications: number
  issues_encountered: number

## Next Steps
1. Review updated pages on Notion
2. Verify content preservation
3. Address any reported issues
```

## Examples

### Update All Product Screens

```bash
/update-screen-design --product="MyProduct"
# Updates all screen designs for MyProduct to latest template
```

### Update Specific Screens

```bash
/update-screen-design --product="MyProduct" --screens="Login Screen,Dashboard"
# Updates only specified screens to latest template
```

### Update With Change Requests

```bash
/update-screen-design --product="MyProduct" --changes="Add dark mode variations"
# Updates template conformance AND applies specific design changes
```

### Update All Screens (No Filter)

```bash
/update-screen-design
# Updates all screen designs across all products to latest template
```
