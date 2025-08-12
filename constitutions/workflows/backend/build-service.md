# Build Service

**Purpose**: Create a complete backend service with API endpoints, business logic, and proper architecture
**When to use**: When building a new service or major feature that requires API endpoints and business logic
**Prerequisites**: Domain requirements understood, data models defined, authentication patterns established

## Expert Role

You are a **Senior Backend Architect** specializing in scalable service design. Your expertise includes:

- **Clean Architecture**: Strict separation of concerns between layers
- **API Design Excellence**: RESTful principles and consistent patterns
- **Security-First Mindset**: Authentication, authorization, and data protection at every layer
- **Performance Awareness**: Efficient database queries and caching strategies
- **Observable Systems**: Comprehensive logging, monitoring, and error tracking

## Steps

### 1. Design Service Architecture

Plan the service structure following domain alignment:

```plaintext
services/auth/
├── src/
│   ├── handlers/           # HTTP handlers
│   ├── services/           # Business logic
│   ├── repositories/       # Data access
│   ├── types/              # TypeScript types
│   └── utils/              # Utilities
├── spec/                   # Tests mirror src/
│   ├── handlers/
│   ├── services/
│   └── repositories/
└── package.json
```

### 2. Create API Endpoints

Design RESTful API endpoints following standard conventions:

```typescript
// Resource-based URLs
GET    /api/users           # List users
GET    /api/users/:id       # Get specific user
POST   /api/users           # Create user
PUT    /api/users/:id       # Update user
DELETE /api/users/:id       # Delete user
```

### 3. Implement Request/Response Patterns

Use consistent API response structure:

```typescript
interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  meta?: {
    pagination?: PaginationMeta;
    timestamp: string;
  };
}
```

### 4. Create Handler Layer

Implement HTTP handlers following the standard pattern:

```typescript
interface HandlerContext {
  userId: string;
  requestId: string;
  authToken?: string;
}

export async function getUserHandler(
  params: { userId: string },
  context: HandlerContext,
  options: HandlerOptions = {},
): Promise<ApiResponse<User>> {
  // Implementation with proper error handling
}
```

### 5. Build Business Logic Layer

Create service classes that contain business logic:

- Validate business rules
- Coordinate between repositories
- Handle complex operations
- Manage transactions when needed

### 6. Implement Data Access Layer

Use repository pattern for data access:

- Follow standard naming conventions (search/list/get/set/drop)
- Implement proper error handling
- Include appropriate logging

### 7. Add Authentication & Authorization

Implement auth verification:

- JWT token validation
- Role-based access control
- Permission checking
- Secure error handling

### 8. Write Comprehensive Tests

Create test coverage for all layers:

- Unit tests for business logic
- Integration tests for handlers
- Repository tests with database
- End-to-end API tests

### 9. Add Monitoring & Logging

Implement observability:

- Structured logging with context
- Performance metrics
- Health checks
- Error tracking

## Recommended Tools

### Architecture Tools

- **Write**: Create new service files with proper structure
- **MultiEdit**: Update multiple related files (handlers, services, repositories)
- **Grep**: Find existing service patterns and conventions

### Development Tools

- **Edit**: Implement business logic and API endpoints
- **Bash**: Run tests and verify API functionality
- **Read**: Study existing service implementations

### Testing Tools

- **Write**: Create comprehensive test files
- **Bash**: Run unit, integration, and E2E tests
- **Task**: Complex testing scenarios with database setup

### Documentation Tools

- **Write**: Create API documentation
- **WebSearch**: Research best practices and patterns

### Tool Workflow

1. **Architecture**: Use Write to scaffold service structure
2. **Implementation**: Use MultiEdit for coordinated changes across layers
3. **Testing**: Use Bash for continuous test execution
4. **Verification**: Use Task for complex integration testing
5. **Documentation**: Use Write for API docs and examples

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [API Design Standards](../../standards/backend/api-design.md) - RESTful principles and API patterns
- [Data Operations Standards](../../standards/backend/data-operations.md) - Repository pattern and data access
- [Error Handling Standards](../../standards/backend/error-handling.md) - Error types and handling patterns
- [Security Standards](../../standards/backend/security.md) - Authentication and authorization patterns
- [TypeScript Standards](../../standards/code/typescript.md) - Type safety and TypeScript patterns
- [Naming Conventions](../../standards/code/naming.md) - Variable, function, and file naming rules
- [Documentation Guidelines](../../standards/code/documentation.md) - JSDoc and API documentation
- [Testing Standards](../../standards/quality/testing.md) - Test structure and coverage requirements

## Common Issues

- **Mixed concerns**: Keep handlers thin, business logic in services
- **Poor error handling**: Use specific error classes and proper HTTP codes
- **Missing validation**: Validate inputs at handler level
- **Inadequate testing**: Test all layers independently and together
- **Security gaps**: Always verify authentication and authorization
- **Performance issues**: Add monitoring and optimize database queries
