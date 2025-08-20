# Accessibility Standards

_WCAG compliance standards for inclusive web development_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- [General Principles](@../../general-principles.md) - Accessibility builds on fundamental coding principles of clarity, consistency, and user-centered design
- [Documentation Standards](@../../documentation.md) - All accessibility features and decisions must be properly documented for compliance and team understanding

## Core Principles

### WCAG 2.1 AA Compliance

All components must meet the four fundamental accessibility principles.

```typescript
// ✅ GOOD: accessible button with proper semantics
<button
  aria-label="Close dialog"
  aria-expanded={isOpen}
  onClick={handleClose}
>
  <CloseIcon aria-hidden="true" />
  Close
</button>

// ❌ BAD: inaccessible clickable div
<div onClick={handleClose} className="button-like">
  <CloseIcon />
</div>
```

### Semantic HTML First

Use proper HTML elements before adding ARIA attributes.

```typescript
// ✅ GOOD: semantic HTML provides built-in accessibility
<button onClick={handleSubmit}>Submit Form</button>
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/home">Home</a></li>
    ...
  </ul>
</nav>
<main>
  <h1>Page Title</h1>
  <article>
    <h2>Article Title</h2>
    ...
  </article>
</main>

// ❌ BAD: non-semantic HTML reduces accessibility
<div onClick={handleSubmit}>Submit Form</div>
<div className="nav">
  <div className="nav-item">Home</div>
  ...
</div>
```

### Keyboard Navigation Support

Ensure all interactive elements are keyboard accessible.

```typescript
// ✅ GOOD: keyboard accessible custom element
export const CustomButton: FC<Props> = ({ onClick, children }) => {
  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      aria-label="Custom action button"
    >
      {children}
    </div>
  );
};

// ❌ BAD: no keyboard support
<div onClick={onClick} className="clickable">
  {children}
</div>
```

## Document Structure

### Heading Hierarchy

Maintain logical heading order for screen reader navigation.

```typescript
// ✅ GOOD: proper heading hierarchy
<main>
  <h1>Main Page Title</h1>
  <section>
    <h2>Section Title</h2>
    <article>
      <h3>Article Title</h3>
      <h4>Subsection</h4>
    </article>
  </section>
</main>

// ❌ BAD: skipped heading levels
<main>
  <h1>Main Page Title</h1>
  <h4>Should be h2</h4>  // Skipped h2, h3
  <h2>Out of order</h2>
</main>
```

## ARIA Implementation

### Essential ARIA Patterns

```typescript
// ✅ GOOD: dialog with proper ARIA
<div
  role="dialog"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
  aria-modal="true"
>
  <h2 id="dialog-title">Confirm Action</h2>
  <p id="dialog-description">Are you sure you want to delete this item?</p>
  <button onClick={handleConfirm}>Yes, Delete</button>
  <button onClick={handleCancel}>Cancel</button>
</div>

// ✅ GOOD: form field with descriptions
<input
  type="email"
  id="email"
  aria-describedby="email-help email-error"
  aria-invalid={hasError}
  aria-required="true"
/>
<div id="email-help">We'll never share your email</div>
{hasError && <div id="email-error" role="alert">Please enter a valid email</div>}
```

### Interactive Widget Roles

```typescript
// ✅ GOOD: tab interface with proper roles
<div role="tablist" aria-label="Settings sections">
  <button
    role="tab"
    aria-selected={activeTab === 'general'}
    aria-controls="general-panel"
    id="general-tab"
  >
    General
  </button>
  ...
</div>

<div
  role="tabpanel"
  id="general-panel"
  aria-labelledby="general-tab"
  hidden={activeTab !== 'general'}
>
  General settings content
</div>
```

## Focus Management

### Modal Focus Trapping

```typescript
// ✅ GOOD: proper focus management in modal
export const Modal: FC<ModalProps> = ({ isOpen, onClose, children }) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // store and move focus
      previousFocusRef.current = document.activeElement as HTMLElement;
      dialogRef.current?.focus();

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
        if (e.key === 'Tab') trapFocus(e, dialogRef.current);
      };

      document.addEventListener('keydown', handleKeyDown);

      return () => {
        document.removeEventListener('keydown', handleKeyDown);
        previousFocusRef.current?.focus(); // restore focus
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={dialogRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
    >
      {children}
    </div>
  );
};
```


## Form Accessibility

### Accessible Form Fields

```typescript
// ✅ GOOD: complete accessible form field
export const FormField: FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  required = false,
  helpText,
  error,
  ...props
}) => {
  const id = `field-${name}`;
  const helpId = helpText ? `${id}-help` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [helpId, errorId].filter(Boolean).join(' ');

  return (
    <div className="form-field">
      <label htmlFor={id}>
        {label}
        {required && <span aria-label="required"> *</span>}
      </label>

      <input
        id={id}
        name={name}
        type={type}
        aria-describedby={describedBy || undefined}
        aria-invalid={error ? 'true' : 'false'}
        aria-required={required}
        {...props}
      />

      {helpText && <div id={helpId}>{helpText}</div>}
      {error && <div id={errorId} role="alert">{error}</div>}
    </div>
  );
};
```


## Visual Design

### Color and Contrast

Ensure sufficient color contrast and avoid color-only indicators.

```typescript
// ✅ GOOD: WCAG AA compliant colors
const colors = {
  primary: "#0066cc",    // 4.5:1 contrast ratio
  success: "#28a745",    // High contrast
  danger: "#dc3545",     // 4.5:1 against white
  textPrimary: "#212529", // High contrast
  textSecondary: "#6c757d", // Meets AA standard
} as const;

// ❌ BAD: insufficient contrast
const badColors = {
  lightGray: "#e9ecef",  // Too light for text
  paleText: "#999999",   // Below 4.5:1 ratio
};
```

### Color-Independent Design

Use icons and text alongside color to convey information.

```typescript
// ✅ GOOD: status with icon and text
export const StatusIndicator: FC<Props> = ({ status, message }) => {
  const getStatusIcon = (status: Status) => {
    switch (status) {
      case 'success': return <CheckIcon aria-hidden="true" />;
      case 'warning': return <WarningIcon aria-hidden="true" />;
      case 'error': return <ErrorIcon aria-hidden="true" />;
      default: return <InfoIcon aria-hidden="true" />;
    }
  };

  return (
    <div
      className={`status-${status}`}
      role="status"
      aria-label={`${status}: ${message}`}
    >
      {getStatusIcon(status)}
      <span>{message}</span>
    </div>
  );
};

// ❌ BAD: color-only indication
<div className={`status-${status}`}>{message}</div>
```

## Screen Reader Support

### Live Region Announcements

```typescript
// ✅ GOOD: dynamic announcements for screen readers
export const useLiveAnnouncement = () => {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.textContent = message;

    document.body.appendChild(liveRegion);
    setTimeout(() => document.body.removeChild(liveRegion), 1000);
  }, []);

  return { announce };
};

// usage in notifications
export const NotificationSystem: FC<Props> = () => {
  const { announce } = useLiveAnnouncement();

  const handleSuccess = useCallback((message: string) => {
    announce(`Success: ${message}`, 'polite');
  }, [announce]);

  return (
    <div role="region" aria-label="Notifications">
      {/* notification content */}
    </div>
  );
};
```

### Visually Hidden Content

```typescript
// ✅ GOOD: content hidden visually but available to screen readers
export const VisuallyHidden: FC<{ children: ReactNode }> = ({ children }) => {
  const srOnlyStyle: CSSProperties = {
    position: 'absolute',
    width: '1px',
    height: '1px',
    padding: '0',
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap',
    border: '0',
  };

  return <span style={srOnlyStyle}>{children}</span>;
};

// usage for icon buttons
<button onClick={onClick} aria-label={label}>
  {icon}
  <VisuallyHidden>{label}</VisuallyHidden>
</button>
```

## Quick Reference

| Element Type | Accessibility Requirements | ARIA Attributes | Notes |
|--------------|---------------------------|------------------|-------|
| Button | Keyboard support, focus indicator | `aria-label`, `aria-expanded` | Use `<button>` element |
| Form Input | Label association, error states | `aria-describedby`, `aria-invalid` | Required `<label>` |
| Modal/Dialog | Focus trap, escape key | `role="dialog"`, `aria-modal` | Manage focus |
| Navigation | Landmark roles, skip links | `role="navigation"`, `aria-label` | Clear structure |
| Status Updates | Live region announcements | `aria-live`, `role="alert"` | Use appropriate urgency |

## Patterns & Best Practices

### Accessible Modal Pattern

**Purpose:** Create keyboard-accessible modal dialogs with proper focus management

**When to use:**
- Confirmation dialogs
- Form overlays
- Content popups

**Implementation:**

```typescript
// pattern template
export const AccessibleModal: FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      const previousFocus = document.activeElement;
      dialogRef.current?.focus();

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
      };

      document.addEventListener('keydown', handleKeyDown);
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
        (previousFocus as HTMLElement)?.focus();
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" tabIndex={-1}>
        <h2 id="modal-title">{title}</h2>
        {children}
      </div>
    </div>
  );
};
```

### Common Patterns

1. **Skip Links** - Allow keyboard users to skip navigation

   ```typescript
   <a href="#main-content" className="skip-link">
     Skip to main content
   </a>
   ```

2. **Loading States** - Announce loading to screen readers

   ```typescript
   {loading && <div aria-live="polite">Loading content...</div>}
   ```

## Anti-Patterns

### Missing Alt Text

```typescript
// ❌ BAD: missing alt text
<img src="chart.png" />

// ✅ GOOD: descriptive alt text
<img src="chart.png" alt="Sales increased 20% from Q1 to Q2" />
```

### Non-Semantic Interactive Elements

```typescript
// ❌ BAD: div as button without keyboard support
<div onClick={handleClick} className="button-like">Click me</div>

// ✅ GOOD: proper button element
<button onClick={handleClick}>Click me</button>
```

### Common Mistakes to Avoid

1. **Color-only indicators**
   - Problem: Colorblind users cannot distinguish states
   - Solution: Use icons, text, or patterns alongside color
   - Example: `<span className="error"><ErrorIcon /> Error message</span>`

2. **Missing form labels**
   - Problem: Screen readers cannot identify input purpose
   - Solution: Always associate labels with inputs

## Quick Decision Tree

1. **Is this interactive?**
   - If button-like → Use `<button>` element
   - If link-like → Use `<a>` element
   - If custom → Add keyboard support and ARIA

2. **Does this convey information?**
   - If status change → Use live region
   - If error state → Use `role="alert"`
   - If additional context → Use `aria-describedby`

3. **Is this visible to all users?**
   - If decorative only → Use `aria-hidden="true"`
   - If informative → Provide alt text or screen reader text
   - If interactive → Ensure keyboard accessibility

