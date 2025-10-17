---
allowed-tools: "Bash, Read, Grep, Glob, Task, mcp__plugin_specification_notion__notion-search, mcp__plugin_specification_notion__notion-fetch, mcp__plugin_web_browser__browser_navigate, mcp__plugin_web_browser__browser_get_markdown"

argument-hint: <service-name> [--area=...]

description: "Review service documentation completeness on Notion"
---

# Review Service Operation

Review the completeness and integrity of a service's documentation on Notion through comprehensive validation of service operations. This command orchestrates parallel validation tasks to ensure all service operations meet coding standards and completeness requirements.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Modify or edit service operation content in Notion
- Create or implement new service operations
- Read old or outdated documentation files from the local filesystem
- Perform service implementation or code generation

**When to REJECT**:

- Service name does not exist in Notion Services database
- User lacks appropriate permissions to access Notion workspace
- Request involves editing or modifying service operations
- Request asks to read local documentation files instead of Notion



## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Review Service Operation Workflow

- Execute review-service-operation.md

### Step 2: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Service: [service-name]
- Operations reviewed: [count]
- Issues found: [count]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. Discovered service operations from Notion Services database
2. Validated [count] operations across [domains] functional domains
3. Generated comprehensive validation report with recommendations

## Workflows Applied
- Review Service Operation: [Status]

## Issues Found (if any)
- **Issue**: [Description with location]
  **Fix**: [Applied fix or actionable recommendation]

## Validation Report
[Link or content of comprehensive validation report]
```

## 📝 Examples

### Simple Usage

```bash
/review-service-operation "user-management"
# Reviews all operations for the user-management service
```

### Complex Usage with Area Filter

```bash
/review-service-operation "payment-processing" --area="authentication" 
# Reviews only operations in authentication area for payment-processing service
```

### Delegation Example

```bash
/review-service-operation "notification-service"
# Automatically delegates to:
#   - Discovery Agent: Extracts service context and operations
#   - Validator A: Reviews operations 1-2 (parallel)
#   - Validator B: Reviews operations 3-4 (parallel)
#   - Report Agent: Consolidates findings
```

### Error Case Handling

```bash
/review-service-operation "nonexistent-service"
# Error: Service 'nonexistent-service' not found in Services database
# Suggestion: Check available services with Notion search
# Alternative: Use '/list-services' to see valid service names
```

### With Area Targeting

```bash
/review-service-operation "order-management" --area="fulfillment"
# Reviews only operations in fulfillment area for order-management service
# Filters operations by functional domain before validation
```