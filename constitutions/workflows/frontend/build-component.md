# Build React Component

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Complete workflow for building React components with comprehensive testing, Storybook documentation, and accessibility compliance through streamlined three-phase execution
**When to use**: Creating new React components from scratch, building multiple related components, creating component families or design system components
**Prerequisites**: React development environment set up, project structure understood, familiarity with React patterns and testing practices, Storybook configuration available

### Your Role

You are a **Frontend Development Director** who orchestrates component development like a UI/UX engineering project manager. You never execute development tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Assign complete component development to subagents, each capable of creating up to 5 complete components with all their files
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously, each handling complete component packages
- **Quality Oversight**: Review component implementations objectively ensuring accessibility and React standards compliance
- **Decision Authority**: Make architectural decisions based on subagent analysis and component requirements

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Component Names**: Name(s) of React component(s) to build (PascalCase) - can be a single component or array of related components
- **Component Requirements**: Functional requirements and design specifications for each component
- **Props Interface**: Required and optional props with types and descriptions for each component

#### Optional Inputs

- **Design System Integration**: Whether component should integrate with existing design system (default: true)
- **Accessibility Level**: WCAG compliance level required (default: AA)
- **Performance Requirements**: Specific performance optimization needs

#### Expected Outputs

- **Component Implementation(s)**: Complete React component(s) with TypeScript types (one or more .tsx files)
- **Storybook Stories with Tests**: Interactive documentation with all component variants and interaction tests using play functions
- **Type Exports**: Exported TypeScript interfaces for external consumption for all components
- **Documentation**: JSDoc comments and usage examples for all components
- **Accessibility Compliance**: WCAG-compliant implementation with proper ARIA attributes for all components

#### Data Flow Summary

The workflow takes component specifications and transforms them into production-ready React components by systematically planning component architecture in Phase 1, deploying subagents that each create complete component packages (up to 5 components per subagent, each with implementation and story files including tests) in Phase 2, and performing comprehensive quality verification in Phase 3.

### Visual Overview

#### Main Workflow Flow

```plaintext
[START]
   |
   v
[Step 1: Build React Components]
   |
   ├─ Phase 1: Planning (You)
   │   └─ Analyze requirements & batch components (up to 5 per subagent)
   |
   ├─ Phase 2: Parallel Execution (Subagents)
   │   ├─ Subagent A: Creates components 1-5
   │   │   └─ Each with .tsx + .stories.tsx (includes tests)
   │   ├─ Subagent B: Creates components 6-10
   │   │   └─ Each with .tsx + .stories.tsx (includes tests)
   │   └─ Subagent N: Creates remaining components
   │       └─ Each with .tsx + .stories.tsx (includes tests)
   |
   └─ Phase 3: Verification (You + Verification Subagents)
       └─ Quality checks: TypeScript, ESLint, Test Coverage, Accessibility
   |
   v
[Decision: PROCEED / RETRY / ROLLBACK]
   |
   v
[END]

Legend:
═══════════════════════════════════════════
• Each subagent creates up to 5 complete components
• Each component = 2 files (.tsx + .stories.tsx)
• Stories include interaction tests via play functions
• All subagents work in parallel for efficiency
═══════════════════════════════════════════
```

## 3. WORKFLOW IMPLEMENTATION

### Step 1: Build Complete React Component

**Step Configuration**:

- **Purpose**: Create complete React component(s) with implementation, testing, documentation, and quality verification
- **Input**: Component name(s), requirements, and props interface(s) from workflow inputs
- **Output**: Production-ready React component(s) with all supporting files and documentation
- **Sub-workflow**: None
- **Parallel Execution**: Yes - subagents each create up to 5 complete components in Phase 2

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from workflow invocation (component name(s), requirements, props interface(s))
2. **Analyze component count** and determine batching strategy:
   - Single component: Assign to one subagent to create all files
   - Multiple components: Group into batches of up to 5 components per subagent
   - Component families: Group related components together for consistency
3. **Determine the standards** to send to all subagents for consistent quality across all components
4. **Create dynamic batches** following these rules:
   - Each batch contains 1-5 complete components
   - Each subagent creates ALL files for their assigned components:
     - ComponentName.tsx (implementation with accessibility)
     - ComponentName.stories.tsx (Storybook documentation with interaction tests)
   - Number of subagents = Math.ceil(total_components / 5)
   - Assign related components to the same subagent when possible
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare comprehensive task assignments** with component specifications for each subagent
7. **Queue all batches** for parallel execution by Full-Stack Component Developer subagents

**OUTPUT from Planning**: Component batch assignments for parallel development (up to 5 components per batch)

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to create complete components in parallel. Each subagent handles **up to 5 complete components**.

- **[IMPORTANT]** Each subagent creates ALL files for their assigned components (implementation, tests, stories)
- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about creating complete, production-ready components
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

```
>>>
**ultrathink: adopt the Full-Stack Component Developer mindset**

    - You're a **Full-Stack Component Developer** with comprehensive expertise in React development who follows these technical principles:
      - **Complete Ownership**: Create entire components with all their files (implementation, tests, stories)
      - **Standards Compliance**: Follow all assigned standards without exception for every file
      - **Component Excellence**: Deliver production-ready components with full test coverage and documentation
      - **Quality Assurance**: Build in quality, accessibility, and type safety from the start

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - constitutions/standards/coding/general-principles.md
    - constitutions/standards/coding/typescript.md
    - constitutions/standards/coding/functions.md
    - constitutions/standards/coding/documentation.md
    - constitutions/standards/coding/testing.md
    - constitutions/standards/coding/frontend/react-components.md
    - constitutions/standards/coding/frontend/react-hooks.md
    - constitutions/standards/coding/frontend/accessibility.md
    - constitutions/standards/coding/frontend/storybook.md
    - constitutions/standards/coding/naming/functions.md

    **Key React Standards to Apply**:

    **Component Structure** (from react-components.md):
    ```typescript
    // ALWAYS use this pattern for components
    export interface ComponentNameProps {
      variant?: 'primary' | 'secondary';
      onClick?: () => void;
      children: ReactNode;
    }

    export const ComponentName: FC<ComponentNameProps> = ({ 
      variant = 'primary', 
      ...props 
    }) => {
      return <element className={variant} {...props} />;
    };
    ```

    **Storybook with Tests** (from storybook.md):
    ```typescript
    // Story file includes both documentation AND tests
    import type { Meta, StoryObj } from '@storybook/react';
    import { within, userEvent } from '@storybook/testing-library';
    import { expect } from '@storybook/jest';

    const meta = {
      title: 'Components/Category/ComponentName',
      component: ComponentName,
      tags: ['autodocs'],
    } satisfies Meta<typeof ComponentName>;

    export default meta;
    type Story = StoryObj<typeof meta>;

    // Story with interaction test
    export const Interactive: Story = {
      args: { children: 'Click me' },
      play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const button = canvas.getByRole('button');
        
        // Test interactions
        await userEvent.click(button);
        await expect(button).toHaveBeenCalled();
      },
    };
    ```

    **Assignment**
    You're assigned to create the following complete component(s) with ALL their files:

    Components to build: [List of 1-5 component names]

    **For EACH component, you must create**:

    **1. ComponentName.tsx - Implementation File**:
    - Create full React component with TypeScript
    - Export props interface for external consumption
    - Implement accessibility features and ARIA attributes
    - Apply performance optimizations (React.memo, useMemo, useCallback) as needed
    - Follow FC pattern with arrow functions
    - Add comprehensive JSDoc comments
    - Example structure:
      ```typescript
      import { FC, ReactNode } from 'react';

      /**
       * Button component for user interactions
       * @example
       * <Button variant="primary" onClick={handleClick}>Click me</Button>
       */
      export interface ButtonProps {
        /** Visual style variant */
        variant?: 'primary' | 'secondary' | 'danger';
        /** Click handler */
        onClick?: () => void;
        /** Button content */
        children: ReactNode;
        /** Disable interactions */
        disabled?: boolean;
      }

      export const Button: FC<ButtonProps> = ({
        variant = 'primary',
        disabled = false,
        onClick,
        children,
      }) => {
        return (
          <button
            className={`btn btn-${variant}`}
            disabled={disabled}
            onClick={onClick}
            aria-disabled={disabled}
          >
            {children}
          </button>
        );
      };
      ```

    **2. ComponentName.stories.tsx - Storybook File with Tests**:
    - Create stories for all component variants
    - Configure interactive controls for all props
    - Include interaction tests using play functions
    - Test all behaviors, interactions, and accessibility
    - Enable autodocs and proper meta configuration
    - Example structure:
      ```typescript
      import type { Meta, StoryObj } from '@storybook/react';
      import { within, userEvent, waitFor } from '@storybook/testing-library';
      import { expect } from '@storybook/jest';
      import { Button } from './Button';

      const meta = {
        title: 'Components/UI/Button',
        component: Button,
        parameters: { layout: 'centered' },
        tags: ['autodocs'],
        argTypes: {
          variant: {
            control: 'select',
            options: ['primary', 'secondary', 'danger'],
            description: 'Visual style variant',
          },
          disabled: {
            control: 'boolean',
            description: 'Disable button interaction',
          },
        },
      } satisfies Meta<typeof Button>;

      export default meta;
      type Story = StoryObj<typeof meta>;

      // Basic story
      export const Primary: Story = {
        args: {
          variant: 'primary',
          children: 'Click me',
        },
      };

      // Story with interaction tests
      export const Interactive: Story = {
        args: {
          children: 'Interactive Button',
          onClick: () => console.log('clicked'),
        },
        play: async ({ canvasElement, args }) => {
          const canvas = within(canvasElement);
          const button = canvas.getByRole('button');
          
          // Test button is rendered
          await expect(button).toBeInTheDocument();
          
          // Test click interaction
          await userEvent.click(button);
          
          // Test accessibility
          await expect(button).toHaveAccessibleName('Interactive Button');
        },
      };

      // Test disabled state
      export const Disabled: Story = {
        args: {
          disabled: true,
          children: 'Disabled',
        },
        play: async ({ canvasElement }) => {
          const canvas = within(canvasElement);
          const button = canvas.getByRole('button');
          
          // Test disabled state
          await expect(button).toBeDisabled();
          await expect(button).toHaveAttribute('aria-disabled', 'true');
        },
      };
      ```

    **Steps**

    1. Read requirements for all assigned components (1-5 components max)
    2. For each component, create BOTH required files:
       a. Implementation file (.tsx) with full functionality
       b. Storybook file (.stories.tsx) with documentation AND interaction tests
    3. Ensure consistency across all files for each component
    4. Apply all coding standards to every file created
    5. Test each component thoroughly using play functions in stories
    6. Validate TypeScript compilation for all files
    7. Verify comprehensive test coverage through story interactions

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of all components created with their files
    - Standards compliance verification for all files
    - Test coverage percentage for each component
    - TypeScript compilation status for all files
    - Accessibility compliance for each component

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Created [N] complete component(s) with all files'
    modifications: ['components/Component1.tsx', 'components/Component1.stories.tsx', ...]
    outputs:
      components_created: ['Component1', 'Component2', ...] # up to 5
      files_per_component:
        Component1: ['.tsx', '.stories.tsx']
        Component2: ['.tsx', '.stories.tsx']
      interaction_tests:
        Component1: 'N tests in stories'
        Component2: 'N tests in stories'
      typescript_compilation: pass|fail
      accessibility_compliant: true|false
      stories_count: N  # total across all components
      all_standards_met: true|false
    issues: []  # only if problems encountered
    ```
<<<
```

#### Phase 3: Review (Subagents)

In a single message, you spin up review subagents to check quality, up to **3** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

```
>>>
**ultrathink: adopt the Quality Assurance Lead mindset**

    - You're a **Quality Assurance Lead** with expertise in React component quality review who follows these principles:
      - **Comprehensive Testing**: Review all functionality and edge cases
      - **Standards Compliance**: Ensure strict adherence to all coding standards
      - **Integration Review**: Confirm all files work together properly
      - **Quality Gates**: Block deployment if any critical issues exist

    **Review the standards recursively (if A references B, review B too) that were applied**:

    - constitutions/standards/coding/frontend/react-components.md - Verify React patterns and structure
    - constitutions/standards/coding/frontend/accessibility.md - Check WCAG compliance implementation
    - constitutions/standards/coding/testing.md - Validate test coverage and quality
    - constitutions/standards/coding/typescript.md - Confirm type safety and exports
    - constitutions/standards/coding/documentation.md - Review documentation completeness

    **Review Assignment**
    You're assigned to review the following complete components created by subagents:

    - Component batch 1: [List of up to 5 components with all their files]
    - Component batch 2: [Additional components if applicable]
    - Each component includes:
      * ComponentName.tsx: Implementation with accessibility
      * ComponentName.stories.tsx: Storybook documentation with interaction tests

    **Review Steps**

    1. Read all files for each created component
    2. Review TypeScript compilation passes for all components
    3. Check ESLint compliance across all files
    4. Validate test coverage through story interaction tests
    5. Confirm accessibility compliance for all components
    6. Review Storybook stories and play functions work correctly
    7. Test that each component has both required files (.tsx and .stories.tsx)
    8. Validate consistency within each component's file set

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Quality and standards compliance for all components
    - Interaction test coverage in stories for each component
    - Storybook functionality and play function execution
    - File completeness (both files per component)
    - Cross-component consistency and integration

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Component quality review results'
    checks:
      typescript_compilation: pass|fail
      eslint_compliance: pass|fail
      story_interaction_tests: pass|fail
      accessibility_wcag_aa: pass|fail
      storybook_functionality: pass|fail
      file_naming_conventions: pass|fail
      component_exports: pass|fail
      documentation_complete: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
<<<
```

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution from all subagents + review)
2. **Apply decision criteria**:
   - All components created with complete file sets (2 files each)
   - TypeScript compilation passes for all components
   - Interaction tests in stories cover all behaviors
   - Accessibility compliance verified for all components
   - Storybook stories and play functions work correctly
3. **Select next action**:
   - **PROCEED**: All components complete with quality → Workflow success
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **RETRY**: Specific component failures → Re-execute failed components
   - **ROLLBACK**: Systemic failures → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat|| → Review and fix fundamental issues
4. **Decision Loop Management**: In phase 4, you(the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues
5. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all items as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
6. **Prepare transition**: Package final outputs for workflow completion

### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: build-component
status: completed
outputs:
  components_implemented:
    - name: 'ComponentName'
      files: ['components/ComponentName.tsx', 'components/ComponentName.stories.tsx']
      typescript_compliant: true
      accessibility_compliant: true
    - name: 'ComponentName2'
      files: ['components/ComponentName2.tsx', 'components/ComponentName2.stories.tsx']
      typescript_compliant: true
      accessibility_compliant: true
  storybook_stories:
    total_stories: 8
    interaction_tests: 12
    play_functions: working
    autodocs_enabled: true
  type_exports:
    - 'ComponentNameProps'
    - 'ComponentName2Props'
  documentation:
    jsdoc_complete: true
    usage_examples: included
  quality_verification:
    typescript_compilation: passed
    eslint_compliance: passed
    accessibility_wcag_aa: passed
    storybook_functionality: passed
total_components: 2
files_created: 4
summary: |
  Successfully created [N] production-ready React components with complete TypeScript
  implementation, Storybook stories with interaction tests, and full WCAG accessibility
  compliance. All components follow established patterns and standards.
```
