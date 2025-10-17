# React Component Standards

_Standards for React component structure, patterns, and performance optimization_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- TypeScript Standards (plugin:coding:standard:typescript) - React components use TypeScript interfaces and typing throughout all examples
- Function Standards (plugin:coding:standard:functions) - React components are functions and component handlers are functions
- Testing Standards (plugin:coding:standard:testing) - Component test files and testing patterns are essential for quality
- Documentation Standards (plugin:coding:standard:documentation) - Components require proper JSDoc and interface documentation
- General Principles (plugin:coding:standard:general-principles) - Foundational coding principles that apply to all component code
- File Naming Standards (plugin:coding:standard:file-structure) - Specific component file naming patterns (Button.tsx, Button.spec.tsx)
- Accessibility Standards (standard:accessibility) - Frontend components must follow accessibility requirements

**Note**: This standard requires the coding plugin to be enabled for referenced coding standards.

## Core Principles

### Functional Components with TypeScript

Always use functional components with proper TypeScript interfaces for type safety and maintainability.

```typescript
// ✅ GOOD: proper component structure
export interface ButtonProps {
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  children: ReactNode;
}

export const Button: FC<ButtonProps> = ({ variant = 'primary', ...props }) => {
  return <button className={variant} {...props} />;
};

// ❌ BAD: missing interface export, class component
class BadButton extends Component {
  render() { return <button>...</button>; }
}
```

### Single Responsibility

Components still follow the Single Responsibility principle from the general coding standards, but express it with UI intent: move data-fetching or orchestration into hooks/utilities and keep renders focused.

```typescript
// ✅ GOOD: focused component
export const UserProfile: FC<Props> = ({ user }) => {
  return (
    <div>
      <UserAvatar user={user} />
      <UserInfo user={user} />
      ...
    </div>
  );
};

// ❌ BAD: monolithic component handling multiple concerns
export const UserEverything: FC<Props> = ({ user }) => {
  // 200+ lines of mixed logic
};
```

### Performance Optimization

Use memoization strategically for expensive operations and stable references.

```typescript
// ✅ GOOD: memoize expensive calculations
export const ExpensiveList = memo(({ items }: Props) => {
  const sortedItems = useMemo(() => 
    items.sort((a, b) => b.timestamp - a.timestamp), [items]
  );
  
  const handleClick = useCallback((id: string) => {
    updateItem(id);
  }, [updateItem]);
  
  return <div>{sortedItems.map(item => <Item key={item.id} ... />)}</div>;
});

// ❌ BAD: creating objects in render
export const BadComponent = ({ user }) => {
  return (
    <UserProfile
      style={{ margin: 10 }} // new object every render
      options={{ showEmail: true }} // new object every render
    />
  );
};
```

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

## Anti-Patterns

### Class Components

```typescript
// ❌ BAD: class components (except Error Boundaries)
class BadButton extends Component {
  render() { return <button>...</button>; }
}

// ✅ GOOD: functional components
export const Button: FC<Props> = ({ children }) => {
  return <button>{children}</button>;
};
```

### Missing Interface Exports

```typescript
// ❌ BAD: inline props type, not exported
const BadButton = ({ onClick }: { onClick: () => void }) => {
  return <button onClick={onClick}>...</button>;
};

// ✅ GOOD: exported interface
export interface ButtonProps {
  onClick?: () => void;
}

export const Button: FC<ButtonProps> = ({ onClick }) => {
  return <button onClick={onClick}>...</button>;
};
```

### Common Mistakes to Avoid

1. **Creating objects in render**
   - Problem: Causes unnecessary re-renders
   - Solution: Define objects outside component or use useMemo
   - Example: `const style = { margin: 10 }` outside component

2. **Deep prop drilling**
   - Problem: Maintenance nightmare, unclear data flow
   - Solution: Use Context API for deeply nested props

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
