---
argument-hint: '[service-name]'
description: 'Validate service operations in Notion for completeness and coding standards compliance'
tools:
  - mcp__notion__search
  - mcp__notion__fetch
---

Use Notion MCP tools to access the page of $ARGUMENTS service under "Services" database and all of its related service operations under "Service Operations" database. List all operations belonging to $ARGUMENTS. Then ONE by ONE fetch the full page content of each operation page and execute the following validation checklist:

ultrathink

IMPORTANT: If the pseudo code appears to be incomplete/truncated, DO NOT COMPLAINT. it's caused by a bug from notion. The code is very likely complete.

**Use Case Validation:**

- Check each operation has at least one documented use case (one use case is okay)
- Check that any relevant usecase scenarios mentioned in the service page is also mentioned in the service operation page as a sync block
- If missing: Suggest specific user scenarios that would trigger this operation

**Requirements Completeness:**

- DO NOT check the state of the checkboxes
- Verify input parameters are clearly defined with types and constraints
- Verify output interfaces are documented with structure and types (if the output is void, mark the output as type void)
- Verify functional requirements document business logic, processing steps is not required
- If incomplete: Suggest missing interface definitions and all processing steps to document

**Pseudo Code Standards Compliance:**

Validate pseudo code follows this structure and formatted well:

```typescript
import { createOperation } from '#factory';

export default createOperation.<operationName>(
  async ({ inputParam1, inputParam2 }, { verifyAccess, data: { entityName }, service: { self, otherService } }) => {
    // check permission
    verifyAccess(`<resource>:<identifier>:<action>`);

    // business logic implementation
    const result = await entityName.dataOperation({ parameters });

    // additional processing
    // ...

    return result;
  },
);
```

Check these coding standards:

- **Variable Naming**: camelCase for variables/functions, descriptive names preferred
- **Import Order**: Built-in modules (node:\*), third-party libraries, project modules (# prefixed subpath imports, then relative paths)
- **TypeScript**: Strict typing, avoid `any`, use proper interfaces
- **Comments**: Use `//` for single-line, document business logic and complex operations, explain permission checks and data operations, always in lower case
- **Function Structure**: Arrow functions, proper destructuring, async/await, no let, use const, pure function only
- **Pseudo Code IS MEANT TO BE INCOMPLETE**: Focus on the business logic and important steps to follow, use `...` and omit fields for brevity if it's getting long, completeness is not required

**Data Operations Consistency:**

- Extract all data operation calls from pseudo code and compare with the "Data Operations" field (Note that the name of data operation in the Data Operations field is in PascalCase and in the code it'd be camelCase)
- If inconsistent: Checkout all data operation names in the "Data Operations" database. Then suggest to either update the pseudo code (if a similar data operation is found indicating that it may simply a rename) or Suggest to create a new data operation and add it to the data operations field to maintain consistency

**Requirements Alignment:**

- Verify each use case scenario is covered by corresponding requirements
- If gaps: Suggest to add missing requirements or what to refine existing ones to cover all use cases

**Permission Alignment:**

- Verify permission check used in the pseudo code is also declared in the permission field in the service operation page. Note that the permission in permission field would be in `<placeholder>` format instead of `${somename.placeholder}` in the code. They're both placeholders, correct and refer to the same permission. Do not raise as an issue as long as the non-placeholder parts are aligned.

**Code-Requirements Consistency:**

- Verify business logic in pseudo code implements all specified requirements
- If misaligned: Suggest update to the pseudo code to implement missing requirements or adjust requirements to match intended implementation

**Report issues for each operation in this format:**

**✅ Operation: [Operation Name]** (for no issue found)

**❌ Operation: [Operation Name]** (for operation with issues found)

- **Issue Type**: [Use Cases/Requirements/Pseudo Code/Data Ops/Alignment]
- **Problem**: [Specific issue description]
- **Detailed Fix Suggestion**: [Actionable recommendation]

**Group operations by functional domains**

**When Encountering Issues**

When an issue is found in an operation page, IMMEDIATELY pause further checking and offer fix suggestions to the user for approval.

Suggestions must be presented in high readability.

Suggest only the following properities in a service operation page for changes and display diff on content to be applied

- Use Cases
- Permission
- Requirement
- Pseudo Code

**Post Issue Resolution**

When issues on an operation page has been resolved, read this instruction page in the background again and say you'd proceed to the next operation to check for any issues and will IMMEDIATELY report any issues found.
