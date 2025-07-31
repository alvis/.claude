# Data Protection Standards

*Standards for input validation, data encryption, sanitization, and secure data handling*

## Core Data Protection Principles

### MUST Follow Rules
- **MUST validate all user input** - Never trust data from external sources
- **MUST sanitize data for output context** - Prevent XSS and injection attacks
- **MUST encrypt sensitive data at rest** - Use AES-256 or stronger
- **MUST use parameterized queries** - Prevent SQL injection
- **MUST sanitize logs** - Never log passwords, tokens, or PII

### SHOULD Follow Guidelines
- **SHOULD implement field-level encryption** - For highly sensitive data
- **SHOULD use content security policies** - Additional XSS protection
- **SHOULD validate data types and ranges** - Not just format
- **SHOULD implement rate limiting** - Prevent abuse

## Input Validation

### Validation Strategy

```typescript
interface ValidationRule<T> {
  validate(value: unknown): T;
  sanitize?(value: T): T;
}

class ValidationPipeline<T> {
  constructor(private rules: ValidationRule<any>[]) {}

  validate(value: unknown): T {
    return this.rules.reduce((acc, rule) => {
      const validated = rule.validate(acc);
      return rule.sanitize ? rule.sanitize(validated) : validated;
    }, value) as T;
  }
}
```

### Common Validators

```typescript
import validator from 'validator';

class Validators {
  static email(): ValidationRule<string> {
    return {
      validate(value: unknown): string {
        if (typeof value !== 'string') {
          throw new ValidationError('Email must be a string');
        }
        if (!validator.isEmail(value)) {
          throw new ValidationError('Invalid email format');
        }
        return value;
      },
      sanitize(value: string): string {
        return value.toLowerCase().trim();
      }
    };
  }

  static string(options: {
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    trim?: boolean;
  } = {}): ValidationRule<string> {
    return {
      validate(value: unknown): string {
        if (typeof value !== 'string') {
          throw new ValidationError('Value must be a string');
        }

        const str = options.trim !== false ? value.trim() : value;

        if (options.minLength && str.length < options.minLength) {
          throw new ValidationError(
            `Must be at least ${options.minLength} characters`
          );
        }

        if (options.maxLength && str.length > options.maxLength) {
          throw new ValidationError(
            `Must be no more than ${options.maxLength} characters`
          );
        }

        if (options.pattern && !options.pattern.test(str)) {
          throw new ValidationError('Invalid format');
        }

        return str;
      }
    };
  }

  static uuid(): ValidationRule<string> {
    return {
      validate(value: unknown): string {
        if (typeof value !== 'string' || !validator.isUUID(value)) {
          throw new ValidationError('Invalid UUID format');
        }
        return value;
      }
    };
  }

  static number(options: {
    min?: number;
    max?: number;
    integer?: boolean;
  } = {}): ValidationRule<number> {
    return {
      validate(value: unknown): number {
        const num = Number(value);
        
        if (isNaN(num)) {
          throw new ValidationError('Must be a number');
        }

        if (options.integer && !Number.isInteger(num)) {
          throw new ValidationError('Must be an integer');
        }

        if (options.min !== undefined && num < options.min) {
          throw new ValidationError(`Must be at least ${options.min}`);
        }

        if (options.max !== undefined && num > options.max) {
          throw new ValidationError(`Must be no more than ${options.max}`);
        }

        return num;
      }
    };
  }
}
```

### Request Validation

```typescript
interface RequestValidator {
  body?: Record<string, ValidationRule<any>>;
  query?: Record<string, ValidationRule<any>>;
  params?: Record<string, ValidationRule<any>>;
}

function validateRequest(schema: RequestValidator) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      // Validate body
      if (schema.body) {
        const validated: any = {};
        for (const [key, rule] of Object.entries(schema.body)) {
          validated[key] = rule.validate(req.body[key]);
        }
        req.body = validated;
      }

      // Validate query parameters
      if (schema.query) {
        const validated: any = {};
        for (const [key, rule] of Object.entries(schema.query)) {
          validated[key] = rule.validate(req.query[key]);
        }
        req.query = validated;
      }

      // Validate route parameters
      if (schema.params) {
        const validated: any = {};
        for (const [key, rule] of Object.entries(schema.params)) {
          validated[key] = rule.validate(req.params[key]);
        }
        req.params = validated;
      }

      next();
    } catch (error) {
      next(error);
    }
  };
}

// Usage
router.post('/users',
  validateRequest({
    body: {
      email: Validators.email(),
      name: Validators.string({ minLength: 2, maxLength: 100 }),
      age: Validators.number({ min: 18, max: 120, integer: true })
    }
  }),
  createUser
);
```

## SQL Injection Prevention

### Parameterized Queries

```typescript
class DatabaseService {
  // ✅ Good: Parameterized query
  async findUserByEmail(email: string): Promise<User | null> {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await this.pool.query(query, [email]);
    return result.rows[0] || null;
  }

  // ✅ Good: Multiple parameters
  async findUsers(filters: UserFilters): Promise<User[]> {
    const conditions: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (filters.name) {
      conditions.push(`name ILIKE $${paramIndex}`);
      values.push(`%${filters.name}%`);
      paramIndex++;
    }

    if (filters.email) {
      conditions.push(`email = $${paramIndex}`);
      values.push(filters.email);
      paramIndex++;
    }

    if (filters.role) {
      conditions.push(`role = $${paramIndex}`);
      values.push(filters.role);
      paramIndex++;
    }

    const query = `
      SELECT * FROM users
      ${conditions.length ? 'WHERE ' + conditions.join(' AND ') : ''}
      ORDER BY created_at DESC
    `;

    const result = await this.pool.query(query, values);
    return result.rows;
  }

  // ❌ Bad: String concatenation
  async unsafeQuery(table: string, id: string): Promise<any> {
    // NEVER DO THIS
    const query = `SELECT * FROM ${table} WHERE id = '${id}'`;
    return await this.pool.query(query);
  }
}
```

### Query Builders

```typescript
// Using Knex.js for safe query building
class UserRepository {
  async findWithFilters(filters: UserFilters): Promise<User[]> {
    let query = this.knex('users');

    if (filters.name) {
      query = query.where('name', 'like', `%${filters.name}%`);
    }

    if (filters.email) {
      query = query.where('email', filters.email);
    }

    if (filters.roles && filters.roles.length > 0) {
      query = query.whereIn('role', filters.roles);
    }

    if (filters.createdAfter) {
      query = query.where('created_at', '>=', filters.createdAfter);
    }

    return query.orderBy('created_at', 'desc');
  }
}
```

## XSS Prevention

### Output Encoding

```typescript
class XSSProtection {
  // HTML context
  static escapeHtml(str: string): string {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;',
    };
    return str.replace(/[&<>"'/]/g, char => map[char]);
  }

  // JavaScript context
  static escapeJs(str: string): string {
    return str
      .replace(/\\/g, '\\\\')
      .replace(/'/g, "\\'")
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t');
  }

  // URL context
  static escapeUrl(str: string): string {
    return encodeURIComponent(str);
  }

  // CSS context
  static escapeCss(str: string): string {
    return str.replace(/[^\w]/g, char => 
      '\\' + char.charCodeAt(0).toString(16).padStart(6, '0')
    );
  }
}
```

### Content Security Policy

```typescript
const cspDirectives = {
  defaultSrc: ["'self'"],
  scriptSrc: ["'self'", "'strict-dynamic'"],
  styleSrc: ["'self'", "'unsafe-inline'"],
  imgSrc: ["'self'", "https:", "data:"],
  fontSrc: ["'self'"],
  connectSrc: ["'self'"],
  mediaSrc: ["'none'"],
  objectSrc: ["'none'"],
  frameSrc: ["'none'"],
  workerSrc: ["'self'"],
  formAction: ["'self'"],
  frameAncestors: ["'none'"],
  baseUri: ["'self'"],
  manifestSrc: ["'self'"],
};

app.use(helmet.contentSecurityPolicy({
  directives: cspDirectives,
  reportOnly: false,
}));
```

## Data Encryption

### Encryption Service

```typescript
import crypto from 'crypto';

class EncryptionService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly keyLength = 32;
  private readonly ivLength = 16;
  private readonly tagLength = 16;
  private readonly saltLength = 64;
  private readonly iterations = 100000;

  private deriveKey(password: string, salt: Buffer): Buffer {
    return crypto.pbkdf2Sync(password, salt, this.iterations, this.keyLength, 'sha256');
  }

  encrypt(text: string, password: string): string {
    const salt = crypto.randomBytes(this.saltLength);
    const key = this.deriveKey(password, salt);
    const iv = crypto.randomBytes(this.ivLength);
    
    const cipher = crypto.createCipheriv(this.algorithm, key, iv);
    
    const encrypted = Buffer.concat([
      cipher.update(text, 'utf8'),
      cipher.final()
    ]);
    
    const tag = cipher.getAuthTag();
    
    const combined = Buffer.concat([salt, iv, tag, encrypted]);
    return combined.toString('base64');
  }

  decrypt(encryptedData: string, password: string): string {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const salt = combined.slice(0, this.saltLength);
    const iv = combined.slice(this.saltLength, this.saltLength + this.ivLength);
    const tag = combined.slice(
      this.saltLength + this.ivLength,
      this.saltLength + this.ivLength + this.tagLength
    );
    const encrypted = combined.slice(this.saltLength + this.ivLength + this.tagLength);
    
    const key = this.deriveKey(password, salt);
    
    const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return decrypted.toString('utf8');
  }
}
```

## Data Sanitization

### Log Sanitizer

```typescript
class LogSanitizer {
  private readonly sensitivePatterns = [
    /password["\s]*[:=]["\s]*["']?([^"',\s}]+)["']?/gi,
    /authorization["\s]*[:=]["\s]*["']?([^"',\s}]+)["']?/gi,
    /api[_-]?key["\s]*[:=]["\s]*["']?([^"',\s}]+)["']?/gi,
    /secret["\s]*[:=]["\s]*["']?([^"',\s}]+)["']?/gi,
    /token["\s]*[:=]["\s]*["']?([^"',\s}]+)["']?/gi,
    /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, // Credit card
    /\b\d{3}-\d{2}-\d{4}\b/g, // SSN
  ];

  sanitize(data: any): any {
    if (typeof data === 'string') {
      return this.sanitizeString(data);
    }

    if (typeof data !== 'object' || data === null) {
      return data;
    }

    if (Array.isArray(data)) {
      return data.map(item => this.sanitize(item));
    }

    const sanitized: any = {};
    for (const [key, value] of Object.entries(data)) {
      const sanitizedKey = this.sanitizeString(key);
      
      if (this.isSensitiveField(key)) {
        sanitized[sanitizedKey] = '[REDACTED]';
      } else {
        sanitized[sanitizedKey] = this.sanitize(value);
      }
    }

    return sanitized;
  }

  private sanitizeString(str: string): string {
    let sanitized = str;
    
    for (const pattern of this.sensitivePatterns) {
      sanitized = sanitized.replace(pattern, (match) => {
        const parts = match.split(/[:=]/);
        if (parts.length > 1) {
          return parts[0] + ': [REDACTED]';
        }
        return '[REDACTED]';
      });
    }
    
    return sanitized;
  }

  private isSensitiveField(fieldName: string): boolean {
    const sensitiveFields = [
      'password', 'token', 'secret', 'key', 'authorization',
      'cookie', 'session', 'ssn', 'creditCard', 'cvv', 'pin'
    ];
    
    const lowerField = fieldName.toLowerCase();
    return sensitiveFields.some(field => lowerField.includes(field));
  }
}
```

## Testing Data Protection

```typescript
describe('Data Protection', () => {
  describe('Input Validation', () => {
    it('should validate email addresses', () => {
      const validator = Validators.email();
      
      expect(() => validator.validate('invalid')).toThrow();
      expect(validator.validate('user@example.com')).toBe('user@example.com');
    });

    it('should prevent SQL injection', async () => {
      const maliciousInput = "'; DROP TABLE users; --";
      const result = await db.findUserByEmail(maliciousInput);
      
      expect(result).toBeNull();
      // Verify table still exists
      const tableExists = await db.query(
        "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'users')"
      );
      expect(tableExists.rows[0].exists).toBe(true);
    });
  });

  describe('Encryption', () => {
    it('should encrypt and decrypt data', () => {
      const service = new EncryptionService();
      const plaintext = 'sensitive data';
      const password = 'strong-password';
      
      const encrypted = service.encrypt(plaintext, password);
      expect(encrypted).not.toBe(plaintext);
      
      const decrypted = service.decrypt(encrypted, password);
      expect(decrypted).toBe(plaintext);
    });
  });

  describe('Sanitization', () => {
    it('should sanitize logs', () => {
      const sanitizer = new LogSanitizer();
      const input = {
        user: 'john@example.com',
        password: 'secret123',
        apiKey: 'sk_live_abcd1234',
      };
      
      const sanitized = sanitizer.sanitize(input);
      expect(sanitized.password).toBe('[REDACTED]');
      expect(sanitized.apiKey).toBe('[REDACTED]');
      expect(sanitized.user).toBe('john@example.com');
    });
  });
});
```

## References

- [Authentication Standards](./authentication.md)
- [OWASP Input Validation](https://owasp.org/www-community/controls/Input_Validation)
- [Encryption Best Practices](../code/security-patterns.md#encryption)