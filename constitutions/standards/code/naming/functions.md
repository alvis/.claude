# Function Naming Standards

*Standards for naming functions, methods, and callable expressions*

## Core Function Naming Principles

### MUST Follow Rules
- **MUST start with a verb** - Functions perform actions
- **MUST use camelCase** - Consistent with JavaScript conventions
- **MUST be descriptive** - Clear about what the function does
- **MUST indicate async** - Async functions should be obvious
- **MUST follow conventions** - get, set, is, has patterns

### SHOULD Follow Guidelines
- **SHOULD be concise** - Balance clarity with brevity
- **SHOULD indicate return type** - Through naming patterns
- **SHOULD group related functions** - Common prefixes for related operations
- **SHOULD avoid side effects** in getter functions

## Verb Categories and Usage

### Data Retrieval Functions

```typescript
// get - Synchronous, immediate return (may be from cache)
function getUserName(user: User): string {
  return user.name;
}

function getCurrentTimestamp(): number {
  return Date.now();
}

// fetch - Asynchronous, external data source
async function fetchUserProfile(userId: string): Promise<UserProfile> {
  const response = await api.get(`/users/${userId}`);
  return response.data;
}

// find - Search operation, may return null
function findUserByEmail(users: User[], email: string): User | null {
  return users.find(u => u.email === email) || null;
}

// list - Return collection/array
function listActiveUsers(users: User[]): User[] {
  return users.filter(u => u.isActive);
}

// retrieve - Complex async operation, often with processing
async function retrieveUserDashboard(userId: string): Promise<Dashboard> {
  const [profile, stats, activity] = await Promise.all([
    fetchUserProfile(userId),
    fetchUserStats(userId),
    fetchRecentActivity(userId)
  ]);
  
  return composeDashboard(profile, stats, activity);
}
```

### Data Manipulation Functions

```typescript
// create - Make new instance
async function createUser(data: CreateUserData): Promise<User> {
  const user = new User(data);
  return await userRepository.save(user);
}

// add - Add to collection
function addItemToCart(cart: Cart, item: CartItem): Cart {
  return {
    ...cart,
    items: [...cart.items, item]
  };
}

// update - Modify existing
async function updateUserProfile(
  userId: string, 
  updates: Partial<UserProfile>
): Promise<UserProfile> {
  const user = await userRepository.findById(userId);
  Object.assign(user, updates);
  return await userRepository.save(user);
}

// set - Create or update (upsert)
async function setUserPreference(
  userId: string,
  key: string,
  value: any
): Promise<void> {
  await preferenceRepository.upsert({ userId, key, value });
}

// delete/remove - Eliminate
async function deleteUser(userId: string): Promise<void> {
  await userRepository.delete(userId);
}

function removeItemFromCart(cart: Cart, itemId: string): Cart {
  return {
    ...cart,
    items: cart.items.filter(item => item.id !== itemId)
  };
}
```

### Validation and Boolean Functions

```typescript
// validate - Full validation with detailed results
function validateUserInput(input: unknown): ValidationResult {
  const errors: ValidationError[] = [];
  
  if (!input || typeof input !== 'object') {
    errors.push({ field: 'input', message: 'Invalid input' });
  }
  
  // More validation...
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// is - Boolean state check
function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isUserActive(user: User): boolean {
  return user.status === 'active' && !user.deletedAt;
}

// has - Boolean possession check
function hasPermission(user: User, permission: string): boolean {
  return user.permissions.includes(permission);
}

function hasExpired(expiryDate: Date): boolean {
  return expiryDate < new Date();
}

// can - Boolean capability check
function canEditResource(user: User, resource: Resource): boolean {
  return user.id === resource.ownerId || user.role === 'admin';
}

// should - Boolean recommendation
function shouldRefreshToken(token: Token): boolean {
  const fiveMinutes = 5 * 60 * 1000;
  return token.expiresAt - Date.now() < fiveMinutes;
}
```

### Transformation Functions

```typescript
// transform - General transformation
function transformRawData(raw: RawData): ProcessedData {
  return {
    id: raw.id,
    name: raw.name.trim(),
    createdAt: new Date(raw.created_at)
  };
}

// convert - Type/format conversion
function convertCelsiusToFahrenheit(celsius: number): number {
  return (celsius * 9/5) + 32;
}

// parse - String to structured data
function parseConfigFile(content: string): Config {
  return JSON.parse(content);
}

// format - Structured data to string
function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(amount);
}

// serialize/deserialize - Object to string and back
function serializeUser(user: User): string {
  return JSON.stringify({
    id: user.id,
    name: user.name,
    email: user.email
  });
}

function deserializeUser(data: string): User {
  const parsed = JSON.parse(data);
  return new User(parsed);
}
```

### Action Functions

```typescript
// execute - Run a process
async function executePayment(payment: Payment): Promise<PaymentResult> {
  const result = await paymentGateway.process(payment);
  await recordTransaction(result);
  return result;
}

// process - Multi-step operation
async function processOrder(order: Order): Promise<ProcessedOrder> {
  await validateInventory(order.items);
  await calculatePricing(order);
  await applyDiscounts(order);
  return await finalizeOrder(order);
}

// handle - Event or request handling
async function handleLoginRequest(req: Request): Promise<Response> {
  const { email, password } = req.body;
  const user = await authenticateUser(email, password);
  const token = generateToken(user);
  return { user, token };
}

// trigger - Initiate an action
function triggerNotification(userId: string, message: string): void {
  eventEmitter.emit('notification', { userId, message });
}
```

## Async Function Patterns

### Naming Async Functions

```typescript
// ✅ Good: Clear async operations
async function fetchUserData(userId: string): Promise<UserData> { }
async function loadConfiguration(): Promise<Config> { }
async function saveDocument(doc: Document): Promise<void> { }
async function processPaymentAsync(payment: Payment): Promise<Result> { }

// Consider adding 'Async' suffix for clarity when needed
function processData(data: Data): ProcessedData { }
async function processDataAsync(data: Data): Promise<ProcessedData> { }

// ❌ Bad: Misleading async names
async function getUser(id: string): Promise<User> { } // 'get' implies sync
async function user(id: string): Promise<User> { }    // Not a verb
```

### Promise-Returning Functions

```typescript
// ✅ Good: Clear promise returns
function delayExecution(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function waitForCondition(
  condition: () => boolean,
  timeout: number = 5000
): Promise<void> {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const check = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - start > timeout) {
        reject(new Error('Timeout waiting for condition'));
      } else {
        setTimeout(check, 100);
      }
    };
    check();
  });
}
```

## Method Naming in Classes

### Standard Method Patterns

```typescript
class UserService {
  // Getters - no 'get' prefix for property-like access
  get activeUsers(): User[] {
    return this.users.filter(u => u.isActive);
  }

  // Standard methods - use verb prefixes
  async createUser(data: CreateUserData): Promise<User> {
    return this.repository.create(data);
  }

  findUserByEmail(email: string): User | null {
    return this.users.find(u => u.email === email) || null;
  }

  async updateUser(id: string, updates: Partial<User>): Promise<User> {
    return this.repository.update(id, updates);
  }

  // Private methods - same rules apply
  private validateUserData(data: unknown): void {
    // Validation logic
  }

  private async notifyUserCreated(user: User): Promise<void> {
    // Notification logic
  }
}
```

### Lifecycle Methods

```typescript
class Component {
  // Standard lifecycle names
  async initialize(): Promise<void> { }
  async onMount(): Promise<void> { }
  async beforeUpdate(): Promise<void> { }
  async afterUpdate(): Promise<void> { }
  async onUnmount(): Promise<void> { }
  async dispose(): Promise<void> { }

  // React-style lifecycle
  componentDidMount(): void { }
  componentWillUnmount(): void { }
  shouldComponentUpdate(): boolean { return true; }
}
```

## Factory and Builder Functions

### Factory Functions

```typescript
// ✅ Good: Clear factory patterns
function createUser(data: CreateUserData): User {
  return new User(data);
}

function createDefaultConfig(): Config {
  return {
    port: 3000,
    host: 'localhost',
    debug: false
  };
}

// Factory with options
function createLogger(options: LoggerOptions = {}): Logger {
  return new Logger({
    level: options.level || 'info',
    format: options.format || 'json',
    ...options
  });
}

// Higher-order factory
function createServiceFactory<T>(ServiceClass: new () => T) {
  return (config: Config): T => {
    const service = new ServiceClass();
    service.configure(config);
    return service;
  };
}
```

### Builder Functions

```typescript
// ✅ Good: Builder pattern
function buildQueryString(params: Record<string, any>): string {
  return Object.entries(params)
    .filter(([_, value]) => value != null)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&');
}

function buildEmailMessage(options: EmailOptions): EmailMessage {
  return {
    to: options.to,
    from: options.from || 'noreply@example.com',
    subject: options.subject,
    body: options.template 
      ? renderTemplate(options.template, options.data)
      : options.body
  };
}
```

## Event Handlers and Callbacks

### Event Handler Naming

```typescript
// ✅ Good: Event handler patterns
function handleClick(event: MouseEvent): void { }
function handleSubmit(event: FormEvent): void { }
function handleChange(event: ChangeEvent): void { }
function handleUserLogin(user: User): void { }
function handleError(error: Error): void { }

// With 'on' prefix for props/callbacks
interface ButtonProps {
  onClick: (event: MouseEvent) => void;
  onHover: (hovering: boolean) => void;
  onFocus: () => void;
}

// Event emitter patterns
emitter.on('data', handleData);
emitter.on('error', handleError);
emitter.on('close', handleClose);
```

### Callback Patterns

```typescript
// ✅ Good: Callback naming
type OnSuccess<T> = (result: T) => void;
type OnError = (error: Error) => void;
type OnProgress = (progress: number) => void;
type OnComplete = () => void;

interface AsyncOperationOptions<T> {
  onSuccess?: OnSuccess<T>;
  onError?: OnError;
  onProgress?: OnProgress;
  onComplete?: OnComplete;
}

// Usage
async function uploadFile(
  file: File,
  options: AsyncOperationOptions<string>
): Promise<string> {
  try {
    // Upload logic with progress
    options.onProgress?.(0.5);
    const url = await upload(file);
    options.onSuccess?.(url);
    return url;
  } catch (error) {
    options.onError?.(error);
    throw error;
  } finally {
    options.onComplete?.();
  }
}
```

## Utility and Helper Functions

### Pure Utility Functions

```typescript
// ✅ Good: Utility function naming
function capitalizeFirstLetter(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): T {
  let timeout: NodeJS.Timeout;
  return ((...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  }) as T;
}

function groupBy<T, K extends keyof T>(
  array: T[],
  key: K
): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const group = String(item[key]);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

// ❌ Bad: Vague utility names
function process(data: any): any { }  // Too generic
function util(x: any): any { }        // Meaningless
function doStuff(): void { }          // No indication of purpose
```

## Anti-Patterns to Avoid

```typescript
// ❌ Bad: Poor function naming

// No verb
function user(id: string): User { }           // Should be getUser
function validation(data: any): boolean { }    // Should be validate

// Wrong verb
function getUsers(user: User): void { }        // 'get' but returns void
function createUsersList(): User { }           // 'create' but returns single

// Too generic
function process(data: any): any { }
function handle(thing: any): void { }
function execute(): void { }

// Misleading
function saveUser(user: User): User {
  return { ...user };  // Doesn't actually save
}

// Hungarian notation
function fnGetUser(): User { }                 // 'fn' prefix unnecessary
function cbHandleClick(): void { }             // 'cb' prefix unnecessary

// Overly abbreviated
function gUsr(id: string): User { }            // Write it out
function procPmt(p: Payment): void { }         // Unclear
```

## Testing Function Names

```typescript
// ✅ Good: Test function naming
describe('UserService', () => {
  // Setup functions
  function createMockUser(): User { }
  function setupTestDatabase(): void { }
  function cleanupTestData(): void { }

  // Assertion helpers
  function expectUserToBeValid(user: User): void { }
  function assertEmailSent(email: string): void { }

  // Test cases - descriptive names
  it('should create user when valid data provided', () => { });
  it('should throw ValidationError when email is invalid', () => { });
  it('should return null when user not found', () => { });
});
```

## References

- [Variable Naming](./variables.md) - Variable conventions
- [Type Naming](./types.md) - Class and method naming
- [Patterns](./patterns.md) - Common naming patterns