---
allowed-tools: mcp__notion__search, mcp__notion__fetch
argument-hint: "<service-name> [--operation=operation-name] [--area=area-name]"
description: "Validate service operations in Notion for completeness and standards compliance"
---

# Review Service Operation

In ultrathink mode, review service operations in Notion for completeness and coding standards compliance. Use Notion MCP tools to access the $ARGUMENTS service page under "Services" database and analyze all related service operations under "Service Operations" database.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Does not modify operation pages directly
- Does not validate implementation code in repositories
- Does not check database schema consistency

**When to REJECT:**

- Service or operation does not exist in Notion
- User lacks access to Services or Service Operations database
- Operation pages are incomplete (missing core sections)

## 🔄 Workflow

### Step 1: Planning

1. **Service Discovery**
   - use a subagent
      - Locate the `Services` database via Notion Search (with type database)
      - Fetch the `Services` database and locate the service page
      - Extract service-level context via Notion Fetch
      - From the service page extract metadata (name and id BUT NOT content) of all Service Operations belonging to the service from the link to the database view via Notion Fetch
      - From the service page extract metadata (name and id BUT NOT content) of all Data Operations belonging to the service from the link to the database view via Notion Fetch
      - Report the following content back to the management agent
         - Summary of the service
         - List of service operations (name and id only) belonging to the service
         - List of data operations (name and id only) used by the service

### Step 2: Execution

0. **Delication**
   - In a single message, spin up a subagent for detailed review for each operation, up to 2 operaions at a time
   - Request each subagent to perform the following steps with full detail passed
   - [[IMPORTANT] When there are any issues reported, the management agent must stop dispatching further subagents until all issues have been rectified]
   - [[IMPORTANT] the management agent MUST also pass service-level context, metadata of all service operations and data operations extracted in step 1]
   - [[IMPORTANT] the management agent MUST ask all subagent to ultrathink hard the task and requirement]

1. **Service Page Analysis**
   - Fetch service operation page content via notion fetch method

      **Use Case Validation:**
      - [[IMPORTANT] DO NOT COMPLAINT about the presence of any template placeholders in the use case section]
      - Verify at least one documented use case exists
      - Check sync block alignment with service page scenarios
      - Suggest missing user scenarios if needed

      **Requirements Completeness:**
      - Verify input parameters with types and constraints
      - Check output interfaces documentation
      - Validate functional requirements for business logic
      - Suggest missing interface definitions

      **Pseudo Code Standards Compliance:**
      - Validate pseudo code follows this structure and formatted well:

      ```typescript
      import { ... } from 'node:xxx'; // build-in modules
      
      import { ... } from 'xxx'; // third-party libraries project modules

      import { createOperation } from '#factory'; // project modules

      export default createOperation.<operationName in camelCase>(
      async ({ inputParam1, inputParam2 }, { verifyAccess, data: { entityName }, integration: { library }, service: { self, otherService } }) => {
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

      - **Variable Naming**: camelCase for variables/functions, PascalCase for constants, descriptive names preferred
      - **Import Order**: (1) Built-in modules (node:\*) → (2) third-party libraries → (3) project modules (# prefixed subpath imports, then relative paths), spacing between groups
      - **TypeScript**: Strict typing, avoid `any`, use proper interfaces
      - **Comments**: Use `//` for single-line, document business logic and complex operations, explain permission checks and data operations, always in lower case except for tags such as `// NOTE: ` or references to variable/type/interface/acronym names such as ` // assume UTC timezone`
      - **Function Structure**: Arrow functions, proper destructuring, async/await, no let, use const, pure function only
      - [[IMPORTANT] **Import What Is Used Only**: NOT all import groups are required, only check imports that are definitely needed ]
      - [[IMPORTANT] **Pseudo Code Is MEANT TO BE INCOMPLETE**: Focus on the business logic and important steps to follow, use `...` and omit fields for brevity if it's getting long, completeness is not required, and DO NOT complain about type safety or missing error handling]

      **Data Operations Consistency:**
      - Extract data operation calls from pseudo code
      - Compare with Data Operations field
         - [[IMPORTANT] data operations presented in the Data Operations field may present as an id or url, you can map that with the data operation list retrieved in step 1]
         - [[IMPORTANT] data operations presented in the Data Operations field is always in PascalCase, while in the pseudo code is always in camelCase, DO NOT compliant because of case mismatch]
         - [[IMPORTANT] DO NOT fetch the related data operation pages and ignore their statuses, as it's out of scope]
      - Suggest updates or new operations for consistency

      **Requirements Alignment:**
      - Verify use cases covered by requirements
      - Suggest missing or refined requirements

      **Permission Alignment:**
      - Check permission checks in pseudo code match permission field
      - Account for placeholder format differences

      **Code-Requirements Consistency:**
      - Verify business logic implements all requirements
      - Suggest pseudo code or requirements updates

2. **Issue Escalation Process**
   - When issues found, management agent pauses further validation
   - Present detailed issues report (including code snippet around the issue) and fix suggestions to the management agent, which may inclide
      - Use Cases content changes
      - Permission field updates
      - Requirement modifications
      - Pseudo Code corrections
      - Display content diffs for changes
   - Primary agent present in full detail the issues (including code snippet around the issue) and fix suggestions (with code implementation if code related) to the user
   - Await approval before continuing

3. **Resolution Confirmation**
   - Verify fixes applied correctly
   - Resume validation process
   - Continue to next operation

4. If no issue is found, the subagent should simply report a ✅ for the operation page

### Step 4: Reporting

**Output Format:**

```markdown
Operation Validation Report

## Summary
- Service: [service-name]
- Operations checked: [count]
- Issues found: [count]
- Status: [PASS/ISSUES_FOUND]

## Operations by Functional Domain

### [Domain Group]

✅ Operation: [Operation Name]
   Status: No issues found

❌ Operation: [Operation Name]
   - **Issue Type**: [Use Cases/Requirements/Pseudo Code/Data Ops/Alignment]
   - **Problem**: [Specific issue description]
   - **Detailed Fix Suggestion**: [Actionable recommendation]

## Next Steps
- [Required manual actions]
- [Recommended improvements]
```

## 📝 Examples

### Simple Service Review

```bash
/review-service-operation "user-management" --operation="CreateUser"
# Reviews single operation for standards compliance
```

### Full Service Analysis

```bash
/review-service-operation "user-management"
# Reviews all operations in user-management service
```

### Domain-Specific Review

```bash
/review-service-operation "payment-processing" --area="process-refund"
# Focuses on specific high-risk operation
```

### Error Case Handling

```bash
/review-service-operation "nonexistent-service"
# Error: Service not found in Services database
# Suggestion: Check available services with Notion search
```
