# Verify Authentication & Authorization Scope

**Purpose**: Implement proper authentication token verification and authorization scope checking in services
**When to use**: In every service handler that requires user authentication or specific permissions
**Prerequisites**: JWT tokens configured, user roles/permissions defined, auth service available

## Steps

### 1. Verify JWT Token

Validate the authentication token:

```typescript
async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET) as JWTPayload;
    
    // Check expiration
    if (Date.now() >= payload.exp * 1000) {
      throw new AuthenticationError('Token expired');
    }
    
    return payload;
  } catch (error) {
    throw new AuthenticationError('Invalid token');
  }
}
```

### 2. Extract User Context

Get user information from verified token:

```typescript
interface AuthContext {
  user: JWTPayload;
  roles: string[];
  permissions: string[];
}

async function buildAuthContext(token: string): Promise<AuthContext> {
  const user = await verifyToken(token);
  const roles = await getUserRoles(user.userId);
  const permissions = await getUserPermissions(user.userId);
  
  return { user, roles, permissions };
}
```

### 3. Check Required Roles

Verify user has required role:

```typescript
function requireRole(requiredRole: string) {
  return (context: AuthContext) => {
    if (!context.roles.includes(requiredRole)) {
      throw new AuthorizationError(`Role ${requiredRole} required`);
    }
  };
}

// Usage in handler
const authContext = await buildAuthContext(authToken);
requireRole('admin')(authContext);
```

### 4. Check Specific Permissions

Verify user has specific permission:

```typescript
function requirePermission(permission: string) {
  return (context: AuthContext) => {
    if (!context.permissions.includes(permission)) {
      throw new AuthorizationError(`Permission ${permission} required`);
    }
  };
}

// Usage in handler
requirePermission('user:read')(authContext);
```

### 5. Resource-Level Authorization

Check if user can access specific resources:

```typescript
async function canAccessResource(
  userId: string, 
  resourceId: string, 
  action: string
): Promise<boolean> {
  // Check if user owns the resource
  if (await isResourceOwner(userId, resourceId)) {
    return true;
  }
  
  // Check if user has admin role
  if (await hasRole(userId, 'admin')) {
    return true;
  }
  
  // Check specific permission for this resource type
  const permission = `${getResourceType(resourceId)}:${action}`;
  return hasPermission(userId, permission);
}
```

### 6. Implement in Service Handlers

Apply auth checks in handler functions:

```typescript
export async function getUserHandler(
  params: { userId: string },
  context: HandlerContext
): Promise<ApiResponse<User>> {
  try {
    // 1. Verify authentication
    const authContext = await buildAuthContext(context.authToken);
    
    // 2. Check permission
    requirePermission('user:read')(authContext);
    
    // 3. Check resource access
    if (!await canAccessResource(authContext.user.userId, params.userId, 'read')) {
      throw new ForbiddenError('Cannot access this user');
    }
    
    // 4. Execute business logic
    const user = await userService.getUser(params.userId);
    
    return {
      status: 'success',
      data: user,
      meta: { timestamp: new Date().toISOString() }
    };
  } catch (error) {
    return transformError(error);
  }
}
```

### 7. Handle Auth Errors Properly

Transform auth errors to appropriate HTTP responses:

```typescript
function transformAuthError(error: unknown): ApiResponse<never> {
  if (error instanceof AuthenticationError) {
    return {
      status: 'error',
      error: {
        code: 'AUTHENTICATION_REQUIRED',
        message: 'Valid authentication token required',
      }
    };
  }

  if (error instanceof AuthorizationError) {
    return {
      status: 'error',
      error: {
        code: 'INSUFFICIENT_PERMISSIONS',
        message: 'Insufficient permissions for this action',
      }
    };
  }

  // Default to internal server error
  return {
    status: 'error',
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    }
  };
}
```

### 8. Add Logging for Security Events

Log authentication and authorization events:

```typescript
function logAuthEvent(
  event: 'auth_success' | 'auth_failure' | 'authz_failure',
  context: {
    userId?: string;
    action: string;
    resource?: string;
    ip?: string;
    userAgent?: string;
  }
): void {
  logger.info(`Security event: ${event}`, {
    event,
    timestamp: new Date().toISOString(),
    ...context
  });
}
```

## Standards to Follow

- [Security Standards](../../standards/backend/security.md)
- [Error Handling Standards](../../standards/backend/error-handling.md)
- [API Design Standards](../../standards/backend/api-design.md)

## Common Issues

- **Token validation errors**: Ensure proper JWT secret and expiration handling
- **Missing permission checks**: Every protected endpoint needs authorization
- **Generic error messages**: Don't reveal internal auth details to clients
- **Logging sensitive data**: Never log tokens or passwords
- **Resource leakage**: Always check resource-level permissions
- **Performance issues**: Cache role/permission lookups appropriately