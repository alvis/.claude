# Create Standard

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Generate a new standard documentation file that defines mandatory practices, patterns, and principles for a specific technical domain.
**When to use**: When AI needs to create a new standard file in the constitutions/standards/ directory based on requirements and domain analysis.
**Prerequisites**: Access to templates/standard.md, understanding of the technical domain, existing standards reviewed programmatically, clear scope definition.

### Your Role

You are a **Standards Development Director** who orchestrates the standard creation process like a technical documentation architect ensuring comprehensive and enforceable standards. You never execute writing tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break standard creation into systematic phases with specialized content development teams
- **Parallel Coordination**: Run template analysis and content generation simultaneously when dependencies allow
- **Quality Oversight**: Ensure standards are complete, clear, and technically sound through review
- **Integration Authority**: Make go/no-go decisions on standard completeness and publication readiness

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Technical Domain**: Specific area requiring standardization (frontend, backend, code, quality, security, project)
- **Standard Requirements**: Problem description and scope that the standard needs to address

#### Optional Inputs

- **Existing Standards Context**: Related standards that should be referenced or complemented (default: discover during analysis)
- **Target Audience**: Specific roles that will use this standard (default: developers and architects)
- **Technology Scope**: Specific technologies or frameworks to cover (default: general patterns)
- **Standard Category**: Specific subdirectory for placement (default: determine from domain)

#### Expected Outputs

- **Standard File Path**: Absolute path to the created standard file (e.g., /path/to/constitutions/standards/category/filename.md)
- **Implementation Summary**: Comprehensive summary of standard creation including scope, principles, and integration details

#### Data Flow Summary

The workflow takes technical domain requirements and creates a comprehensive standard document through four integrated phases: planning and analysis (you), implementation (single subagent), review (same subagent), and decision with retry logic (you).

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                        SINGLE SUBAGENT
(Orchestrates Only)             (Executes Tasks)
   |                                |
   v                                v
[START]
   |
   v
[Step 1: Create Standard] ─────────→ (4-Phase Integrated Process)
   |
   ├─[Phase 1: Planning & Analysis]──┐
   │  (You analyze requirements,     |
   │   determine standard path,      |
   │   prepare implementation plan)  |
   │                                 |
   ├─[Phase 2: Implementation]───────→ (Subagent: create standard file)
   │                                   |
   ├─[Phase 3: Review]─────────────────→ (Same Subagent: review quality)
   │                                   |
   └─[Phase 4: Decision]──────────────┐
      (You decide next action:        |
      PROCEED, FIX ISSUES, ROLLBACK)  |
   |                                  |
   v                                  |
[END]                                 |

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan, orchestrate, and decide
• RIGHT COLUMN: Single subagent executes implementation and review
• PHASE 1: You determine standard path and create plan
• PHASE 2: Subagent attempts implementation
• PHASE 3: Same subagent reviews quality and compliance
• PHASE 4: You decide: PROCEED, FIX ISSUES, or ROLLBACK
• ITERATIVE: Phase 2 → Phase 3 → Phase 4 → repeat if needed
═══════════════════════════════════════════════════════════════════

Note: 
• You: Plan creation, suggest standard path, make decisions
• Single Subagent: Execute implementation and review
• Workflow is ITERATIVE: Can retry with fixes or rollback
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Create Standard (Single integrated step with 4 phases)

### Step 1: Create Standard

**Step Configuration**:

- **Purpose**: Create a complete standard document through integrated planning, implementation, review, and decision phases
- **Input**: Technical Domain, Standard Requirements from workflow inputs
- **Output**: Standard file path and implementation summary
- **Sub-workflow**: None
- **Parallel Execution**: No (single subagent handles phases 2 and 3)

#### Phase 1: Planning & Analysis (You)

**What You Do**:

1. **Receive inputs** from external sources (technical domain, standard requirements)
2. **Analyze domain requirements** to understand scope and boundaries
3. **Review template structure** by examining templates/standard.md
4. **List all related resources** using find commands for existing standards
5. **Determine target standard path** following this structure:
   - Base path: constitutions/standards/
   - Category: [coding|project|quality]/[subcategory if needed]/
   - Filename: descriptive-kebab-case.md
   - Example: constitutions/standards/coding/frontend/react-components.md
6. **Identify related standards** that should be referenced or cross-linked
7. **Create implementation plan** including:
   - Suggested standard file path
   - Core principles to develop (3-5)
   - Main topic areas to cover
   - Anti-patterns to document
   - Related standards to reference
8. **Prepare comprehensive instructions** for the single subagent with template requirements

**OUTPUT from Planning**: 
- Suggested standard file path (e.g., constitutions/standards/coding/backend/error-handling.md)
- Implementation plan with all sections outlined
- Template usage instructions for subagent

#### Phase 2: Implementation (Single Subagent)

**What You Send to the Subagent**:

In a single message, You dispatch ONE subagent to implement the complete standard based on your planning.

- **[IMPORTANT]** Provide the suggested standard file path from Phase 1
- **[IMPORTANT]** Include complete implementation plan with all sections outlined
- **[IMPORTANT]** The subagent should return ONLY success or failure status

Request the subagent to perform the following implementation:

    >>>
    **ultrathink: adopt the Standards Implementation Specialist mindset**

    - You're a **Standards Implementation Specialist** with deep expertise in creating comprehensive standards who follows these technical principles:
      - **Template Adherence**: Follow the standard template structure exactly
      - **Content Excellence**: Write clear, actionable, and enforceable standards
      - **Code Quality**: Ensure all examples compile and demonstrate best practices
      - **Integration Focus**: Create proper cross-references and index updates

    **Template Usage Requirement**
    
    - Copy and paste templates/standard.md first, then update content following the instruction ultrathink
    - Ensure all template sections are properly filled with domain-specific content
    - Replace all placeholders with actual values

    **Assignment**
    You're assigned to create the complete standard at the following path:
    - Target Path: [suggested standard file path from Phase 1]
    - Implementation Plan: [complete plan from Phase 1]

    **Steps**

    1. Load and prepare template:
       - Read templates/standard.md for structure
       - Identify all sections and placeholders
       - Prepare content structure based on plan
    
    2. Generate core content:
       - Write 3-5 core principles with clear titles and explanations
       - Create TypeScript code examples for each principle
       - Develop main topic areas with patterns and rules
       - Document anti-patterns with problematic examples
       - Build decision trees and quick reference tables
    
    3. Create standard file:
       - Compile all content following template structure
       - Replace all template placeholders
       - Ensure all code examples are valid TypeScript
       - Write file to specified path
       - Validate file creation success
    
    4. Update indexes:
       - Update constitutions/standards/README.md
       - Update category-specific README if exists
       - Add appropriate cross-references

    **Report**
    **[IMPORTANT]** Return implementation status with summary:

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of standard creation'
    standard_path: 'absolute path if created'
    ```
    <<<

#### Phase 3: Review (Same Subagent)

**When You Trigger This Phase**: Always after Phase 2 completion

**What You Send to the Same Subagent**:

Continue with the SAME subagent to review the implementation quality and compliance.

- **[IMPORTANT]** This phase is always executed after implementation
- **[IMPORTANT]** The same subagent that attempted implementation performs the review
- **[IMPORTANT]** Subagent provides detailed review report for your decision

Request the same subagent to review and report:

    >>>
    **ultrathink: continue as Standards Implementation Specialist with quality review**

    - You're continuing as the **Standards Implementation Specialist** now focusing on quality review:
      - **Compliance Check**: Verify standard follows template structure
      - **Content Quality**: Assess clarity and completeness of principles
      - **Code Validation**: Check all TypeScript examples compile
      - **Integration Review**: Verify index updates and cross-references

    **Review Assignment**
    Review the standard file created in Phase 2 implementation:

    **Review Steps**

    1. Template compliance check:
       - Verify all template sections are present
       - Check that placeholders are replaced
       - Ensure proper markdown structure
    
    2. Content quality assessment:
       - Review 3-5 core principles for clarity
       - Check code examples for correctness
       - Verify anti-patterns are documented
       - Assess decision trees and tables
    
    3. Integration validation:
       - Check README.md updates
       - Verify cross-references work
       - Ensure file path is correct
    
    4. Overall quality evaluation:
       - Is the standard actionable and enforceable
       - Are examples clear and compilable
       - Does it integrate with existing standards

    **Report**
    **[IMPORTANT]** Provide detailed review report for decision-making:

    ```yaml
    status: pass|fail
    summary: 'Brief review summary'
    checks:
      template_compliance: pass|fail
      content_quality: pass|fail
      code_examples: pass|fail
      integration: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|fix_issues|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze review report** from Phase 3
2. **Apply decision criteria** based on review status and recommendations
3. **Select next action**:

   **PROCEED** (Review passes or minor warnings only):
   - Extract standard file path from implementation
   - Compile implementation summary
   - Complete workflow with final outputs

   **FIX ISSUES** (Partial success with fixable issues):
   - Identify specific fixes needed from review report
   - Return to Phase 2 with targeted corrections
   - Maximum 3 fix attempts before escalation
   - After fixes → Phase 3 review → Phase 4 decision → repeat if needed

   **ROLLBACK** (Critical failures requiring cleanup):
   - Revert any partial changes made
   - Clean up incomplete files
   - Return to Phase 1 for re-planning
   - Maximum 2 rollback attempts before workflow termination

4. **Iteration Management**:
   - Track attempt count for each action type
   - Adjust instructions based on review feedback
   - Escalate to user if max attempts exceeded

5. **Decision Loop Management**: In phase 4, you(the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

**Final Output**:
- Standard file path (absolute path to created file)
- Implementation summary including:
  - Domain and scope covered
  - Core principles established
  - Patterns and anti-patterns documented
  - Cross-references created
  - Total attempts required


### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: create-standard
status: completed
outputs:
  standard_file_path: 'constitutions/standards/[category]/[filename].md'
  implementation_summary:
    domain: '[technical domain]'
    scope: '[scope covered]'
    core_principles: 5
    code_examples: 8
    anti_patterns: 3
  quality_assurance:
    template_compliance: passed
    content_quality: passed
    code_validation: passed
    integration_verified: passed
  cross_references:
    related_standards: ['standard1.md', 'standard2.md']
    index_updates: completed
total_attempts: 1
summary: |
  Successfully created standard for [technical domain] with [N] core principles,
  comprehensive TypeScript examples, and clear anti-patterns. Standard is fully
  integrated with cross-references and index updates completed.
```