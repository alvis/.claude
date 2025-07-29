# React & Frontend Coding Standards

*Specific standards for React components, hooks, and frontend development*

## Table of Contents

- [Component Structure](#component_structure) `component_structure` - **workflow:** `build-component`
- [Component Patterns](#component_patterns) `component_patterns`
- [Performance Optimization](#performance_optimization) `performance_optimization`
- [Next.js Patterns](#nextjs_patterns) `nextjs_patterns`
- [Hooks Patterns](#hooks_patterns) `hooks_patterns`
- [Testing React](#testing_react) `testing_react`
- [Accessibility](#accessibility) `accessibility`
- [Storybook Standards](#storybook_standards) `storybook_standards`

<component_structure>

## ⚛️ React Component Standards

<workflow name="build-component">

### Complete React Component Development

**Full process for building React components:**

1. **Plan Component** - Define props interface and component structure
2. **Create Files** - Set up component, test, and story files
3. **Build Component** - Implement component following standards
4. **Write Tests** - Create comprehensive test coverage
5. **Create Stories** - Build Storybook stories for documentation
6. **Review Accessibility** - Verify WCAG compliance and screen reader support
7. **Optimize Performance** - Add memoization if needed

### File Organization

```plaintext
components/
├── Button.tsx          # Component
├── Button.spec.tsx     # Tests (rc: prefix)
└── Button.stories.tsx  # Storybook
```

### Naming Conventions

- Components: `PascalCase.tsx`
- Hooks: `camelCase.ts` (useAuth.ts)

### CRITICAL Component Rules

- **ALWAYS use arrow functions with `FC` type**
- **NO class components** (except Error Boundaries)
- **ALWAYS export props interface for every component** (required for type safety and documentation)
- **Keep components small and focused**
- **Follow accessibility standards (WCAG)**
- **Optimize performance with memoization when needed**

</workflow>

### Component Template with Accessibility

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

// Component uses the exported interface
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

### Accessibility Requirements

- **ALWAYS** provide semantic HTML elements
- **ALWAYS** include proper ARIA attributes
- **ALWAYS** support keyboard navigation
- **ALWAYS** test with screen readers
- **ALWAYS** maintain proper color contrast (WCAG AA)

</component_structure>

<component_patterns>

## 🎨 Component Design Patterns

### Single Responsibility

- Follow the `Single Responsibility Principle`
- One component should handle one task
- Extract complex logic into custom hooks

### Props Design

- Always define and export props interface
- Keep `props` simple and minimal
- Avoid passing down complex structures
- Use discriminated unions for variant props

### State Management

- Keep state close to usage
- Split contexts for performance
- Use Context API for global state
- Single source of truth

### Performance by Default

- Use `React.memo` for expensive components
- Use `useMemo` for expensive calculations
- Use `useCallback` for stable event handlers
- Avoid creating objects/functions in render
- Implement lazy loading for heavy components

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

</component_patterns>

<performance_optimization>

## ⚡ Performance Optimization

### Component Memoization

Use memoization where performance optimization is necessary:

```typescript
// Memoize expensive components
export const ExpensiveList = memo(({ items }: Props) => {
  return items.map(item => <Item key={item.id} {...item} />);
});

// Memoize calculations
const sorted = useMemo(() => 
  items.sort((a, b) => b.score - a.score),
  [items]
);

// Stable callbacks
const handleClick = useCallback((id: string) => {
  updateItem(id);
}, [updateItem]);
```

### Performance Rules

- Use `React.memo` for components with expensive renders
- Use `useMemo` for expensive calculations
- Use `useCallback` for stable event handlers
- Avoid creating objects/functions in render

</performance_optimization>

<nextjs_patterns>

## 🔗 Next.js Specific Patterns

### Dynamic Imports

```typescript
const HeavyChart = dynamic(() => import('#components/Chart'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

### Image Optimization

```typescript
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // Above fold
  placeholder="blur"
/>
```

### Font Optimization

```typescript
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});
```

### App Router Patterns

- Use Server Components by default
- Add `'use client'` only when needed
- Leverage streaming and suspense
- Optimize for Core Web Vitals

</nextjs_patterns>

<hooks_patterns>

## 🪝 Custom Hooks

### Hook Design Principles

- Start with `use` prefix
- Return consistent interface
- Handle loading and error states
- Make hooks reusable and composable

### Hook Template

```typescript
interface UseDataOptions {
  enabled?: boolean;
  refetchOnMount?: boolean;
}

interface UseDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useData<T>(
  url: string, 
  options: UseDataOptions = {}
): UseDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refetch = useCallback(() => {
    // Implementation
  }, [url]);

  useEffect(() => {
    if (options.enabled !== false) {
      refetch();
    }
  }, [refetch, options.enabled]);

  return { data, loading, error, refetch };
}
```

</hooks_patterns>

<testing_react>

## 🧪 React Testing Standards

### Test File Naming

- React component tests: `Component.spec.tsx`
- Use `rc:` prefix in descriptions

### Testing Template

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

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

### Testing Principles

- Test behavior, not implementation
- Use Testing Library queries effectively
- Mock external dependencies
- Test user interactions
- Verify accessibility attributes

</testing_react>

<accessibility>

## ♿ Accessibility Standards

### ARIA Requirements

- Provide appropriate `aria` attributes
- Support keyboard navigation
- Follow WCAG guidelines
- Test with screen readers

### Accessibility Checklist

✅ Semantic HTML elements used?
✅ Alt text for images?
✅ Focus management implemented?
✅ Keyboard navigation works?
✅ Color contrast meets WCAG standards?
✅ Screen reader friendly?
✅ Form labels properly associated?

### Accessibility Examples

```typescript
// ✅ Good: Semantic and accessible
<button 
  aria-label="Close dialog"
  onClick={handleClose}
>
  <CloseIcon aria-hidden="true" />
</button>

// ✅ Good: Form accessibility
<div>
  <label htmlFor="email">Email Address</label>
  <input 
    id="email"
    type="email"
    aria-describedby="email-help"
    required
  />
  <div id="email-help">We'll never share your email</div>
</div>
```

</accessibility>

<storybook_standards>

## 📖 Storybook Standards

### Story File Naming

- Basic stories: `Component.stories.tsx`
- Complex scenarios: `Component.demo.stories.tsx`

### Story Structure

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Button',
  },
};
```

### Documentation Standards

- Utilize Storybook for component documentation
- Create stories for all component variants
- Document props with JSDoc comments
- Include usage examples and edge cases

</storybook_standards>
