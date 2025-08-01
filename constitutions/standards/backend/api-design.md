# API Design Standards

_Standards for RESTful API design, request/response patterns, and service architecture_

## RESTful Conventions

### Resource-Based URLs

```typescript
// ✅ Good: Resource-based URLs
GET    /api/users           # List users
GET    /api/users/:id       # Get specific user
POST   /api/users           # Create user
PUT    /api/users/:id       # Update user
DELETE /api/users/:id       # Delete user

// ✅ Good: Nested resources
GET    /api/users/:id/posts        # Get user's posts
POST   /api/users/:id/posts        # Create post for user
GET    /api/posts/:id/comments     # Get post's comments

// ❌ Avoid: Action-based URLs
POST   /api/createUser
GET    /api/getUserById/:id
POST   /api/updateUserStatus
```

### HTTP Methods

- **GET**: Retrieve data (safe, idempotent)
- **POST**: Create resources (not idempotent)
- **PUT**: Update/replace entire resource (idempotent)
- **PATCH**: Partial updates (not necessarily idempotent)
- **DELETE**: Remove resources (idempotent)

### Status Codes

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server errors

## Request/Response Patterns

### Standard API Response

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

### Pagination Metadata

```typescript
interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}
```

### Success Responses

```typescript
// Single resource
{
  "status": "success",
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

// Collection with pagination
{
  "status": "success",
  "data": [
    { "id": "123", "name": "John Doe" },
    { "id": "124", "name": "Jane Smith" }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 157,
      "hasMore": true
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Responses

```typescript
// Validation error
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}

// Authentication error
{
  "status": "error",
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required"
  }
}

// Authorization error
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Insufficient permissions for this action"
  }
}
```

## Handler Pattern

### Handler Interface

```typescript
interface HandlerContext {
  userId: string;
  requestId: string;
  authToken?: string;
}

interface HandlerOptions {
  timeout?: number;
  retries?: number;
}

type HandlerFunction<TParams, TResult> = (
  params: TParams,
  context: HandlerContext,
  options?: HandlerOptions,
) => Promise<ApiResponse<TResult>>;
```

### Handler Implementation

```typescript
export async function getUserHandler(
  params: { userId: string },
  context: HandlerContext,
  options: HandlerOptions = {},
): Promise<ApiResponse<User>> {
  try {
    // 1. Validate input
    validateUserId(params.userId);

    // 2. Check authorization
    await requirePermission("user:read", context);

    // 3. Execute business logic
    const user = await userService.getUser(params.userId);

    // 4. Return success response
    return {
      status: "success",
      data: user,
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  } catch (error) {
    // 5. Transform and return error
    return transformError(error);
  }
}
```

## Service Architecture

### Layered Architecture

```typescript
// Handler Layer - HTTP concerns
class UserHandler {
  async getUser(req: Request, res: Response): Promise<void> {
    const result = await getUserHandler(
      { userId: req.params.id },
      { userId: req.user.id, requestId: req.id },
    );

    if (result.status === "error") {
      res.status(getHttpStatusCode(result.error?.code)).json(result);
    } else {
      res.status(200).json(result);
    }
  }
}

// Service Layer - Business logic
class UserService {
  constructor(
    private userRepository: UserRepository,
    private validator: UserValidator,
  ) {}

  async getUser(userId: string): Promise<User> {
    this.validator.validateId(userId);

    const user = await this.userRepository.get({ id: userId });
    if (!user) {
      throw new NotFoundError("User", userId);
    }

    return user;
  }
}

// Repository Layer - Data access
class UserRepository {
  async get(identifier: { id: string }): Promise<User | null> {
    const result = await this.db.query("SELECT * FROM users WHERE id = $1", [
      identifier.id,
    ]);

    return result.rows[0] ? this.mapToUser(result.rows[0]) : null;
  }
}
```

## Domain Alignment

### Service Structure

Services, data, and manifests align by domain:

```plaintext
services/profile/
data/profile/
manifests/profile/
infrastructure/profile/
```

### Directory Organization

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

## Query Parameters

### Standard Query Parameters

```typescript
interface QueryParams {
  // Pagination
  page?: number; // Page number (1-based)
  limit?: number; // Items per page
  offset?: number; // Items to skip

  // Sorting
  sort?: string; // Sort field
  order?: "asc" | "desc"; // Sort direction

  // Filtering
  filter?: string; // JSON-encoded filter object
  search?: string; // Search query

  // Response formatting
  fields?: string; // Comma-separated field list
  include?: string; // Related resources to include
}
```

### Example Usage

```bash
# Pagination
GET /api/users?page=2&limit=50

# Sorting
GET /api/users?sort=createdAt&order=desc

# Filtering
GET /api/users?filter={"active":true,"role":"admin"}

# Search
GET /api/users?search=john@example.com

# Field selection
GET /api/users?fields=id,name,email

# Include related data
GET /api/users?include=profile,preferences
```

## Content Negotiation

### Request Headers

```typescript
// Content type for request body
'Content-Type': 'application/json'

// Accepted response format
'Accept': 'application/json'

// API versioning
'Accept-Version': 'v1'

// Authentication
'Authorization': 'Bearer <token>'

// Request tracking
'X-Request-ID': '<uuid>'
```

### Response Headers

```typescript
// Content type
'Content-Type': 'application/json; charset=utf-8'

// API version
'X-API-Version': 'v1'

// Request tracking
'X-Request-ID': '<uuid>'

// Rate limiting
'X-RateLimit-Limit': '1000'
'X-RateLimit-Remaining': '999'
'X-RateLimit-Reset': '1642681200'

// Caching
'Cache-Control': 'private, max-age=300'
'ETag': '"abc123"'
```

## Versioning Strategy

### URL Versioning (Preferred)

```typescript
// Version in URL path
GET /api/v1/users
GET /api/v2/users

// Version in subdomain
GET https://v1.api.example.com/users
GET https://v2.api.example.com/users
```

### Header Versioning

```typescript
// Version in Accept header
Accept: application/vnd.api.v1+json
Accept: application/vnd.api.v2+json

// Version in custom header
X-API-Version: v1
X-API-Version: v2
```

## Rate Limiting

### Rate Limit Headers

```typescript
interface RateLimitHeaders {
  "X-RateLimit-Limit": string; // Total requests allowed
  "X-RateLimit-Remaining": string; // Requests remaining
  "X-RateLimit-Reset": string; // Reset timestamp
  "X-RateLimit-Window": string; // Window duration
}
```

### Rate Limit Response

```typescript
// When rate limit exceeded
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests, please try again later",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "resetAt": "2024-01-15T11:00:00Z"
    }
  }
}
```

## Documentation Standards

### OpenAPI/Swagger

Document all endpoints with:

- Request/response schemas
- Authentication requirements
- Error responses
- Example requests/responses
- Parameter descriptions

### Endpoint Documentation

```yaml
/api/users/{id}:
  get:
    summary: Get user by ID
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: User found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UserResponse"
      404:
        description: User not found
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```
