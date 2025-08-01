# Type Naming Standards

_Standards for naming classes, interfaces, types, and enums in TypeScript_

## Core Type Naming Principles

### MUST Follow Rules

- **MUST use PascalCase** for all types, interfaces, classes, and enums
- **MUST use noun phrases** for types and interfaces
- **MUST avoid prefixes** like 'I' for interfaces or 'T' for types
- **MUST be descriptive** without being redundant
- **MUST use singular names** for types (unless representing collections)

### SHOULD Follow Guidelines

- **SHOULD use suffixes** to clarify purpose (Service, Repository, Config)
- **SHOULD group related types** with consistent naming patterns
- **SHOULD use generic type parameters** starting with T (T, U, V, K)
- **SHOULD match domain language** in type names

## Interface Naming

### Basic Interfaces

```typescript
// ✅ Good: Clear, descriptive interface names
interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
}

interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
  timestamp: Date;
}

// ❌ Bad: Poor interface naming
interface IUser {} // Don't use 'I' prefix
interface UserInterface {} // Redundant 'Interface' suffix
interface UserType {} // Confusing with type aliases
interface Data {} // Too generic
```

### Domain-Specific Interfaces

```typescript
// ✅ Good: Domain-specific naming
interface Order {
  id: string;
  customerId: string;
  items: OrderItem[];
  total: number;
}

interface PaymentMethod {
  id: string;
  type: "credit_card" | "paypal" | "bank_transfer";
  lastFourDigits?: string;
}

interface ShippingAddress {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

// ✅ Good: Configuration interfaces
interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  ssl?: boolean;
}

interface AuthConfig {
  jwtSecret: string;
  tokenExpiry: string;
  refreshTokenExpiry: string;
}
```

### Request/Response Interfaces

```typescript
// ✅ Good: Clear request/response naming
interface CreateUserRequest {
  email: string;
  password: string;
  name: string;
}

interface CreateUserResponse {
  user: User;
  token: string;
}

interface UpdateProductRequest {
  name?: string;
  price?: number;
  description?: string;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
}

// ❌ Bad: Unclear request/response names
interface UserData {} // Is this request or response?
interface ProductInfo {} // Too vague
```

## Type Alias Naming

### Union and Intersection Types

```typescript
// ✅ Good: Descriptive type aliases
type UserId = string;
type Email = string;
type IsoDateString = string;

type UserRole = "admin" | "editor" | "viewer";
type PaymentStatus = "pending" | "processing" | "completed" | "failed";
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

// ✅ Good: Complex type compositions
type UserWithRoles = User & { roles: UserRole[] };
type PartialUser = Partial<User>;
type ReadonlyUser = Readonly<User>;

// ✅ Good: Discriminated unions
type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: string };

type PaymentResult =
  | { status: "success"; transactionId: string }
  | { status: "failed"; reason: string }
  | { status: "pending"; estimatedTime: number };

// ❌ Bad: Confusing or redundant names
type TUser = User; // Redundant 'T' prefix
type UserType = User; // Redundant 'Type' suffix
type StringType = string; // Unnecessary aliasing
```

### Function Types

```typescript
// ✅ Good: Clear function type names
type UserValidator = (user: User) => ValidationResult;
type EventHandler<T> = (event: T) => void;
type AsyncOperation<T> = () => Promise<T>;
type Middleware = (req: Request, res: Response, next: NextFunction) => void;

// ✅ Good: Callback patterns
type OnSuccess<T> = (result: T) => void;
type OnError = (error: Error) => void;
type ProgressCallback = (progress: number) => void;

// ❌ Bad: Unclear function types
type Function1 = (x: any) => any; // Too generic
type Callback = Function; // No type information
```

## Class Naming

### Service Classes

```typescript
// ✅ Good: Service class naming
class UserService {
  constructor(private repository: UserRepository) {}

  async createUser(data: CreateUserData): Promise<User> {
    // Implementation
  }
}

class EmailService {
  async sendEmail(to: string, subject: string, body: string): Promise<void> {
    // Implementation
  }
}

class AuthenticationService {
  async authenticate(credentials: Credentials): Promise<AuthResult> {
    // Implementation
  }
}

// ❌ Bad: Poor service naming
class UserManager {} // Vague responsibility
class UserHelper {} // Suggests utility rather than service
class ProcessUser {} // Verb-based name
class UserUtils {} // Should be functions, not a class
```

### Repository Classes

```typescript
// ✅ Good: Repository pattern naming
class UserRepository {
  async findById(id: string): Promise<User | null> {
    // Implementation
  }

  async save(user: User): Promise<User> {
    // Implementation
  }
}

class OrderRepository {
  async findByCustomerId(customerId: string): Promise<Order[]> {
    // Implementation
  }
}

// ✅ Good: Specific repository implementations
class PostgresUserRepository implements UserRepository {
  // PostgreSQL-specific implementation
}

class MongoOrderRepository implements OrderRepository {
  // MongoDB-specific implementation
}
```

### Component Classes

```typescript
// ✅ Good: Component naming (React/Angular/Vue)
class UserProfileComponent {}
class NavigationBar {}
class ShoppingCartWidget {}
class PaymentForm {}

// For React functional components
const UserProfile: React.FC<UserProfileProps> = (props) => {};
const ProductCard: React.FC<ProductCardProps> = (props) => {};

// ❌ Bad: Generic component names
class Component1 {}
class MyComponent {}
class Comp {}
```

## Enum Naming

### Standard Enums

```typescript
// ✅ Good: Enum naming patterns
enum UserRole {
  Admin = "ADMIN",
  Editor = "EDITOR",
  Viewer = "VIEWER",
}

enum HttpStatus {
  Ok = 200,
  Created = 201,
  BadRequest = 400,
  Unauthorized = 401,
  NotFound = 404,
  InternalServerError = 500,
}

enum LogLevel {
  Debug = "DEBUG",
  Info = "INFO",
  Warning = "WARNING",
  Error = "ERROR",
  Critical = "CRITICAL",
}

// ✅ Good: Const assertions as enums
const OrderStatus = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
} as const;

type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];

// ❌ Bad: Poor enum naming
enum status {} // Should be PascalCase
enum USER_ROLE {} // Should be PascalCase, not UPPER_SNAKE
enum EUserRole {} // Don't use 'E' prefix
```

## Generic Type Parameters

### Standard Generic Patterns

```typescript
// ✅ Good: Generic type parameter naming
interface Container<T> {
  value: T;
  getValue(): T;
  setValue(value: T): void;
}

interface KeyValuePair<K, V> {
  key: K;
  value: V;
}

class EventEmitter<TEvents extends Record<string, any>> {
  on<K extends keyof TEvents>(
    event: K,
    handler: (data: TEvents[K]) => void,
  ): void {
    // Implementation
  }
}

// ✅ Good: Descriptive generic constraints
interface Repository<TEntity extends { id: string }> {
  findById(id: string): Promise<TEntity | null>;
  save(entity: TEntity): Promise<TEntity>;
}

type AsyncFunction<TArgs extends any[], TReturn> = (
  ...args: TArgs
) => Promise<TReturn>;

// ❌ Bad: Poor generic naming
interface Container<Type> {} // Use single letter T
interface Map<KeyType, ValueType> {} // Too verbose
interface Data<X, Y, Z> {} // Non-standard letters without reason
```

## Namespace and Module Naming

```typescript
// ✅ Good: Namespace organization
namespace Api {
  export interface User {}
  export interface Product {}

  export namespace V1 {
    export interface Response {}
  }
}

namespace Database {
  export interface Config {}
  export interface Connection {}
}

// ✅ Good: Module exports
export interface UserModule {
  UserService: typeof UserService;
  UserRepository: typeof UserRepository;
  UserController: typeof UserController;
}
```

## Error and Exception Types

```typescript
// ✅ Good: Error class naming
class ValidationError extends Error {
  constructor(
    public field: string,
    message: string,
  ) {
    super(message);
  }
}

class AuthenticationError extends Error {}
class AuthorizationError extends Error {}
class NotFoundError extends Error {}
class ConflictError extends Error {}

// ✅ Good: Error type definitions
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: Date;
}

type ErrorCode =
  | "INVALID_INPUT"
  | "UNAUTHORIZED"
  | "FORBIDDEN"
  | "NOT_FOUND"
  | "INTERNAL_ERROR";
```

## Testing Type Names

```typescript
// ✅ Good: Test-specific type naming
interface MockUser extends User {
  _isMock: true;
}

type TestCase<TInput, TExpected> = {
  name: string;
  input: TInput;
  expected: TExpected;
};

interface TestFixture {
  users: User[];
  products: Product[];
  orders: Order[];
}

class UserServiceStub implements UserService {
  // Test implementation
}
```

## Anti-Patterns to Avoid

```typescript
// ❌ Bad: Common type naming mistakes
interface IUserService {} // Don't use 'I' prefix
type TUser = User; // Don't use 'T' prefix for aliases
class userService {} // Should be PascalCase
enum user_role {} // Should be PascalCase

interface UserInterface {} // Redundant suffix
type UserType = User; // Redundant suffix
class ServiceClass {} // Generic name

type str = string; // Unnecessary aliasing
type num = number; // Don't abbreviate
type bool = boolean; // Pointless renaming

interface Data {} // Too generic
interface Info {} // Too vague
interface Object {} // Conflicts with built-in
```

## References

- [Variable Naming](./variables.md) - Variable naming patterns
- [Function Naming](./functions.md) - Function and method naming
- [TypeScript Standards](../typescript.md) - TypeScript best practices
