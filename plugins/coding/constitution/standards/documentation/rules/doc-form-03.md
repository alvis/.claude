# DOC-FORM-03: Function JSDoc Sentence Style

## Intent

Function JSDoc summaries must start with a present-tense third-person verb (`validates`, `returns`, `creates`), stay lowercase, and omit a trailing period. Noun phrases and verbose forms like `This function ...` are non-compliant.

## Fix

```typescript
/** validates webhook signature */
function validateWebhookSignature(input: SignatureInput): boolean {
  return verifier.matches(input);
}

/** ensures required environment variables exist */
function ensureEnv(): void {}
```

## Non-Functions: Noun Phrases

Non-function elements (interfaces, types, constants) use descriptive noun phrases, not verb forms:

```typescript
/** configuration options for API client initialization */
interface ApiConfig {
  baseUrl: string;
  timeout: number;
}

/** user authentication and profile information */
interface User {
  id: string;
  email: string;
}

/** supported payment methods for transaction processing */
type PaymentMethod = "credit_card" | "paypal" | "bank_transfer";

/** maximum number of retry attempts for failed requests */
const MAX_RETRY_ATTEMPTS = 3;
```

## Quick Reference

| Element | Format | Example |
|---------|--------|---------|
| Function | 3rd person verb, lowercase, no period | `/** validates user input */` |
| Interface | Noun phrase, lowercase, no period | `/** user account information */` |
| Type | Descriptive phrase, lowercase, no period | `/** payment processing status */` |
| Constant | Descriptive phrase, lowercase, no period | `/** maximum retry attempts */` |
| Parameter | Lowercase description | `@param userId the unique identifier` |

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `/** Validate token. */`, refactor before adding new behavior.
- ❌ `/** Validates email address format. */` has two violations: capital V and trailing period.
- ❌ `/** Email validation */` is a noun phrase on a function; rewrite to `/** validates email address format */`.
- ❌ `/** This function validates email */` is verbose; rewrite to `/** validates email address format */`.
- ❌ Unnecessary multi-line for simple void functions: use one-line `/** ensures required environment variables exist */` instead.

## Related

DOC-FORM-01, DOC-FORM-02, DOC-FORM-04
