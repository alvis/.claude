# Accessibility Standards

_WCAG compliance standards for inclusive web development_

## Core Accessibility Requirements

### WCAG 2.1 AA Compliance

All components must meet WCAG 2.1 AA standards:

- **Perceivable** - Information and UI components must be presentable to users in ways they can perceive
- **Operable** - UI components and navigation must be operable
- **Understandable** - Information and UI operation must be understandable
- **Robust** - Content must be robust enough to be interpreted by a wide variety of assistive technologies

### Critical Rules

- **ALWAYS provide semantic HTML elements**
- **ALWAYS include proper ARIA attributes**
- **ALWAYS support keyboard navigation**
- **ALWAYS test with screen readers**
- **ALWAYS maintain proper color contrast (WCAG AA)**
- **ALWAYS provide alternative text for images**
- **ALWAYS associate form labels properly**

## Semantic HTML

### Use Proper HTML Elements

```typescript
// ✅ GOOD: semantic HTML improves accessibility and SEO
<button onClick={handleSubmit}>Submit Form</button>
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/home">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>
<main>
  <h1>Page Title</h1>
  <article>
    <h2>Article Title</h2>
    <p>Article content...</p>
  </article>
</main>

// ❌ BAD: non-semantic HTML reduces accessibility
<div onClick={handleSubmit}>Submit Form</div>
<div className="nav">
  <div className="nav-item">Home</div>
  <div className="nav-item">About</div>
</div>
<div className="main">
  <div className="title">Page Title</div>
  <div className="article">
    <div className="article-title">Article Title</div>
    <div>Article content...</div>
  </div>
</div>
```

### Heading Hierarchy

```typescript
// ✅ GOOD: proper heading hierarchy maintains logical document structure
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

// ❌ BAD: broken heading hierarchy confuses screen readers
<main>
  <h1>Main Page Title</h1>
  <h4>Should be h2</h4>  {/* Skipped levels */}
  <h2>Out of order</h2>
</main>
```

## ARIA Attributes

### Essential ARIA Attributes

```typescript
// ✅ GOOD: proper ARIA usage enhances accessibility context
<button
  aria-label="Close dialog"
  aria-expanded={isOpen}
  aria-controls="dialog-content"
  onClick={handleClose}
>
  <CloseIcon aria-hidden="true" />
</button>

<div
  role="dialog"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
  aria-modal="true"
>
  <h2 id="dialog-title">Confirm Action</h2>
  <p id="dialog-description">Are you sure you want to delete this item?</p>
</div>

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

### ARIA Roles

```typescript
// ✅ GOOD: appropriate ARIA roles clarify component purpose
<div role="tablist" aria-label="Settings sections">
  <button
    role="tab"
    aria-selected={activeTab === 'general'}
    aria-controls="general-panel"
    id="general-tab"
  >
    General
  </button>
  <button
    role="tab"
    aria-selected={activeTab === 'privacy'}
    aria-controls="privacy-panel"
    id="privacy-tab"
  >
    Privacy
  </button>
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

## Keyboard Navigation

### Focus Management

```typescript
// ✅ GOOD: proper focus management ensures keyboard accessibility
export const Modal: FC<ModalProps> = ({ isOpen, onClose, children }) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Store current focus
      previousFocusRef.current = document.activeElement as HTMLElement;

      // Focus the modal
      dialogRef.current?.focus();

      // Trap focus within modal
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }

        if (e.key === 'Tab') {
          trapFocus(e, dialogRef.current);
        }
      };

      document.addEventListener('keydown', handleKeyDown);

      return () => {
        document.removeEventListener('keydown', handleKeyDown);
        // Restore focus
        previousFocusRef.current?.focus();
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
      onKeyDown={(e) => {
        if (e.key === 'Escape') onClose();
      }}
    >
      {children}
    </div>
  );
};
```

### Keyboard Event Handling

```typescript
// ✅ GOOD: keyboard accessibility supports all interaction methods
export const CustomButton: FC<Props> = ({ onClick, children }) => {
  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    // Support both Enter and Space like native buttons
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
```

## Form Accessibility

### Form Labels and Descriptions

```typescript
// ✅ GOOD: accessible form components provide clear user guidance
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
      <label htmlFor={id} className="form-label">
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

      {helpText && (
        <div id={helpId} className="form-help">
          {helpText}
        </div>
      )}

      {error && (
        <div id={errorId} role="alert" className="form-error">
          {error}
        </div>
      )}
    </div>
  );
};
```

### Form Validation Messages

```typescript
// ✅ GOOD: accessible error handling announces validation issues
export const useFormValidation = (schema: ValidationSchema) => {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const announceErrors = useCallback((newErrors: Record<string, string>) => {
    // Announce errors to screen readers
    const errorCount = Object.keys(newErrors).length;
    if (errorCount > 0) {
      const announcement = `Form has ${errorCount} error${errorCount > 1 ? "s" : ""}. Please review and correct.`;

      // Create live region announcement
      const liveRegion = document.createElement("div");
      liveRegion.setAttribute("aria-live", "polite");
      liveRegion.setAttribute("aria-atomic", "true");
      liveRegion.style.position = "absolute";
      liveRegion.style.left = "-10000px";
      liveRegion.textContent = announcement;

      document.body.appendChild(liveRegion);

      setTimeout(() => {
        document.body.removeChild(liveRegion);
      }, 1000);
    }
  }, []);

  const validate = useCallback(
    (values: Record<string, any>) => {
      const newErrors = schema.validate(values);
      setErrors(newErrors);

      if (Object.keys(newErrors).length > 0) {
        announceErrors(newErrors);
      }

      return Object.keys(newErrors).length === 0;
    },
    [schema, announceErrors],
  );

  return { errors, touched, setTouched, validate };
};
```

## Color and Contrast

### Color Contrast Requirements

```typescript
// ✅ GOOD: high contrast color definitions meet WCAG standards
const colors = {
  // WCAG AA compliant contrast ratios
  primary: "#0066cc", // 4.5:1 against white
  primaryText: "#ffffff", // High contrast text
  secondary: "#6c757d", // 4.5:1 against white
  success: "#28a745", // 3:1 against white
  danger: "#dc3545", // 4.5:1 against white
  warning: "#856404", // 4.5:1 against white (darker than default)

  // Text colors
  textPrimary: "#212529", // High contrast
  textSecondary: "#6c757d", // Still meets AA
  textMuted: "#6c757d", // 4.5:1 minimum
} as const;

// ❌ BAD: low contrast colors fail accessibility requirements
const badColors = {
  lightGray: "#e9ecef", // Too light for text
  paleBlue: "#cce7ff", // Insufficient contrast
  lightText: "#999999", // Below 4.5:1 ratio
};
```

### Color Usage Patterns

```typescript
// ✅ GOOD: avoiding color-only indicators supports colorblind users
export const StatusIndicator: FC<StatusIndicatorProps> = ({ status, message }) => {
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
      className={`status-indicator status-${status}`}
      role="status"
      aria-label={`${status}: ${message}`}
    >
      {getStatusIcon(status)}
      <span>{message}</span>
    </div>
  );
};

// ❌ BAD: color-only indication excludes colorblind users
export const BadStatusIndicator: FC<Props> = ({ status, message }) => {
  return (
    <div className={`status-${status}`}>
      {message}
    </div>
  );
};
```

## Screen Reader Support

### Live Regions

```typescript
// ✅ GOOD: screen reader announcements provide dynamic feedback
export const useLiveAnnouncement = () => {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.textContent = message;

    document.body.appendChild(liveRegion);

    setTimeout(() => {
      if (document.body.contains(liveRegion)) {
        document.body.removeChild(liveRegion);
      }
    }, 1000);
  }, []);

  return { announce };
};

// Usage in component
export const NotificationSystem: FC<Props> = () => {
  const { announce } = useLiveAnnouncement();

  const handleSuccess = useCallback((message: string) => {
    announce(`Success: ${message}`, 'polite');
  }, [announce]);

  const handleError = useCallback((message: string) => {
    announce(`Error: ${message}`, 'assertive');
  }, [announce]);

  return (
    <div role="region" aria-label="Notifications">
      {/* Notification content */}
    </div>
  );
};
```

### Hidden Content for Screen Readers

```typescript
// ✅ GOOD: screen reader only content provides additional context
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

// Usage
export const IconButton: FC<Props> = ({ icon, onClick, label }) => {
  return (
    <button onClick={onClick} aria-label={label}>
      {icon}
      <VisuallyHidden>{label}</VisuallyHidden>
    </button>
  );
};
```

## Testing Accessibility

### Accessibility Testing Checklist

✅ **Manual Testing Checklist:**

- [ ] Navigate entire interface using only keyboard
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast meets WCAG AA standards
- [ ] Check heading hierarchy and structure
- [ ] Ensure all images have appropriate alt text
- [ ] Test form labels and error messages
- [ ] Verify focus indicators are visible
- [ ] Test with browser zoom at 200%

### Automated Testing

```typescript
// ✅ GOOD: accessibility testing ensures compliance and usability
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './Button';

expect.extend(toHaveNoViolations);

describe('rc:Button accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(
      <Button onClick={() => {}}>Click me</Button>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be accessible via keyboard', () => {
    const mockClick = vi.fn();
    render(<Button onClick={mockClick}>Click me</Button>);

    const button = screen.getByRole('button');
    button.focus();

    // Should be focusable
    expect(button).toHaveFocus();

    // Should activate on Enter
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(mockClick).toHaveBeenCalled();
  });

  it('should have proper ARIA attributes', () => {
    render(
      <Button
        aria-label="Custom label"
        disabled={true}
      >
        Button
      </Button>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Custom label');
    expect(button).toHaveAttribute('disabled');
  });
});
```

## Common Accessibility Issues

### Issues to Avoid

```typescript
// ❌ BAD: common accessibility problems that reduce usability
// Missing alt text
<img src="chart.png" />

// Unclear link text
<a href="/details">Click here</a>

// No keyboard support
<div onClick={handleClick}>Button</div>

// Missing form labels
<input type="email" placeholder="Email" />

// Low contrast
<span style={{ color: '#999', backgroundColor: '#eee' }}>Text</span>

// ✅ GOOD: accessible alternatives improve user experience
// Descriptive alt text
<img src="chart.png" alt="Sales increased 20% from Q1 to Q2" />

// Clear link text
<a href="/details">View product details</a>

// Proper button with keyboard support
<button onClick={handleClick}>Submit</button>

// Properly labeled form fields
<label htmlFor="email">Email Address</label>
<input id="email" type="email" />

// High contrast colors
<span style={{ color: '#212529', backgroundColor: '#ffffff' }}>Text</span>
```
