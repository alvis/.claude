# Documentation & Comments

## JSDoc

- One‑line preferred: `/** handles user auth */`
- Functions: Start with 3rd‑person verb; lowercase; no trailing period
- Non-functions (interfaces, types, classes, constants, fields, etc.): Use noun phrases for clarity and consistency
- List each `@param`; enumerate every `@throws`
- Exclude TS types in prose
- For functions: Begin JSDoc comments with a third-person singular action verb (e.g., ✅ `handles` not ❌ `handle`)
- For non-functions: Use noun phrases (e.g., ✅ `configuration options` not ❌ `defines configuration options`)
- Write all comments and JSDoc in lowercase
- Explain intent, not mechanics; avoid obvious comments
- Omit hyphens in `@param` tags
- Include any error thrown with a `@throws` tag
- Do not end JSDoc comments with a period
- List all possible throws and explain their conditions
- For single-line JSDoc comments, use `/** description */` instead of multi-line format

~ ✅ EXAMPLES ~

```typescript
// FUNCTIONS: Use 3rd-person verbs
/**
 * fetches a user's profile
 * @param userId the user's ID
 * @returns the user's profile
 * @throw MissingDataError if the user's profile cannot be found
 */
async function fetchUserProfile(userId: string): Promise<UserProfile> {
  const profile = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

  if (!profile) {
    throw new MissingDataError('user profile not found');
  }
}

// NON-FUNCTIONS: Use noun phrases for interfaces, types, classes, constants, fields, etc.

/** configuration options for API client */
interface ApiClientConfig {
  /** base URL for API requests */
  baseUrl: string;
  /** request timeout in milliseconds */
  timeout: number;
}

/** user authentication credentials */
type AuthCredentials = {
  /** user's email address */
  email: string;
  /** user's password */
  password: string;
};

/** HTTP client for external API communication */
class HttpClient {
  /** default request headers */
  private headers: Record<string, string>;
}

/** maximum number of retry attempts */
const MAX_RETRIES = 3;

/** supported file extensions for upload */
export const ALLOWED_EXTENSIONS = ['.jpg', '.png', '.pdf'];
```

## Interface fields

Group keys; each field gets a JSDoc line.

Follow these guidelines when defining interfaces:

- Document all fields with JSDoc comments
- Group fields logically for easy reference
- Use `// <group description> //` to indicate groupings
- Keep field descriptions lowercase and concise

~ ✅ EXAMPLE ~

```typescript
/** describes a product */
interface Product {
  // index //
  /** unique identifier */
  id: string;

  // properties //
  /** display name */
  name: string;
}
```

## Inline Comments

### When to Write Comments

- Explain **why**, not **what**
- Clarify intent, design decisions, or non-obvious reasoning
- Document workarounds, external constraints, or legacy issues
- Explain intentional deviations from best practices
- Avoid comments that merely restate the code

### Comment Format

- Use `// NOTE:` for important explanations
- Add blank line before multi-line NOTE comments
- Keep comments up-to-date when code changes

### Examples

✅ **Good Comments**:

```typescript
// check if user exists before proceeding
if (!user) throw new Error('User not found');

// NOTE: with shared-workspace-lockfile=true, the lockfile is stored in the workspace root only

// NOTE:
// skip processing if there is no tsconfig
// or the current tsconfig is the workspace root tsconfig
// to avoid circular references
```

❌ **Unnecessary Comment**:

```typescript
// loop through the array
for (let i = 0; i < arr.length; i++) {...}
```

--- END ---
