# Storybook Standards

_Standards for Storybook stories, organization, and documentation patterns_

## Story File Naming

### Standard Story Files

- **Component stories**: `ComponentName.stories.tsx`
- **Demo stories**: `ComponentName.demo.stories.tsx` for complex scenarios
- **Always use TypeScript** for story files

```plaintext
✅ Good:
Button.stories.tsx
UserCard.stories.tsx
PaymentFlow.demo.stories.tsx

❌ Bad:
button.stories.js         # Should be PascalCase and TypeScript
Button-stories.tsx        # Should use dot notation
ButtonStories.tsx         # Missing .stories suffix
```

## Story Title Convention

### Path-Based Naming

Story titles must reflect the component's location in the file structure:

```typescript
// ✅ Good: Path reflects file location
// File: components/forms/Button.stories.tsx
export default {
  title: 'Components/Forms/Button',
  component: Button,
} as Meta<typeof Button>;

// File: components/dashboard/widgets/UserCard.stories.tsx
export default {
  title: 'Components/Dashboard/Widgets/UserCard',
  component: UserCard,
} as Meta<typeof UserCard>;

// ❌ Bad: Flat structure loses context
export default {
  title: 'Button',  // Missing path context
  component: Button,
};
```

## Story Structure

### Basic Story Template

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Components/UI/Button', // Path-based naming
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger'],
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled',
  },
};
```

## Demo Stories

Use `.demo.stories.tsx` for complex multi-component scenarios:

```typescript
// PaymentFlow.demo.stories.tsx
const meta = {
  title: 'Demos/E-Commerce/PaymentFlow',
  parameters: { layout: 'fullscreen' },
};

export const CompleteCheckout: Story = {
  render: () => (
    <PaymentProvider>
      <OrderSummary {...orderProps} />
      <PaymentForm onSubmit={handlePayment} />
    </PaymentProvider>
  ),
};
```

## Organization Patterns

### Directory Structure

```plaintext
components/
  Button/
    Button.tsx
    Button.spec.tsx
    Button.stories.tsx
  Forms/
    PaymentForm/
      PaymentForm.tsx
      PaymentForm.spec.tsx
      PaymentForm.stories.tsx
      PaymentForm.demo.stories.tsx  # Complex scenarios
```

### Story Categories

- **Components**: `Components/Category/ComponentName`
- **Demos**: `Demos/Feature/ScenarioName`

## Story Best Practices

### Essential Stories

Every component should include:
- **Default** - Minimal required props
- **All variants** - Primary, Secondary, etc.
- **All states** - Disabled, Loading, Error
- **Edge cases** - Long text, empty state

### Interactive Stories

Use `play` function for interactions:

```typescript
export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const button = within(canvasElement).getByRole('button');
    await userEvent.click(button);
  },
};
```

## Documentation

Add component and story documentation via `parameters.docs.description`.


## Controls and Args

Common control types:
- `select` - Dropdown options
- `boolean` - Toggle switch
- `range` - Number slider
- `color` - Color picker
- `date` - Date picker
- `false` - Disable control


## Testing Integration

Reuse stories in tests with `composeStories`:

```typescript
import { composeStories } from '@storybook/react';
import * as stories from './Button.stories';

const { Primary } = composeStories(stories);
```

## Anti-Patterns to Avoid

- **No inline component definitions** in stories
- **No direct DOM manipulation**
- **No real API calls** - use mock data
- **No side effects** outside of play functions

## Summary

1. **Use path-based titles** that mirror directory structure
2. **Create `.demo.stories.tsx`** for complex multi-component scenarios
3. **Include all variants and states** in stories
4. **Document thoroughly** with descriptions and usage examples
5. **Use TypeScript** for type safety
6. **Organize stories** into logical categories
7. **Add interactive examples** with play functions
8. **Test accessibility** scenarios
9. **Mock external dependencies** instead of real calls
10. **Reuse stories** in component tests