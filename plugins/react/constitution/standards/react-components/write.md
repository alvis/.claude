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

## Quick Reference

| Pattern | Use Case | Example | Notes |
|---------|----------|---------|-------|
| FC<Props> | All components | `const Button: FC<Props> = ...` | Always export interface |
| memo() | Expensive renders | `memo(({ items }) => ...)` | Use sparingly |
| useMemo | Heavy calculations | `useMemo(() => sort(items), [items])` | Memoize expensive ops |
| useCallback | Stable handlers | `useCallback((id) => update(id), [])` | Prevent child re-renders |
| Context | Deep props | `<Provider value={data}>` | Split contexts for performance |

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
