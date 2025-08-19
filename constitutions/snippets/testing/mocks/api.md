# API Mocking Snippets

## Core Principle: Mock at HTTP Level

**Always prefer mocking low-level HTTP API calls via Undici, even when using client wrappers** (e.g., Notion Client, Stripe SDK, etc.). This approach:

- Tests the actual client library's HTTP handling and parsing
- Provides realistic API responses that match production
- Catches integration issues between client and API
- Remains stable across client library version changes
- Enables testing of edge cases and error scenarios the client must handle

### Example: Mocking with Client Wrappers

```ts
// ✅ GOOD: Mock HTTP, use real client
import { Client } from '@notionhq/client';
import { MockAgent, setGlobalDispatcher } from 'undici';

const mockAgent = new MockAgent();
setGlobalDispatcher(mockAgent);

// mock the actual Notion API endpoints
mockAgent.get('https://api.notion.com')
  .intercept({ path: '/v1/pages/page-id' })
  .reply(200, { 
    object: 'page',
    id: 'page-id',
    properties: { /* actual API response */ }
  });

// use real client with global fetch (intercepted by Undici)
const client = new Client({ fetch }); // ← key: pass global fetch
const page = await client.pages.retrieve({ page_id: 'page-id' });
// client processes real API response format
```

```ts
// ❌ BAD: mocking client methods directly
vi.spyOn(client.pages, 'retrieve').mockResolvedValue(mockPage);
// bypasses client's HTTP handling, parsing, and error logic
```

## HTTP Mocking (Undici)

### Basic Setup

```ts
import { MockAgent, setGlobalDispatcher } from 'undici';

const mockAgent = new MockAgent();
setGlobalDispatcher(mockAgent);

// before describe

describe(...)
```

### Simple Mock

```ts
mockAgent.get('https://api.example.com')
  .intercept({ path: '/v1/resource' })
  .reply(200, { data: 'value' })
  .persist(); // keep mock active for multiple calls
```

### Dynamic Response

```ts
mockAgent.get('https://api.example.com')
  .intercept({ method: 'POST', path: '/v1/search' })
  .reply(200, (request) => {
    const body = JSON.parse(request.body);
    return { query: body.query, results: [] };
  });
```

### Error Mock

```ts
// HTTP error
mockAgent.get('https://api.example.com')
  .intercept({ path: '/v1/*' })
  .reply(404, { error: 'Not found' });

// Network error
mockAgent.get('https://api.example.com')
  .intercept({ path: '/v1/*' })
  .replyWithError(new Error('Network error'));
```

## Module Mocking (Vitest)

### Typed Module Mock

```ts
const { mockFn } = vi.hoisted(() => ({
  mockFn: vi.fn<() => string>(() => 'typed')
}));

vi.mock('#module', () => ({
  mockFn
} satisfies Partial<typeof import('#module')>));
```

### Spy on Method

```ts
const spy = vi.spyOn(object, 'method')
  .mockResolvedValue({ data: 'test' });

// later assertions
expect(spy).toHaveBeenCalledWith(args);
```

## Patterns

### Factory Function

```ts
const buildUser = (overrides = {}) => ({
  id: 'test-id',
  name: 'Test',
  ...overrides
});
```

### Parameterized Mock Helper

```ts
export const mockAPI = (params: {
  id: string;
  status?: number;
  data?: unknown;
}) => {
  const { id, status = 200, data = {} } = params;
  mockAgent.get('https://api.example.com')
    .intercept({ path: `/v1/resource/${id}` })
    .reply(status, data)
    .persist();
};
```

### Test with Fetch Override

```ts
// CRITICAL: Pass global fetch to enable HTTP interception
const notion = new Client({ fetch }); // Notion client
const stripe = new Stripe('key', { httpClient: { fetch } }); // Stripe client  
const custom = new APIClient({ fetch }); // Custom clients

// Without { fetch }, mocking won't work as clients use their own HTTP layer
```
