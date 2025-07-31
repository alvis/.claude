# Build Data Controller

**Purpose**: Create a complete data controller with repository pattern, validation, and error handling
**When to use**: When building a new data access layer for an entity or updating existing data operations
**Prerequisites**: Database schema defined, entity types created, validation requirements understood

## Steps

### 1. Design Repository Interface

Define the contract for data operations following standard naming conventions:

```typescript
interface EntityRepository<T, K = string> {
  // Read operations
  search(options: QueryOptions): Promise<T[]>;
  list(filter: Partial<T>): Promise<T[]>;
  get(identifier: K | { [key: string]: unknown }): Promise<T | null>;
  
  // Write operations
  set(entity: T): Promise<T>;
  drop(identifier: K): Promise<void>;
  
  // Batch operations
  setBatch(entities: T[]): Promise<T[]>;
  dropBatch(identifiers: K[]): Promise<void>;
}
```

### 2. Implement Repository

Create the database repository implementation:
- Use standard query structure with QueryOptions
- Handle both single and batch operations
- Include proper error handling and logging
- Map database results to domain entities

### 3. Create Data Controller

Build the controller layer that orchestrates business logic:
- Implement validation for all inputs
- Add structured logging with context
- Handle errors with appropriate classification
- Include pagination metadata for list operations

### 4. Add Validation Layer

Create input validation:
- Validate query options and filters
- Check required fields and formats
- Provide specific error messages with field names
- Support both full and partial validation

### 5. Write Tests

Create comprehensive test coverage:
- Unit tests for repository methods
- Controller integration tests
- Validation edge cases
- Error scenario handling

### 6. Verify Implementation

Ensure the implementation follows standards:
- Repository methods use correct naming (search/list/get/set/drop)
- QueryOptions structure is consistent
- Error handling uses specific error classes
- Logging includes proper context

## Standards to Follow

- [Data Operations Standards](../../standards/backend/data-operations.md)
- [Error Handling Standards](../../standards/backend/error-handling.md)
- [Testing Standards](../../standards/quality/testing.md)

## Common Issues

- **Mixed search/list logic**: Keep search (NLP) and list (filter) operations separate
- **Inconsistent error handling**: Use specific error classes, not generic Error
- **Missing validation**: Always validate inputs before processing
- **Poor test coverage**: Test both success and failure scenarios
- **Incomplete logging**: Include context like requestId, userId, operation name