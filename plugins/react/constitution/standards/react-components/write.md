# React Components: Compliant Patterns

> **Prerequisite**: Read `meta.md` in this directory first for dependencies and rule groups.
> **Compliance**: Also follow `scan.md` in this directory to avoid violations during writing. When unsure about a specific rule, consult its detailed guidance in `rules/<rule-id>.md`.

## File Organization

### Naming Conventions

```plaintext
✅ GOOD:
Button.tsx              # PascalCase components
useScroll.ts            # camelCase hooks
Button.spec.tsx         # Test files
Button.stories.tsx      # Story files

❌ BAD:
browser.tsx             # Should be Browser.tsx
UseScroll.ts            # Should be useScroll.ts
```

### Directory Structure

```plaintext
components/
├── Button.tsx          # Implementation
├── Button.spec.tsx     # Tests with 'rc:' prefix
└── Button.stories.tsx  # Storybook stories
```

## Component Architecture

### Props Design

Keep props simple, predictable, and well-typed.

```typescript
// ✅ GOOD: simple, focused props
export interface AlertProps {
  variant: "success" | "warning" | "error";
  message: string;
  onDismiss?: () => void;
}

// ❌ BAD: complex nested structure
export interface BadProps {
  config: {
    display: { variant: string; theme: object; };
    behavior: { dismissible: boolean; callbacks: object; };
  };
}
```

### Component Composition

Favor composition over complex prop configurations.

```typescript
// ✅ GOOD: composable structure
<Card>
  <Card.Header>
    <Card.Title>Profile</Card.Title>
  </Card.Header>
  <Card.Body>
    <UserInfo user={user} />
  </Card.Body>
</Card>

// ❌ BAD: too many props
<UserCard
  title="Profile"
  showHeader={true}
  headerStyle="primary"
  user={user}
  ...
/>
```

## State Management

### State Placement

Keep state close to where it's used and lift up only when necessary.

```typescript
// ✅ GOOD: local state for local concerns
export const TodoItem: FC<Props> = ({ todo, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div>
      {isEditing ? <TodoEditForm ... /> : <TodoDisplay ... />}
    </div>
  );
};

// ✅ GOOD: context for deep prop drilling
const UserContext = createContext<User | null>(null);

export const UserProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
};
```

## Framework Integration

### Next.js Patterns

```typescript
// ✅ GOOD: dynamic imports for performance
const HeavyChart = dynamic(() => import('#components/Chart'), {
  loading: () => <Skeleton />,
  ssr: false,
});

// ✅ GOOD: optimized images
<Image
  src="/hero.jpg"
  alt="Description"
  width={1200}
  height={600}
  priority
/>
```

## Documentation

Every exported component is documented via a co-located Storybook story file. The kind of story file depends on whether the scenario involves a single component or a composition. This section enforces _coverage_; refer to `standard:storybook` for story _content_ rules (titles, args, autodocs, coverage of variants, play functions).

### `.stories.tsx` (Always Required)

Every exported component ships a `<Name>.stories.tsx` documenting:

- Basic states (default, disabled, loading, error)
- Props matrix (each variant of `variant`, `size`, etc.)
- Edge cases of _that component in isolation_ (long text, empty content, async-pending)

```typescript
// components/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
} satisfies Meta<typeof Button>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = { args: { variant: 'primary', children: 'Save' } };
export const Disabled: Story = { args: { disabled: true, children: 'Save' } };
export const Loading: Story = { args: { loading: true, children: 'Saving…' } };
```

### `.demo.stories.tsx` (Multi-Component Scenarios)

When a component participates in a composition with siblings, slots, or controlled-uncontrolled coordination, additionally ship a `<Name>.demo.stories.tsx` showing the integration as it appears in production:

- Composition with siblings (`<Form><Field/><Submit/></Form>`)
- Slot patterns (`<Card.Header/>` + `<Card.Body/>`)
- Controlled-uncontrolled coordination (parent state driving multiple children)
- Form-with-validation flows (field + error + submit + toast)

```typescript
// components/Form.demo.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Form } from './Form';
import { TextField } from '../TextField';
import { SubmitButton } from '../SubmitButton';

const meta = {
  title: 'Components/Form/Demo',
  component: Form,
  tags: ['autodocs'],
} satisfies Meta<typeof Form>;
export default meta;
type Story = StoryObj<typeof meta>;

export const WithValidation: Story = {
  render: () => (
    <Form onSubmit={() => {}}>
      <TextField name="email" required />
      <SubmitButton>Send</SubmitButton>
    </Form>
  ),
};
```

### Decision Rule

If your story only renders `<MyComponent>`, it's `.stories.tsx`. If your story renders `<MyComponent>` + `<OtherComponent>` to demonstrate composition, it's `.demo.stories.tsx`.

### File-Tree Examples

```plaintext
✅ GOOD: simple component — one story file
components/
├── Button.tsx
├── Button.stories.tsx
└── Button.spec.tsx

✅ GOOD: composition component — story + demo
components/
├── Form.tsx
├── Form.stories.tsx          # Form rendered alone (empty, with one field, etc.)
├── Form.demo.stories.tsx     # Form composed with TextField + SubmitButton
└── Form.spec.tsx

❌ BAD: exported component, no story
components/
└── Button.tsx                # missing Button.stories.tsx

❌ BAD: composition demo placed inside the basic story
components/
├── Form.tsx
└── Form.stories.tsx          # contains <Form><TextField/></Form> — should be .demo.stories.tsx
```

## Quick Reference

| Pattern | Use Case | Example | Notes |
|---------|----------|---------|-------|
| FC<Props> | All components | `const Button: FC<Props> = ...` | Always export interface |
| memo() | Expensive renders | `memo(({ items }) => ...)` | Use sparingly |
| useMemo | Heavy calculations | `useMemo(() => sort(items), [items])` | Memoize expensive ops |
| useCallback | Stable handlers | `useCallback((id) => update(id), [])` | Prevent child re-renders |
| Context | Deep props | `<Provider value={data}>` | Split contexts for performance |
| Storybook coverage | All exported components | `<Name>.stories.tsx` required; `<Name>.demo.stories.tsx` for multi-component scenarios | `RC-DOC-01` |

## Patterns & Best Practices

### Component Template Pattern

**Purpose**: Standardized component structure with TypeScript safety

**When to use**:

- Every new component
- Refactoring existing components

**Implementation**:

```typescript
// pattern template
export interface ComponentProps {
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  children: ReactNode;
}

export const Component: FC<ComponentProps> = ({
  variant = 'primary',
  ...props
}) => {
  return <element className={variant} {...props} />;
};
```

## Quick Decision Tree

1. **Need to share state between components?**
   - If siblings → Lift state to common parent
   - If deep nesting → Use Context
   - Otherwise → Keep local

2. **Component rendering slowly?**
   - If expensive calculations → Use useMemo
   - If expensive component → Use memo
   - If unstable callbacks → Use useCallback
   - Otherwise → Profile first

3. **Need complex interactions?**
   - If form-like → Use useReducer
   - If simple state → Use useState
   - If external state → Use custom hook
