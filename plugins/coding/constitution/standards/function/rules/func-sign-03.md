# FUNC-SIGN-03: Standard Parameter Names

## Intent

Use canonical semantic names: `params` (structured query/command input), `options` (optional modifiers), `data` (primary payload), `config` (initialization), `context` (execution metadata), `details` (supplemental metadata). Avoid opaque placeholders like `payload`, `cfg`, and `extra` when a canonical name fits.

## Fix

```typescript
function getUserProfile(params: { userId: string }): Promise<User> {
  return api.get(`/users/${params.userId}`);
}
```

### `options` for Optional Configuration

```typescript
interface FormatOptions {
  locale?: string;
  currency?: string;
  precision?: number;
}

function formatPrice(amount: number, options: FormatOptions = {}): string {
  const { locale = "en-US", currency = "USD", precision = 2 } = options;
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: precision,
  }).format(amount);
}
```

### `data` for Primary Payload

```typescript
function createUser(data: CreateUserData): Promise<User> {
  return api.post("/users", data);
}

function updateProfile(userId: string, data: UpdateProfileData): Promise<User> {
  return api.patch(`/users/${userId}`, data);
}
```

### `config` for Initialization

```typescript
interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  ssl?: boolean;
  poolSize?: number;
}

class Database {
  constructor(config: DatabaseConfig) {
    this.config = config;
    this.connect();
  }
}
```

### `context` for Execution Metadata

```typescript
interface RequestContext {
  user: User;
  requestId: string;
  permissions: string[];
}

function checkAccess(resource: Resource, context: RequestContext): boolean {
  if (resource.ownerId === context.user.id) return true;
  if (context.permissions.includes("admin")) return true;
  return false;
}
```

### `details` for Supplemental Metadata

```typescript
interface ErrorDetails {
  code: string;
  field?: string;
  originalError?: Error;
}

function logError(message: string, details: ErrorDetails): void {
  logger.error(message, {
    errorCode: details.code,
    field: details.field,
    stack: details.originalError?.stack,
  });
}
```

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `fn(payload, cfg, extra)`, refactor before adding new behavior.
- Choose parameter names by role in the API contract, not by current implementation details.

## Related

FUNC-SIGN-01, FUNC-SIGN-02, FUNC-SIGN-04, NAM-TYPE-02
