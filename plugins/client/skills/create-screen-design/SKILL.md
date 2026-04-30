---
name: create-screen-design
description: Create UX design docs with responsive ASCII variations
model: opus
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: <product name> <screen descriptions...> [--constraints=...] [--platforms=...]
---

# Create Screen Design

Creates comprehensive design documentation for interactive screens (web page/app or mobile client) on Notion, following best UX standards with responsive design variations.

## Purpose & Scope

**When to use**: When you need to document screen designs for a product, create design alternatives for user interfaces, or establish design specifications for development teams.

**Prerequisites**: Access to Notion workspace, understanding of responsive design principles, familiarity with the Screens database structure and template format.

**What this command does NOT do**:

- Implement frontend components or code
- Deploy designs to production environments
- Create clickable prototypes or interactive mockups
- Modify existing screen designs (use update-screen-design instead)

**When to REJECT**:

- Product name is missing or does not exist on Notion
- No screen descriptions provided
- Request is for updating existing designs rather than creating new ones

## Role

You are a **UX Director** who orchestrates the design workflow like a creative director. You never execute design tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Design Delegation**: Break complex design work into parallel tasks and assign to specialist design subagents
- **Parallel Design Coordination**: Maximize efficiency by running multiple design subagents simultaneously for different screen variations
- **Design Quality Oversight**: Review design work objectively without being involved in execution details
- **Design Decision Authority**: Make go/no-go decisions based on subagent design reports and review results

## Inputs and Outputs

### Required Inputs

- **Product Name**: Name of the product (must exist on Notion) for which screens are being designed
- **Screen Descriptions**: Array of screen names/descriptions to be designed (e.g., "Login Screen", "Dashboard", "User Profile")

### Optional Inputs

- **Design Constraints**: Specific layout design, brand guidelines, color schemes, or design limitations (default: follow template guidelines)
- **Target Platforms**: Specific platforms to focus on (default: web and mobile)

### Expected Outputs

- **Notion Design Page**: Complete design documentation page created under the Screens database
- **Responsive Design Variations**: 5 main design variations with 3 responsive sub-variations each (15 total ASCII designs)
- **Design Specifications**: Complete design documentation following the template structure
- **Design Alternatives Section**: Detailed ASCII representations of all design variations

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Create Screen Design Documentation

Create comprehensive screen design documentation on Notion with responsive variations.

#### Phase 1: Planning (You)

1. **Receive inputs** from user (product name, screen descriptions)
2. **Validate Notion access** and verify Screens database and template availability
3. **Analyze design requirements** based on screen descriptions and product context
4. **Create dynamic page-based batches** following these rules:
   - Generate one batch per screen/page requested
   - Each batch represents one complete page with all 15 ASCII designs
   - If 1 screen requested: 1 subagent for phase 2, 1 for phase 3
   - If N screens requested: N subagents for phase 2, N for phase 3
   - Each subagent handles the complete design documentation for their assigned page
5. **Use TodoWrite** to create task list from all page batches (each page = one todo item with status 'pending')
6. **Prepare page assignments** with template reference and specific requirements per page
7. **Queue all page batches** for parallel execution by subagents

#### Phase 2: Execution (Subagents)

In a single message, spin up subagents to perform design tasks in parallel, **one subagent per page** requested.

- **[IMPORTANT]** Each subagent is responsible for creating ONE complete design page with all 15 ASCII designs
- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each page's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Senior UX Designer mindset**

    - You're a **Senior UX Designer** with deep expertise in responsive design who follows these design principles:
      - **User-Centric Design**: Always prioritize user experience and usability
      - **Responsive Excellence**: Create designs that work seamlessly across all device types
      - **Design System Consistency**: Follow established patterns and maintain visual coherence
      - **Accessibility First**: Ensure designs are accessible and inclusive
      - **Innovation Balance**: Blend creativity with proven UX patterns

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **[IMPORTANT]** You MUST use Notion MCP tools (mcp__plugin_client_notion__*) for ALL Notion operations:
    - Use `mcp__plugin_client_notion__fetch` to read any Notion pages or databases
    - Use `mcp__plugin_client_notion__notion-create-pages` to create new pages
    - Use `mcp__plugin_client_notion__search` to find existing pages
    - Never access Notion URLs directly without these tools

    **Assignment**
    You're assigned to create ONE complete screen design documentation page for:

    Product: [Product Name]
    Your Assigned Screen: [Specific Screen Description - e.g., "Login Screen" or "Dashboard"]
    Design Constraints: [Any specific constraints]

    **Reference Template**
    Follow the design template structure at: https://www.notion.so/4555730e74b44592b77dd8a97620d3f2
    **[IMPORTANT]** Use `mcp__plugin_client_notion__fetch` tool to access this template URL

    **Steps**

    1. **Copy Template First**:
       - Use `mcp__plugin_client_notion__fetch` tool to access the template at https://www.notion.so/4555730e74b44592b77dd8a97620d3f2
       - Copy the entire template structure to ensure consistency
       - This ensures all sections and formatting are preserved

    2. **Modify Template Content**:
       - Update page title with your assigned screen name
       - Fill in all template sections with screen-specific content
       - Maintain all section headings from the template
       - Customize content while preserving template structure

    3. **Create All 15 ASCII Designs**:
       - Design 5 main variations for your assigned screen
       - For EACH variation, create 3 responsive versions:
         * Desktop version (wide layout)
         * Tablet version (medium layout)
         * Mobile version (narrow layout)
       - Total: 5 variations x 3 devices = 15 ASCII designs
       - Place all designs in the "Design Alternatives" section

    4. **Complete Documentation**:
       - Document design rationale for each variation
       - Explain key features and user flow considerations
       - Link to product pages and maintain database relationships
       - Ensure all template sections are thoroughly completed
       - Use `mcp__plugin_client_notion__notion-create-pages` tool to create new page under Screens database
       - Database collection URL: collection://c7bc479b-71db-41b1-b5ab-a07c641816b5
       - Parent database URL: https://www.notion.so/110161382ea64eefa46a4907574d4530

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of what was accomplished'
    modifications: ['notion-page-created', 'design-variations-completed', ...]
    outputs:
      design_variations: [list of completed variations]
      ascii_designs: [count of ASCII designs created]
      notion_page_url: [URL of created Notion page]
      template_sections: [list of completed template sections]
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

In a single message, spin up review subagents to check quality, **one review subagent per page** created.

- **[IMPORTANT]** Each review subagent reviews ONE complete page created by a Phase 2 subagent
- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Design Quality Auditor mindset**

    - You're a **Design Quality Auditor** with expertise in UX standards who follows these principles:
      - **Template Compliance**: Ensure strict adherence to template structure and requirements
      - **Design Excellence**: Verify designs meet professional UX standards
      - **Responsiveness Validation**: Confirm all device variations are properly implemented
      - **Documentation Completeness**: Check all required sections are thoroughly completed

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review Assignment**
    You're assigned to verify ONE complete design page:

    Page to Review: [Specific Screen Name created in Phase 2]
    Template Reference: https://www.notion.so/4555730e74b44592b77dd8a97620d3f2

    **[IMPORTANT]** You MUST use Notion MCP tools for all review operations:
    - Use `mcp__plugin_client_notion__fetch` to read the created page and template
    - Use `mcp__plugin_client_notion__search` if you need to find related pages

    Review ALL aspects of this single page:
    - Template Conformance: Verify page structure matches template exactly
    - All Sections Complete: Check every template section is properly filled
    - 15 ASCII Designs: Confirm all 5 variations x 3 devices are present
    - Design Quality: Assess ASCII design clarity and readability
    - Responsive Effectiveness: Verify desktop, tablet, mobile adaptations
    - Documentation Completeness: Review design rationale and descriptions
    - Database Integration: Confirm proper Screens database relationships

    **Review Steps**

    1. **Template Verification**:
       - Use `mcp__plugin_client_notion__fetch` to read both the created page and template at https://www.notion.so/4555730e74b44592b77dd8a97620d3f2
       - Verify ALL template sections are present and properly structured
       - Confirm section headings match the template exactly
    2. **Design Count Verification**:
       - Count and verify exactly 15 ASCII designs are present
       - Check 5 main variations exist
       - Confirm each variation has desktop, tablet, and mobile versions
    3. **Design Quality Assessment**:
       - Evaluate ASCII designs for clarity and professional appearance
       - Verify responsive adaptations are meaningful and effective
    4. **Content Review**:
       - Check all template sections have substantive content
       - Verify design rationales are complete and logical
    5. **Integration Check**:
       - Use `mcp__plugin_client_notion__fetch` to verify proper placement in Screens database (https://www.notion.so/110161382ea64eefa46a4907574d4530)
       - Confirm the page exists in collection://c7bc479b-71db-41b1-b5ab-a07c641816b5
       - Verify product linking and relationships

    **Report**
    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief review summary'
    checks:
      template_compliance: pass|fail
      design_quality: pass|fail
      documentation_completeness: pass|fail
      notion_integration: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Review template compliance status
   - Consider design quality feedback
   - Assess documentation completeness
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success - Workflow complete
   - **FIX ISSUES**: Partial success with minor issues - Create new batches for failed items and perform phase 2 again - Review following phase 3 again
   - **ROLLBACK**: Critical failures - Revert changes - Create new batches for failed items and perform phase 2 again - Review following phase 3 again
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare final output**: Package Notion page URL and design documentation summary

### Step 2: Reporting

**Output Format**:

```
[pass/fail] Command: create-screen-design $ARGUMENTS

## Summary
- Product: [product name]
- Screens created: [count]
- Design variations per screen: 5
- Total ASCII designs: [count x 15]

## Outputs
status: success|failure|partial
summary: 'Screen design documentation workflow completion status'
outputs:
  notion_page_url: 'URL of created Notion page under Screens database'
  design_variations_count: 5
  total_ascii_designs: 15
  responsive_breakpoints: ['desktop', 'tablet', 'mobile']
  template_compliance: true|false
  product_integration: 'Product name linked and integrated'
modifications: ['notion-screens-database', 'design-documentation-created']
issues: ['issue1', 'issue2', ...]  # only if problems encountered

## Next Steps
1. Review design documentation on Notion
2. Gather stakeholder feedback on variations
3. Select preferred design variation for implementation
```

## Examples

### Create Single Screen Design

```bash
/create-screen-design "MyProduct" "Login Screen"
# Creates complete design documentation with 15 ASCII design variations for the login screen
```

### Create Multiple Screen Designs

```bash
/create-screen-design "MyProduct" "Dashboard" "User Profile" "Settings"
# Creates 3 design pages, each with 15 ASCII design variations (45 total)
```

### With Design Constraints

```bash
/create-screen-design "MyProduct" "Landing Page" --constraints="dark theme, minimal, no sidebar"
# Creates design documentation following specific brand constraints
```

### Error Case

```bash
/create-screen-design
# Error: Product name and screen descriptions required
# Suggestion: Provide product and screens like '/create-screen-design "MyProduct" "Dashboard"'
```
