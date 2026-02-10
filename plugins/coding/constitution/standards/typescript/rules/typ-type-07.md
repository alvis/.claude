# TYP-TYPE-07: Testing-Only Partial Cast Pattern

## Intent

Testing partial-cast chains (`satisfies Partial<T> as Partial<T> as T` or equivalent) are test-only and limited to mock boundaries that require full-type compatibility. They are forbidden in production/runtime modules and non-test utilities. `as never` is not allowed for mocked-instance or test-double typing in tests.

## Fix

```typescript
const userRepository = {
  findById: vi.fn(),
} satisfies Partial<UserRepository>;

run(userRepository as Partial<UserRepository> as UserRepository);
```

### Testing Patterns (TESTING ONLY)

Two distinct patterns depending on context:

```typescript
// ✅ INSIDE vi.mock: Triple pattern when mocking partial module
vi.mock("./user-service", () => ({
  userService: {
    getUser: vi.fn(),
  } satisfies Partial<MockedObject<UserService>> as Partial<
    MockedObject<UserService>
  > as MockedObject<UserService>,
}));

// ✅ OUTSIDE vi.mock: Strictly satisfies only
const mockUser = {
  id: "123",
  name: "Test User",
} satisfies Partial<User>;

function setupTest(user: Partial<User> = mockUser) {
  // ...
}
```

**Why two patterns?**

- **Inside vi.mock**: The module system requires the exact type, so triple casting is necessary
- **Outside vi.mock**: Test code should explicitly handle partial types for accuracy

**NOTE**: These patterns are ONLY allowed in test files. Production code must NEVER use these patterns.

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `const u = {} as unknown as User`, refactor before adding new behavior.
- If full-instance typing is required in tests, bridge from `Partial<T>` to `T` only after structural validation.

## Related

TYP-CORE-03, TYP-TYPE-06, TYP-TYPE-01
