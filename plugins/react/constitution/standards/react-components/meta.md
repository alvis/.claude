# React Component Standards

_Standards for React component structure, patterns, and performance optimization_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- TypeScript Standards (plugin:coding:standard:typescript) - React components use TypeScript interfaces and typing throughout all examples
- Function Standards (plugin:coding:standard:function) - React components are functions and component handlers are functions
- Testing Standards (plugin:coding:standard:testing) - Component test files and testing patterns are essential for quality
- Documentation Standards (plugin:coding:standard:documentation) - Components require proper JSDoc and interface documentation
- General Principles (plugin:coding:standard:universal) - Foundational coding principles that apply to all component code
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

## Rule Groups

- `RC-NAMING-*`: File naming conventions and directory structure for components, tests, and stories.
- `RC-STRUCT-*`: Functional component structure with TypeScript interfaces; no class components except Error Boundaries.
- `RC-PROPS-*`: Props design — exported interfaces, simple/predictable shapes, composition over configuration.
- `RC-STATE-*`: State placement — local-first, lift only when necessary, Context for deep prop drilling.
- `RC-PERF-*`: Performance — memoization with `memo`/`useMemo`/`useCallback`; avoid creating objects in render.
- `RC-NEXT-*`: Framework integration patterns for Next.js (dynamic imports, optimized images).
