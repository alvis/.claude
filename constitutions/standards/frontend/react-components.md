# React Component Standards

_Standards for React component structure, patterns, and performance optimization_

## Component Structure Requirements

### Critical Component Rules

- **ALWAYS use arrow functions with `FC` type** - Use `FC` for functional components with typed props
- **NO class components** (except Error Boundaries)
- **ALWAYS export props interface for every component** (required for type safety and documentation)
- **Keep components small and focused** (single responsibility principle)
- **Follow accessibility standards (WCAG)**
- **Optimize performance with memoization when needed**
- **Implement functional components and hooks exclusively** - Avoid class components

### Component Template

```typescript
// ✅ ALWAYS export the props interface
export interface ButtonProps {
  /** Button variant */
  variant?: 'primary' | 'secondary';
  /** Click handler */
  onClick?: () => void;
  /** Accessible label for screen readers */
  'aria-label'?: string;
  /** Whether button is disabled */
  disabled?: boolean;
  children: ReactNode;
}

// ✅ ALWAYS use arrow functions with FC type
export const Button: FC<ButtonProps> = ({
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

## File Organization

### Naming Conventions

- **Component files**: Name in `PascalCase`, e.g. ✅ `Browser.tsx` ❌ `browser.tsx`
- **Hook files**: Remain in `camelCase`, e.g. ✅ `useScroll.ts` ❌ `UseScroll.ts`
- **Test files**: `Component.spec.tsx` or `Component.spec.ts`
- **Story files**: 
  - `ComponentName.stories.tsx` for basic component stories
  - `ComponentName.demo.stories.tsx` for complex scenarios involving multiple components

### Directory Structure

```plaintext
components/
├── Button.tsx          # Component implementation
├── Button.spec.tsx     # Tests (use 'rc:' prefix)
└── Button.stories.tsx  # Storybook documentation
```

## Storybook Standards

### Story Naming Convention

Use the component's path and name for the story title:

```typescript
// ✅ Good: Path-based naming for stories
// components/forms/Button.stories.tsx
export default {
  title: "Components/Forms/Button",
  component: Button,
} as Meta<typeof Button>;

// components/dashboard/UserCard.stories.tsx
export default {
  title: "Components/Dashboard/UserCard",
  component: UserCard,
} as Meta<typeof UserCard>;

// ❌ Bad: Flat naming structure
export default {
  title: "Button", // Missing path context
  component: Button,
};
```

### Story Organization

```typescript
// ✅ Good: Complete story structure
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta = {
  title: "Components/UI/Button",
  component: Button,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger"],
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// Primary story
export const Primary: Story = {
  args: {
    variant: "primary",
    children: "Click me",
  },
};

// Additional variants
export const Secondary: Story = {
  args: {
    variant: "secondary",
    children: "Click me",
  },
};

// Interactive states
export const Disabled: Story = {
  args: {
    disabled: true,
    children: "Disabled",
  },
};

// With actions
export const WithClick: Story = {
  args: {
    children: "Click me",
    onClick: () => console.log("clicked"),
  },
};
```

### Story Best Practices

- **Mirror directory structure** in story titles
- **Include all component states** (default, hover, active, disabled)
- **Document props** with controls and descriptions
- **Add interaction tests** for user flows
- **Use decorators** for context providers
- **Include accessibility** scenarios

## Component Design Patterns

### Single Responsibility Principle

- One component should handle one task
- Extract complex logic into custom hooks
- Break down large components into smaller, focused ones

```typescript
// ✅ Good: Focused components
export const UserProfile: FC<UserProfileProps> = ({ user }) => {
  return (
    <div>
      <UserAvatar user={user} />
      <UserInfo user={user} />
      <UserActions user={user} />
    </div>
  );
};

// ❌ Bad: Monolithic component
export const UserEverything: FC<Props> = ({ user }) => {
  // 200+ lines of mixed avatar, info, and action logic
};
```

### Props Design

- **Always define and export props interface**
- Keep props simple and minimal
- Avoid passing down complex structures
- Use discriminated unions for variant props

```typescript
// ✅ Good: Simple, focused props
export interface AlertProps {
  variant: "success" | "warning" | "error";
  message: string;
  onDismiss?: () => void;
}

// ❌ Bad: Complex props structure
export interface BadAlertProps {
  config: {
    display: {
      variant: string;
      theme: object;
      styling: unknown;
    };
    behavior: {
      dismissible: boolean;
      autoHide: boolean;
      callbacks: object;
    };
  };
}
```

### Component Composition

```typescript
// ✅ Good: Composable components
<Card>
  <Card.Header>
    <Card.Title>User Profile</Card.Title>
  </Card.Header>
  <Card.Body>
    <UserInfo user={user} />
  </Card.Body>
</Card>

// ❌ Avoid: Monolithic components with many props
<UserCard
  title="User Profile"
  showHeader={true}
  headerStyle="primary"
  user={user}
  bodyStyle="compact"
/>
```

## State Management

### State Placement

- Keep state close to where it's used
- Lift state up only when necessary
- Use Context API for deeply nested props
- Maintain single source of truth

```typescript
// ✅ Good: Local state for local concerns
export const TodoItem: FC<TodoItemProps> = ({ todo, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div>
      {isEditing ? (
        <TodoEditForm todo={todo} onSave={onUpdate} />
      ) : (
        <TodoDisplay todo={todo} onEdit={() => setIsEditing(true)} />
      )}
    </div>
  );
};
```

### Context Usage

```typescript
// ✅ Good: Split contexts for performance
const UserContext = createContext<User | null>(null);
const ThemeContext = createContext<Theme>('light');

// ✅ Good: Context with provider pattern
export const UserProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  return (
    <UserContext.Provider value={user}>
      {children}
    </UserContext.Provider>
  );
};
```

## Performance Optimization

### When to Use Memoization

- Use `React.memo` for components with expensive renders
- Use `useMemo` for expensive calculations
- Use `useCallback` for stable event handlers
- Avoid creating objects/functions in render

```typescript
// ✅ Good: Memoize expensive components
export const ExpensiveList = memo(({ items }: Props) => {
  return items.map(item => <Item key={item.id} {...item} />);
});

// ✅ Good: Memoize calculations
const UserProfile: FC<Props> = ({ user, activities }) => {
  const sortedActivities = useMemo(() =>
    activities.sort((a, b) => b.timestamp - a.timestamp),
    [activities]
  );

  const handleActivityClick = useCallback((id: string) => {
    updateActivity(id);
  }, [updateActivity]);

  return (
    <div>
      {sortedActivities.map(activity => (
        <Activity
          key={activity.id}
          activity={activity}
          onClick={handleActivityClick}
        />
      ))}
    </div>
  );
};
```

### Performance Anti-Patterns

```typescript
// ❌ Bad: Creating objects in render
const BadComponent: FC<Props> = ({ user }) => {
  return (
    <UserProfile
      user={user}
      style={{ margin: 10, padding: 5 }} // New object every render
      options={{ showEmail: true }}       // New object every render
    />
  );
};

// ✅ Good: Define objects outside render
const profileStyle = { margin: 10, padding: 5 };
const profileOptions = { showEmail: true };

const GoodComponent: FC<Props> = ({ user }) => {
  return (
    <UserProfile
      user={user}
      style={profileStyle}
      options={profileOptions}
    />
  );
};
```

## Next.js Integration

### Dynamic Imports

```typescript
// ✅ Good: Lazy load heavy components
const HeavyChart = dynamic(() => import('#components/Chart'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

### Image Optimization

```typescript
// ✅ Good: Optimized images
<Image
  src="/hero.jpg"
  alt="Hero image description"
  width={1200}
  height={600}
  priority // For above fold images
  placeholder="blur"
/>
```

### Server vs Client Components

```typescript
// ✅ Good: Server Component by default
export const ServerUserList: FC<Props> = async ({ userId }) => {
  const users = await fetchUsers();

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
};

// ✅ Good: Client Component when needed
'use client';

export const InteractiveUserList: FC<Props> = ({ initialUsers }) => {
  const [users, setUsers] = useState(initialUsers);
  const [filter, setFilter] = useState('');

  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter users..."
      />
      {/* Interactive content */}
    </div>
  );
};
```

## Testing Requirements

### Test File Structure

```typescript
// ✅ Good: Use 'rc:' prefix for React component tests
describe('rc:Button', () => {
  it('should render with correct text', () => {
    const expected = 'Click me';

    render(<Button>{expected}</Button>);

    expect(screen.getByRole('button')).toHaveTextContent(expected);
  });

  it('should call onClick when clicked', () => {
    const mockClick = vi.fn();

    render(<Button onClick={mockClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));

    expect(mockClick).toHaveBeenCalledOnce();
  });
});
```

### What to Test

- **Component rendering** - Does it render correctly?
- **User interactions** - Do clicks, inputs work?
- **Props handling** - Are props applied correctly?
- **Conditional rendering** - Do different states show correctly?
- **Accessibility** - Are ARIA attributes present?

## Anti-Patterns to Avoid

### Common Component Mistakes

```typescript
// ❌ Bad: Class components (except Error Boundaries)
class BadButton extends Component {
  render() {
    return <button>{this.props.children}</button>;
  }
}

// ❌ Bad: Not exporting props interface
const BadButton = ({ onClick, children }: { onClick: () => void; children: ReactNode }) => {
  return <button onClick={onClick}>{children}</button>;
};

// ❌ Bad: Complex prop drilling
<ComponentA>
  <ComponentB data={data} theme={theme} config={config}>
    <ComponentC data={data} theme={theme} config={config} />
  </ComponentB>
</ComponentA>

// ✅ Good: Use Context for deeply nested props
<DataProvider value={data}>
  <ThemeProvider value={theme}>
    <ComponentA>
      <ComponentB>
        <ComponentC />
      </ComponentB>
    </ComponentA>
  </ThemeProvider>
</DataProvider>
```
