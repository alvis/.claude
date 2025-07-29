# React Conventions

This document contains all React-specific development conventions and guidelines.

## Component Structure

### File Organization

React component tests and stories live alongside the component:

```plaintext
src/components/
├── Button.tsx              # Component implementation
├── Button.spec.tsx         # Component tests
└── Button.stories.tsx      # Storybook stories
```

### File Naming Conventions

- Name component files in `PascalCase`, e.g. ✅ `Browser.tsx` ❌ `browser.tsx`
- However, all hooks remain in `camelCase`, e.g. ✅ `useScroll.ts` ❌ `UseScroll.ts`

## Component Guidelines

- **ALWAYS use arrow function components with hooks** - no class components allowed
  - Exception: Error boundaries require class components (React's limitation)
- Use `FC` for functional components with typed props
- Each component should be small, focused, and reusable (Single Responsibility Principle)
- All components must be exported as arrow functions

```typescript
// ✅ correct: arrow function component
export const Button: FC<ButtonProps> = ({ onClick, children }) => {
  return <button onClick={onClick}>{children}</button>;
};

// ❌ wrong: function declaration
export function Button({ onClick, children }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}

// ❌ wrong: class component
export class Button extends Component<ButtonProps> {
  render() {
    return <button onClick={this.props.onClick}>{this.props.children}</button>;
  }
}
```

## Accessibility

Adhere to accessibility (a11y) standards in all components:
- Provide appropriate `aria` attributes
- Support keyboard navigation
- Test components using screen readers
- Follow WCAG guidelines

## State Management

- Use a single source of truth for state management
- Prefer Context API for global state
- Colocate state - keep it as close to usage as possible
- Split contexts for performance (avoid one giant AppContext)

## Props

- Always define and export props type for each component
- Keep props simple and minimize passing down complex structures
- Use descriptive prop names
- Document props with JSDoc comments

```typescript
export interface ButtonProps {
  /** Button variant style */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Click handler */
  onClick?: () => void;
  /** Button content */
  children: ReactNode;
  /** Disabled state */
  disabled?: boolean;
}
```

## Performance

Use component memoization where performance optimization is necessary:

```typescript
// Memoize expensive components
export const ExpensiveList = memo(({ items }: Props) => {
  return items.map(item => <Item key={item.id} {...item} />);
});

// Use useMemo for expensive calculations
const sortedItems = useMemo(
  () => items.sort((a, b) => b.score - a.score),
  [items]
);

// Use useCallback for stable references
const handleClick = useCallback(
  (id: string) => {
    updateItem(id);
  },
  [updateItem]
);
```

## Storybook Documentation

Utilize Storybook for component documentation:
- Create `ComponentName.stories.tsx` for basic component stories
- Use `ComponentName.demo.stories.tsx` for complex scenarios involving multiple components

## Error Boundaries

Error boundaries are the only exception to the arrow function component rule:

```typescript
// note: error boundaries require class components in React
// this is the only exception to our arrow function component rule
import { Component, ErrorInfo, ReactNode } from 'react';
import { captureException } from '#utils/monitoring';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // send to monitoring service
    captureException(error, {
      componentStack: errorInfo.componentStack,
      props: this.props,
    });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary-fallback">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Next.js Specific

### Dynamic Imports

```typescript
// Dynamic imports for heavy components
const HeavyChart = dynamic(() => import('#components/HeavyChart'), {
  loading: () => <Skeleton />,
  ssr: false, // Disable SSR for client-only components
});

// Conditional loading
if (userWantsChart) {
  const { Chart } = await import('#components/Chart');
  // Use Chart
}
```

### Image Optimization

```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority // For above-fold images
  placeholder="blur"
  blurDataURL={blurDataUrl}
/>

// Responsive images
<Image
  src="/product.jpg"
  alt="Product"
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  fill
  style={{ objectFit: 'cover' }}
/>
```

### Font Optimization

```typescript
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Prevent FOIT
  preload: true,
  variable: '--font-inter',
});

// Apply to app
<main className={inter.variable}>
```