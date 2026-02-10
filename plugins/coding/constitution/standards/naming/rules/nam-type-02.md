# NAM-TYPE-02: Standard Parameter Vocabulary

## Intent

Use canonical parameter vocabulary by purpose: `params`, `query`, `input`, `options`, `data`, `config`, `context`, `details`, `logger`, `id`. Avoid non-semantic placeholders (`payload`, `cfg`, `extra`, `obj`) when a canonical term applies.

## Fix

```typescript
// canonical parameter names by purpose
function searchCommunities(params: SearchParams): SearchResult[] { /* ... */ }
function listUsers(query: UserQuery): User[] { /* ... */ }
function formatName(name: string, options?: FormatOptions): string { /* ... */ }
function setUser(data: SetUserData): Promise<void> { /* ... */ }
function initializeApp(config: AppConfig): void { /* ... */ }
function handleRequest(request: Request, context: RequestContext): Response { /* ... */ }
function processOrder(details: OrderDetails): ProcessedOrder { /* ... */ }
```

## Parameter Vocabulary

| Name | Usage |
|------|-------|
| `params` | Structured inputs that describe a command or query (filters, identifiers) |
| `query` | Declarative filtering criteria for read operations |
| `input` | User-facing or form-submitted data |
| `options` | Optional modifiers that influence behavior without redefining the primary subject |
| `data` | Core subject matter being created or updated |
| `config` | Configuration objects or initialization settings |
| `context` | Execution context or request metadata |
| `details` | Supplementary metadata accompanying the main subject |
| `logger` | Logging instance |
| `id` | Record identifier |

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `fn(payload, cfg, extra)`, refactor before adding new behavior.

## Related

FUNC-SIGN-03, NAM-TYPE-01, NAM-CORE-01, NAM-CORE-02
