# Operation and Controller Implementation

Consulted by workflow step 5 (Implement operations) and step 6 (Integrate the
controller).

## Operation dispatch prompt (batches of related operations, up to 3 batches in parallel)

<IMPORTANT>
The subagent performs the task itself; it must not delegate the work to
another subagent.
</IMPORTANT>

**Read the following assigned standards** and follow them recursively (when
standard A references standard B, read B too):

- plugin:coding:standard:documentation/write
- plugin:coding:standard:function/write
- plugin:coding:standard:testing/write
- plugin:coding:standard:typescript/write
- standard:data-operation

**Assignment**: implement operations `[list]`.

**Steps** (per operation):

1. Implement the operation function with types in
   `operations/{operationName}.ts`
2. Complete the pending test markers in
   `spec/operations/{operationName}.spec.int.ts` drafted during the scaffold
   step; broader coverage work routes to `coding:complete-test`
3. Follow the patterns: types at the top of the file, selectors from
   `#selectors`, `MissingDataError` for not-found
4. Controller integration uses the `Parameters<typeof op>[1]` /
   `ReturnType<typeof op>` delegation pattern

**Report** (under 1000 tokens):

<report>

```yaml
status: success|failure|partial
modifications: ['operations/op.ts', 'spec/operations/op.spec.int.ts', 'source/index.ts']
outputs:
  operations_implemented: ['op1', 'op2']
  test_count: N
issues: []
```

</report>

## Controller dispatch prompt

**Assignment**: update the controller in `source/index.ts`, adding delegating
methods for ALL new operations in alphabetical order.

**Controller pattern**:

```typescript
import { getEntity } from '#operations/getEntity';

export class DomainName {
  #client: PrismaClient;

  public async getEntity(
    input: Parameters<typeof getEntity>[1],
  ): ReturnType<typeof getEntity> {
    return getEntity(this.#client, input);
  }
}
```

## Key standards rules

- **TYP-IMPT-01/02**: import ordering; type imports separated
- **TYP-CORE-03**: no `as unknown as` — use the `satisfies PartialDeep<T>`
  bridge
- **FUNC-SIGN-01/02**: explicit return types; at most 2 positional parameters
- **TST-MOCK-03/04/05/09**: mock patterns (`vi.fn`, no `beforeEach` mocks,
  `satisfies`, no `as unknown as`)
- **TST-STRU-02/03**: test file layout; AAA blank lines
- **TST-CORE-03**: `should` in `it()`, `op:`/`fn:` prefixes in `describe()`
