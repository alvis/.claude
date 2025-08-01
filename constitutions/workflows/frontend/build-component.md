# Build React Component

**Purpose**: Complete workflow for building React components with tests, stories, and accessibility
**When to use**: Creating new React components from scratch
**Prerequisites**: React development environment set up, project structure understood

## Steps

### 1. Plan Component

Define the component's purpose and interface:

- Identify the component's single responsibility
- Design the props interface with TypeScript
- Consider accessibility requirements from the start
- Plan for different variants/states
- Identify reusable patterns from existing components

### 2. Create Files

Set up the component file structure:

```bash
# Create component files
touch components/ComponentName.tsx
touch components/ComponentName.spec.tsx
touch components/ComponentName.stories.tsx
```

File organization:

```plaintext
components/
├── ComponentName.tsx          # Main component
├── ComponentName.spec.tsx     # Tests with 'rc:' prefix
└── ComponentName.stories.tsx  # Storybook stories
```

### 3. Build Component

Implement the component following standards:

```typescript
// ✅ ALWAYS export the props interface
export interface ComponentNameProps {
  /** Component variant */
  variant?: 'primary' | 'secondary';
  /** Click handler */
  onClick?: () => void;
  /** Accessible label for screen readers */
  'aria-label'?: string;
  /** Whether component is disabled */
  disabled?: boolean;
  children: ReactNode;
}

// ✅ ALWAYS use arrow functions with FC type
export const ComponentName: FC<ComponentNameProps> = ({
  variant = 'primary',
  onClick,
  'aria-label': ariaLabel,
  disabled = false,
  children
}) => {
  return (
    <button
      className={variant}
      onClick={onClick}
      aria-label={ariaLabel}
      disabled={disabled}
      type="button"
    >
      {children}
    </button>
  );
};
```

### 4. Write Tests

Create comprehensive test coverage:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ComponentName } from './ComponentName';

describe('rc:ComponentName', () => {
  it('should render with correct content', () => {
    const expected = 'Test content';

    render(<ComponentName>{expected}</ComponentName>);

    expect(screen.getByRole('button')).toHaveTextContent(expected);
  });

  it('should call onClick when clicked', () => {
    const mockClick = vi.fn();

    render(<ComponentName onClick={mockClick}>Click</ComponentName>);
    fireEvent.click(screen.getByRole('button'));

    expect(mockClick).toHaveBeenCalledOnce();
  });

  it('should apply accessibility attributes', () => {
    const ariaLabel = 'Custom label';

    render(<ComponentName aria-label={ariaLabel}>Button</ComponentName>);

    expect(screen.getByRole('button')).toHaveAttribute('aria-label', ariaLabel);
  });
});
```

### 5. Create Stories

Build Storybook stories for documentation:

```typescript
import type { Meta, StoryObj } from "@storybook/react";
import { ComponentName } from "./ComponentName";

const meta: Meta<typeof ComponentName> = {
  title: "Components/ComponentName",
  component: ComponentName,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: { type: "select" },
      options: ["primary", "secondary"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: "primary",
    children: "Primary Button",
  },
};

export const Secondary: Story = {
  args: {
    variant: "secondary",
    children: "Secondary Button",
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    children: "Disabled Button",
  },
};
```

### 6. Review Accessibility

Verify WCAG compliance and screen reader support:

✅ **Accessibility Checklist:**

- [ ] Semantic HTML elements used
- [ ] Proper ARIA attributes included
- [ ] Keyboard navigation works
- [ ] Focus management implemented
- [ ] Color contrast meets WCAG AA standards
- [ ] Screen reader announcements are clear
- [ ] Form labels properly associated (if applicable)

### 7. Optimize Performance

Add memoization if needed:

```typescript
// Use React.memo for expensive components
export const ExpensiveComponent = memo(({ items }: Props) => {
  return items.map(item => <Item key={item.id} {...item} />);
});

// Use useMemo for expensive calculations
const sortedItems = useMemo(() =>
  items.sort((a, b) => b.score - a.score),
  [items]
);

// Use useCallback for stable event handlers
const handleClick = useCallback((id: string) => {
  updateItem(id);
}, [updateItem]);
```

## Standards to Follow

- [React Component Standards](../../standards/frontend/react-components.md)
- [React Hooks Standards](../../standards/frontend/react-hooks.md)
- [Accessibility Standards](../../standards/frontend/accessibility.md)
- [Testing Standards](../../standards/quality/testing.md)

## Quality Gates

**Required before component completion:**

```bash
# All must pass
npm run typecheck     # TypeScript compilation
npm run lint         # ESLint validation
npm run coverage         # Component tests pass
```

## Common Issues

- **Missing props interface export**: Always export props interface for reusability
- **No accessibility considerations**: Plan for ARIA attributes from the start
- **Missing test cases**: Test all interactive behaviors and edge cases
- **Performance issues**: Only add memoization when performance bottlenecks identified
- **Complex components**: Break down into smaller, focused components
- **Missing stories**: Every component variant should have a Storybook story

## Component Template Reference

See [Component Template](../../patterns/frontend/component-template.md) for the complete boilerplate code.
