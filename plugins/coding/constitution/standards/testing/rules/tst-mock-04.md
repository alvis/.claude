# TST-MOCK-04: No Mock Setup in `beforeEach`; No Happy-Path Returns in `it()`

## Intent

`beforeEach` must NOT contain any mock setup — neither happy-path defaults nor error-path overrides. Its **only** acceptable use is resetting call history of non-Vitest mocks that aren't automatically cleared (e.g., `client.resetHistory()`).

- **Happy-path defaults** → file or describe level (inline `vi.fn(...)` or library-specific setup)
- **Error-path overrides** → inside `it()` only
- **`beforeEach`** → exclusively for `client.resetHistory()` or equivalent non-Vitest history clears

This applies to **all mock APIs** — Vitest-native (`vi.fn()`) and library-specific (aws-sdk-client-mock, nock, msw, etc.).

## Fix

```typescript
// ✅ Happy-path default at file level
const upload = vi.fn(async () => ({ etag: "ok" }));

// ✅ Error-path override inside it()
it("should throw on network failure", () => {
  upload.mockRejectedValueOnce(new Error("network"));
  // ...
});
```

## Happy Path vs Error Path Mocking

**Happy path return values MUST be defined inside `vi.mock()` or `vi.hoisted()`**.

Use `vi.hoisted()` ONLY when you need to:

1. **Spy on calls** - Verify mock was called with specific arguments
2. **Throw errors** - Test error handling paths

If you only need the mock to return success data and don't need to inspect calls or throw errors, put everything inside `vi.mock()`:

```typescript
// ✅ CORRECT: happy path mock defined directly in vi.mock()
vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: class {
        getContainerClient() {
          return {
            getBlockBlobClient: () => ({
              upload: vi.fn(async () => ({ etag: 'etag' })),
              exists: vi.fn(async () => true),
            }),
          };
        }
      },
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);
```

## Library-Specific Mocks (aws-sdk-client-mock)

The same principle applies to non-Vitest mock libraries. Happy-path defaults belong at file or describe level — **never** in `beforeEach`.

```typescript
// ❌ WRONG: Any mock setup in beforeEach — even without reset
const kms = mockClient(KMSClient);
beforeEach(() => {
  kms.on(EncryptCommand).resolves({ CiphertextBlob: ciphertext });
  kms.on(DecryptCommand).resolves({ Plaintext: plaintext });
});

// ❌ WRONG: Reset + re-setup in beforeEach
const ecr = mockClient(ECRClient);
beforeEach(() => {
  ecr.reset(); // nuclear reset clears all behavior (TST-MOCK-10)
  ecr.on(GetAuthorizationTokenCommand).resolves({ // re-setting happy-path
    authorizationData: mockAuthorizationData,
  });
});

// ✅ CORRECT: Defaults at describe/file level, history-only clear in beforeEach
const kms = mockClient(KMSClient);
kms.on(EncryptCommand).resolves({ CiphertextBlob: ciphertext });
kms.on(DecryptCommand).resolves({ Plaintext: plaintext });
kms.on(GenerateDataKeyCommand).resolves({
  Plaintext: dataKey,
  CiphertextBlob: encryptedDataKey,
});

beforeEach(() => {
  kms.resetHistory(); // OK — clears call tracking only, keeps behavior
});

// ✅ Error-path override inside it()
it("should throw when decryption fails", () => {
  kms.on(DecryptCommand).rejectsOnce(
    new InvalidCiphertextException({ $metadata: {}, message: "bad" }),
  );
  // ...
});
```

## What Belongs Where

| What | Where | Example |
|---|---|---|
| Happy-path mock defaults | File or `describe` level | `kms.on(Cmd).resolves(...)` |
| Error-path overrides | Inside `it()` | `kms.on(Cmd).rejectsOnce(...)` |
| Non-Vitest history reset | `beforeEach` | `kms.resetHistory()` |
| All other mock setup | **NOT** in `beforeEach` | — |

## Edge Cases

- When existing code has mock setup in `beforeEach` (e.g., `client.on(Cmd).resolves(...)`, `run.mockResolvedValue("ok")`), refactor to file/describe level before adding new behavior.
- If many tests reconfigure the same success return, move that return to default mock setup at file/describe level.
- Multiple `describe` blocks needing different happy-path defaults: set defaults in each `describe` scope, not in `beforeEach`.

## Related

TST-MOCK-01, TST-MOCK-02, TST-MOCK-03, TST-MOCK-10
