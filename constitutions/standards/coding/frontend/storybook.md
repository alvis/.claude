# Storybook Standards

_Standards for Storybook stories, organization, and documentation patterns_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- [React Components Standards](@../react-components.md) - Storybook documents React components and requires understanding component implementation patterns
- [Documentation Standards](@../../documentation.md) - Storybook stories serve as living documentation and must follow documentation principles
- [TypeScript Standards](@../../typescript.md) - All story examples use TypeScript patterns and type definitions
- [General Principles](@../../general-principles.md) - Story code must follow foundational coding principles and best practices

## Core Principles

### File Naming Convention

Use consistent TypeScript naming for all story files.

```plaintext
✅ GOOD: descriptive TypeScript story files
Button.stories.tsx
UserCard.stories.tsx
PaymentFlow.demo.stories.tsx    # Complex scenarios

❌ BAD: inconsistent naming
button.stories.js               # Should be PascalCase + TS
Button-stories.tsx              # Should use dot notation
ButtonStories.tsx               # Missing .stories suffix
```

### Path-Based Organization

Story titles must reflect component file structure for clear navigation.

```typescript
// ✅ GOOD: path reflects file location
// File: components/forms/Button.stories.tsx
export default {
  title: 'Components/Forms/Button',
  component: Button,
} as Meta<typeof Button>;

// ❌ BAD: flat structure loses context
export default {
  title: 'Button',  // missing path context
  component: Button,
};
```

### Complete Story Coverage

Include all component states and variants for comprehensive documentation.

```typescript
// ✅ GOOD: covers all important states
export const Primary: Story = { args: { variant: 'primary' } };
export const Secondary: Story = { args: { variant: 'secondary' } };
export const Disabled: Story = { args: { disabled: true } };
export const Loading: Story = { args: { loading: true } };
export const WithLongText: Story = { args: { children: 'Very long button text...' } };

// ❌ BAD: only basic state
export const Default: Story = {};
```

## Story Implementation

### Standard Story Structure

```typescript
// complete story template with all recommended features
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Components/UI/Button',
  component: Button,
  tags: ['autodocs'],
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// essential stories
export const Primary: Story = {
  args: { variant: 'primary', children: 'Click me' },
};

export const Disabled: Story = {
  args: { disabled: true, children: 'Disabled' },
};

export const WithClick: Story = {
  args: {
    children: 'Interactive',
    onClick: () => console.log('clicked'),
  },
};
```

### Demo Stories for Complex Scenarios

```typescript
// PaymentFlow.demo.stories.tsx - complex multi-component scenarios
const meta = {
  title: 'Demos/E-Commerce/PaymentFlow',
  parameters: { layout: 'fullscreen' },
};

export const CompleteCheckout: Story = {
  render: () => (
    <PaymentProvider>
      <OrderSummary {...orderProps} />
      <PaymentForm onSubmit={handlePayment} />
      ...
    </PaymentProvider>
  ),
};
```

## Organization Structure

### Directory Alignment

```plaintext
components/
  Button/
    Button.tsx
    Button.spec.tsx
    Button.stories.tsx
  Forms/
    PaymentForm/
      PaymentForm.tsx
      PaymentForm.stories.tsx
      PaymentForm.demo.stories.tsx  # Complex scenarios only
```

## Interactive Stories

### Testing User Interactions

```typescript
// ✅ GOOD: interactive story with play function
export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await userEvent.click(button);
    ...
  },
};

// ✅ GOOD: form interaction story
export const FormInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByLabelText('Email');
    await userEvent.type(input, 'test@example.com');
    await userEvent.click(canvas.getByRole('button', { name: 'Submit' }));
  },
};
```

## Controls and Documentation

### Control Configuration

```typescript
// ✅ GOOD: comprehensive control setup
const meta = {
  title: 'Components/UI/Button',
  component: Button,
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger'],
      description: 'Visual style variant',
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
    },
    disabled: {
      control: 'boolean',
      description: 'Disable button interaction',
    },
    onClick: { control: false }, // disable control for functions
  },
  parameters: {
    docs: {
      description: {
        component: 'Primary button component for user actions',
      },
    },
  },
};
```

## Quick Reference

| Story Type | File Name | Title Pattern | Use Case |
|------------|-----------|---------------|----------|
| Component | `Button.stories.tsx` | `Components/UI/Button` | Basic component docs |
| Demo | `Flow.demo.stories.tsx` | `Demos/Feature/Flow` | Multi-component scenarios |
| Interactive | Any story file | N/A | User interaction testing |
| Controls | Any story file | N/A | Prop exploration |

| Control Type | Use Case | Example |
|--------------|----------|---------|
| `select` | Dropdown options | `options: ['sm', 'md', 'lg']` |
| `boolean` | Toggle switch | `control: 'boolean'` |
| `range` | Number slider | `{ min: 0, max: 100 }` |
| `color` | Color picker | `control: 'color'` |
| `false` | Disable control | Functions, complex objects |

## Patterns & Best Practices

### Complete Component Story Pattern

**Purpose:** Document all component states and variants comprehensively

**When to use:**

- Every component needs Storybook documentation
- Component has multiple variants or states
- Props need interactive exploration

**Implementation:**

```typescript
// pattern template
import type { Meta, StoryObj } from '@storybook/react';
import { ComponentName } from './ComponentName';

const meta = {
  title: 'Components/Category/ComponentName',
  component: ComponentName,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary'] },
    disabled: { control: 'boolean' },
  },
} satisfies Meta<typeof ComponentName>;

export default meta;
type Story = StoryObj<typeof meta>;

// cover all important states
export const Default: Story = {};
export const AllVariants: Story = { args: { variant: 'secondary' } };
export const DisabledState: Story = { args: { disabled: true } };
export const EdgeCase: Story = { args: { children: 'Very long text content...' } };
```

### Common Patterns

1. **Story Composition** - Reuse stories in tests

   ```typescript
   import { composeStories } from '@storybook/react';
   import * as stories from './Button.stories';
   const { Primary } = composeStories(stories);
   ```

2. **Decorator Usage** - Add context providers

   ```typescript
   export default {
     decorators: [
       (Story) => (
         <ThemeProvider theme={defaultTheme}>
           <Story />
         </ThemeProvider>
       ),
     ],
   };
   ```

## Anti-Patterns

### Inline Component Definitions

```typescript
// ❌ BAD: defining components in stories
export const BadStory: Story = {
  render: () => {
    const InlineComponent = ({ text }) => <div>{text}</div>;
    return <InlineComponent text="Bad practice" />;
  },
};

// ✅ GOOD: use existing components
export const GoodStory: Story = {
  render: () => <ExistingComponent text="Good practice" />,
};
```

### Real API Calls in Stories

```typescript
// ❌ BAD: real API calls in stories
export const BadData: Story = {
  render: () => {
    const [data, setData] = useState(null);
    useEffect(() => {
      fetch('/api/data').then(setData); // Real API call
    }, []);
    return <Component data={data} />;
  },
};

// ✅ GOOD: mock data in stories
export const GoodData: Story = {
  args: {
    data: mockData, // Predefined mock data
  },
};
```

### Common Mistakes to Avoid

1. **Missing story variants**
   - Problem: Incomplete documentation of component capabilities
   - Solution: Include all states (default, disabled, loading, error)
   - Example: Create separate stories for each variant

2. **Poor story organization**
   - Problem: Stories scattered without logical grouping
   - Solution: Use path-based titles that mirror file structure

## Quick Decision Tree

1. **What type of story is needed?**
   - If single component → Use `Component.stories.tsx`
   - If multi-component scenario → Use `Flow.demo.stories.tsx`
   - If interaction testing → Add `play` functions

2. **How complex is the component?**
   - If simple → Include all variants in one file
   - If complex → Consider separate demo stories
   - If many states → Use comprehensive argTypes

3. **Does it need context?**
   - If providers needed → Use decorators
   - If mock data → Define in story args
   - If interactions → Use play functions

