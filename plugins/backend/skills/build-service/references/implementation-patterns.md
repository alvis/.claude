# Implementation Patterns — Draft, Complete, Test

This reference is consulted by **Step 4 (Draft → Implement → Test)** for the per-batch context passed to the `coding:draft-code`, `coding:complete-code`, and `coding:complete-test` sub-skills. The orchestrator dispatches these sub-skills sequentially; this reference supplies the per-batch instructions and reference file paths.

## Draft Phase Context (passed to coding:draft-code)

Files to create with TODO placeholders:

- Operations: `src/operations/{op-name}/index.ts` following `createOperation.opName` pattern
- Integrations: `src/integrations/{system}/` directories (if any)
- Webhooks: `src/webhooks/{system}.ts` files (if any)
- Supporting files: `factory.ts`, `config.ts`, `client.ts`, `peer.ts`, `index.ts`

Reference files:

- `<repository-root>/services/billing/package.json` — package structure
- `<repository-root>/services/product/src/factory.ts` — createServiceFactory pattern
- `<repository-root>/services/atc/src/config.ts` — ServiceConfigSpecification
- `<repository-root>/services/billing/src/client.ts` — ClientInitializer

## Implementation Phase Context (passed to coding:complete-code)

Implementation patterns:

- Operations: `createOperation.opName(async (payload, { data, integration, emit }, { initiator }) => { ... })`
- Use `ensure()` from `@theriety/core` for authorization
- Use `retry()`, `RetryableError` for transient failures
- Reference: `<repository-root>/services/product/src/operations/set-offering/index.ts`

## Test Phase Context (passed to coding:complete-test)

| Aspect | Unit Tests (*.spec.ts) | Integration Tests (*.spec.int.ts) |
|--------|------------------------|--------------------------------------|
| Scope | Each operation + integration | End-to-end flows |
| Data layer | vi.fn() mocks | **Real** action.data |
| External APIs | vi.hoisted() + vi.mock() | **Real** API calls |
| Internal services | N/A | **Mock** via vi.mock() |
| Framework | operationMockFactory | Direct calls |

Reference files:

- `<repository-root>/services/product/spec/operations/set-offering.spec.ts` — unit test
- `<repository-root>/services/billing/spec/integrations/stripe/invoice.spec.ts` — integration test
