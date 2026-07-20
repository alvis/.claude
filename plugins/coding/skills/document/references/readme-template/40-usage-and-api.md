## 📖 Usage

<Show several real-world usage examples with code snippets. Focus on common patterns and best practices.>

<Examples should demonstrate:>
- Most common use cases
- Important configuration options
- Integration with other packages
- Error handling patterns (where relevant)

```ts
import { mainExport } from '@theriety/<package-name>';

// clear, practical example
```

---

<!--
IMPORTANT: All code examples in this section MUST be valid TypeScript that can be verified
by the TypeScript compiler. Before adding examples:

1. Create a temporary .ts file in your package
2. Copy the example code into it
3. Run `tsc --noEmit <temp-file>.ts` to verify it compiles
4. Only include examples that pass TypeScript compilation
5. Delete the temporary file after verification

CODE STYLE:
- All comments (code and file tree) start with lowercase
- File tree comments: align vertically with 2 spaces after the longest path **within each directory level**
  - Calculate alignment separately for each directory level (top-level, subdirectory entries, etc.)
  - Do NOT align globally across the entire tree
- Exception: proper nouns, acronyms, code identifiers

**File Tree Alignment Example:**
```plain
src
├── adapters   # top-level: all aligned 2 spaces after longest (utilities)
├── schemas    # top-level: aligned with other top-level entries
│   ├── cache.ts         # schemas level: all aligned 2 spaces after longest (verylongname.ts)
│   ├── service.ts       # schemas level: aligned with siblings
│   └── verylongname.ts  # schemas level: this is the longest, dictates alignment
├── utilities  # top-level: this is the longest, dictates alignment
└── index.ts   # top-level: aligned with other top-level entries
```

**Folder Notation Rule:** Never use trailing `/` on directory names. Write `src/components`, not `src/components/`. Applies to TOCs, tree fences, component refs, and prose references.

This ensures examples remain accurate and useful as the package evolves.
-->

### Example: <Realistic Use Case Title>

<Describe the scenario this example addresses. What real-world problem does it solve?>

```ts
// complete, working example that combines multiple features
// must be valid TypeScript that compiles without errors
import { feature1, feature2 } from '@theriety/<package-name>';

// show imports, setup, execution, and result handling
```

### Example: <Another Use Case>

<Another realistic scenario with complete working code>

```ts
// another validated TypeScript example
```

---

## 📚 API Reference

<!--
Organization guidelines:
- If there are many exports, group them by logical section (e.g., "Core Functions", "Utility Functions", "Type Definitions")
- For each group, use a heading (###) then collapsible details for each API
- If your library is small (< 10 exports), you may omit grouping and just use collapsible details
- Always include examples for each API function
-->

### <Section Name 1>

<details>
<summary><code>functionName(param1: Type1, param2: Type2): ReturnType</code></summary>

**Description:**
<One or two sentences describing what this function/class/type does and when to use it.>

**Parameters:**

- `param1` (`Type1`): Clear description of the parameter, including any constraints or special values
- `param2` (`Type2`): Description with examples of valid values if helpful
<!-- Repeat for each parameter -->

**Returns:**

- `ReturnType`: Description of what is returned, including structure for objects

**Throws:** <!-- Optional: include if the function can throw errors -->

- `ErrorType`: When and why this error is thrown
<!-- Repeat for each error type -->

**Example:**

```ts
// practical example showing typical usage
import { functionName } from '@theriety/<package-name>';

const result = functionName(value1, value2);
// result: expected output
```

**Type Signature:** <!-- Optional: for complex generic types -->

```ts
function functionName<T extends Constraint>(
  param1: Type1,
  param2: Type2,
): ReturnType<T>;
```

</details>

<!-- Repeat the above structure for each API in the section -->

### <Section Name 2>

<!-- Additional grouped APIs, if applicable -->

---

<!-- OSS-ONLY START: Advanced -->
<!--
When to include: any package with non-trivial extension points, performance footguns, or edge-case behaviour readers will hit in production. Skip for tiny utilities whose surface is fully covered by API Reference.
Purpose: collect gotchas and power-user knobs so advanced users don't have to spelunk the source.
-->
