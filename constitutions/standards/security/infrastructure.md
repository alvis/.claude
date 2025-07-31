# Infrastructure Security Standards

*Standards for security headers, rate limiting, CORS, and infrastructure protection*

## Core Infrastructure Security Principles

### MUST Follow Rules
- **MUST implement security headers** - All responses must include security headers
- **MUST use HTTPS everywhere** - No exceptions for production traffic
- **MUST implement rate limiting** - Protect against abuse and DoS
- **MUST configure CORS properly** - Prevent unauthorized cross-origin requests
- **MUST disable unnecessary features** - Reduce attack surface

### SHOULD Follow Guidelines
- **SHOULD use Web Application Firewall** - Additional layer of protection
- **SHOULD implement DDoS protection** - For critical services
- **SHOULD monitor for anomalies** - Detect attacks early
- **SHOULD use secure defaults** - Fail closed, not open

## Security Headers

### Essential Security Headers

```typescript
interface SecurityHeaders {
  'Content-Security-Policy': string;
  'X-Frame-Options': string;
  'X-Content-Type-Options': string;
  'Referrer-Policy': string;
  'Permissions-Policy': string;
  'Strict-Transport-Security': string;
  'X-XSS-Protection': string;
}

export const securityHeaders: SecurityHeaders = {
  // Prevent XSS attacks
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' 'strict-dynamic'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self'",
    "connect-src 'self' wss:",
    "media-src 'none'",
    "object-src 'none'",
    "frame-src 'none'",
    "worker-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "manifest-src 'self'"
  ].join('; '),
  
  // Prevent clickjacking
  'X-Frame-Options': 'DENY',
  
  // Prevent MIME type sniffing
  'X-Content-Type-Options': 'nosniff',
  
  // Control referrer information
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // Control browser features
  'Permissions-Policy': [
    'camera=()',
    'microphone=()',
    'geolocation=()',
    'payment=()',
    'usb=()',
    'magnetometer=()',
    'accelerometer=()'
  ].join(', '),
  
  // Force HTTPS
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  
  // Legacy XSS protection
  'X-XSS-Protection': '1; mode=block'
};
```

### Implementing Security Headers

```typescript
import helmet from 'helmet';

// Express middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'strict-dynamic'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "wss:"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'none'"],
      frameSrc: ["'none'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));

// Manual implementation
app.use((req, res, next) => {
  Object.entries(securityHeaders).forEach(([header, value]) => {
    res.setHeader(header, value);
  });
  next();
});
```

## Rate Limiting

### Rate Limiter Implementation

```typescript
interface RateLimitOptions {
  windowMs: number;
  maxRequests: number;
  keyGenerator?: (req: Request) => string;
  skipSuccessfulRequests?: boolean;
  skipFailedRequests?: boolean;
}

class RateLimiter {
  private store: Map<string, RateLimitEntry> = new Map();

  constructor(private options: RateLimitOptions) {
    // Clean up expired entries periodically
    setInterval(() => this.cleanup(), options.windowMs);
  }

  async isAllowed(key: string): Promise<RateLimitResult> {
    const now = Date.now();
    const windowStart = now - this.options.windowMs;

    let entry = this.store.get(key);
    
    if (!entry || entry.resetTime < now) {
      entry = {
        count: 0,
        resetTime: now + this.options.windowMs,
        firstRequestTime: now
      };
      this.store.set(key, entry);
    }

    // Remove old requests outside the window
    if (entry.firstRequestTime < windowStart) {
      entry.count = 0;
      entry.firstRequestTime = now;
    }

    entry.count++;

    const allowed = entry.count <= this.options.maxRequests;
    const remaining = Math.max(0, this.options.maxRequests - entry.count);
    const resetTime = entry.resetTime;

    return {
      allowed,
      remaining,
      resetTime,
      retryAfter: allowed ? undefined : Math.ceil((resetTime - now) / 1000)
    };
  }

  private cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.store.entries()) {
      if (entry.resetTime < now) {
        this.store.delete(key);
      }
    }
  }
}

// Redis-based rate limiter for distributed systems
class RedisRateLimiter {
  constructor(
    private redis: Redis,
    private options: RateLimitOptions
  ) {}

  async isAllowed(key: string): Promise<RateLimitResult> {
    const now = Date.now();
    const window = Math.floor(now / this.options.windowMs);
    const redisKey = `rate_limit:${key}:${window}`;

    const pipeline = this.redis.pipeline();
    pipeline.incr(redisKey);
    pipeline.expire(redisKey, Math.ceil(this.options.windowMs / 1000) + 1);
    
    const results = await pipeline.exec();
    const count = results?.[0]?.[1] as number || 0;

    const allowed = count <= this.options.maxRequests;
    const remaining = Math.max(0, this.options.maxRequests - count);
    const resetTime = (window + 1) * this.options.windowMs;

    return {
      allowed,
      remaining,
      resetTime,
      retryAfter: allowed ? undefined : Math.ceil((resetTime - now) / 1000)
    };
  }
}
```

### Rate Limiting Middleware

```typescript
function createRateLimitMiddleware(options: RateLimitOptions) {
  const limiter = new RateLimiter(options);

  return async (req: Request, res: Response, next: NextFunction) => {
    const key = options.keyGenerator?.(req) || req.ip;
    const result = await limiter.isAllowed(key);

    // Set rate limit headers
    res.setHeader('X-RateLimit-Limit', options.maxRequests.toString());
    res.setHeader('X-RateLimit-Remaining', result.remaining.toString());
    res.setHeader('X-RateLimit-Reset', result.resetTime.toString());

    if (!result.allowed) {
      res.setHeader('Retry-After', result.retryAfter!.toString());
      return res.status(429).json({
        error: 'Too Many Requests',
        message: 'Rate limit exceeded',
        retryAfter: result.retryAfter
      });
    }

    next();
  };
}

// Usage with different limits
app.use('/api', createRateLimitMiddleware({
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 100,
  keyGenerator: (req) => req.user?.id || req.ip
}));

app.use('/api/auth/login', createRateLimitMiddleware({
  windowMs: 15 * 60 * 1000, // 15 minutes
  maxRequests: 5, // Strict limit for login attempts
  skipSuccessfulRequests: true
}));
```

## CORS Configuration

### Secure CORS Setup

```typescript
import cors from 'cors';

interface CorsOptions {
  origin: string | string[] | ((origin: string, callback: Function) => void);
  credentials: boolean;
  methods: string[];
  allowedHeaders: string[];
  exposedHeaders: string[];
  maxAge: number;
  preflightContinue: boolean;
  optionsSuccessStatus: number;
}

const corsOptions: CorsOptions = {
  // Restrict origins
  origin: (origin, callback) => {
    const allowedOrigins = [
      'https://app.example.com',
      'https://www.example.com'
    ];

    // Allow requests with no origin (e.g., mobile apps)
    if (!origin) return callback(null, true);

    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },

  // Allow credentials
  credentials: true,

  // Allowed methods
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],

  // Allowed headers
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'X-CSRF-Token'
  ],

  // Headers to expose to the client
  exposedHeaders: ['X-RateLimit-Limit', 'X-RateLimit-Remaining'],

  // Cache preflight response
  maxAge: 86400, // 24 hours

  // Pass preflight response to next handler
  preflightContinue: false,

  // Success status for legacy browsers
  optionsSuccessStatus: 204
};

app.use(cors(corsOptions));

// Dynamic CORS for different environments
function createDynamicCors() {
  return cors((req, callback) => {
    const options: CorsOptions = {
      origin: false,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      allowedHeaders: ['Content-Type', 'Authorization'],
      maxAge: 3600
    };

    // Whitelist origins based on environment
    if (process.env.NODE_ENV === 'development') {
      options.origin = true; // Allow all in development
    } else {
      const origin = req.headers.origin;
      if (origin && isAllowedOrigin(origin)) {
        options.origin = true;
      }
    }

    callback(null, options);
  });
}
```

## DDoS Protection

### Request Size Limiting

```typescript
import express from 'express';

// Limit request body size
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Custom body size limiter
function bodySizeLimit(maxSize: number) {
  return (req: Request, res: Response, next: NextFunction) => {
    let size = 0;

    req.on('data', (chunk) => {
      size += chunk.length;
      
      if (size > maxSize) {
        res.status(413).json({
          error: 'Payload Too Large',
          message: `Request body exceeds ${maxSize} bytes`
        });
        req.connection.destroy();
      }
    });

    next();
  };
}
```

### Connection Limiting

```typescript
class ConnectionLimiter {
  private connections = new Map<string, number>();
  private readonly maxConnectionsPerIP = 100;

  trackConnection(ip: string): boolean {
    const current = this.connections.get(ip) || 0;
    
    if (current >= this.maxConnectionsPerIP) {
      return false;
    }

    this.connections.set(ip, current + 1);
    return true;
  }

  releaseConnection(ip: string): void {
    const current = this.connections.get(ip) || 0;
    
    if (current <= 1) {
      this.connections.delete(ip);
    } else {
      this.connections.set(ip, current - 1);
    }
  }

  getConnectionCount(ip: string): number {
    return this.connections.get(ip) || 0;
  }
}
```

## Infrastructure Hardening

### Process Security

```typescript
// Drop privileges after binding to port
if (process.getuid() === 0) {
  process.setgid('nobody');
  process.setuid('nobody');
}

// Disable dangerous Node.js features
delete process.env.NODE_ENV;
Object.freeze(process.env);

// Set resource limits
if (process.platform === 'linux') {
  const posix = require('posix');
  
  // Limit memory usage
  posix.setrlimit('data', { soft: 1024 * 1024 * 512 }); // 512MB
  
  // Limit number of open files
  posix.setrlimit('nofile', { soft: 1024 });
  
  // Limit CPU time
  posix.setrlimit('cpu', { soft: 300 }); // 5 minutes
}
```

### Network Security

```typescript
// Bind to specific interface
const server = app.listen(PORT, '127.0.0.1', () => {
  console.log(`Server listening on 127.0.0.1:${PORT}`);
});

// Set socket options
server.on('connection', (socket) => {
  // Enable keep-alive
  socket.setKeepAlive(true, 60000);
  
  // Set timeout
  socket.setTimeout(30000);
  
  // Disable Nagle algorithm
  socket.setNoDelay(true);
});
```

## Testing Infrastructure Security

```typescript
describe('Infrastructure Security', () => {
  describe('Security Headers', () => {
    it('should set all required security headers', async () => {
      const response = await request(app).get('/api/health');
      
      expect(response.headers['x-frame-options']).toBe('DENY');
      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['strict-transport-security']).toContain('max-age=31536000');
      expect(response.headers['content-security-policy']).toBeDefined();
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits', async () => {
      const requests = Array(101).fill(null).map(() => 
        request(app).get('/api/users')
      );

      const responses = await Promise.all(requests);
      const tooManyRequests = responses.filter(r => r.status === 429);
      
      expect(tooManyRequests.length).toBeGreaterThan(0);
    });
  });

  describe('CORS', () => {
    it('should reject unauthorized origins', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Origin', 'https://evil.com');
      
      expect(response.headers['access-control-allow-origin']).toBeUndefined();
    });
  });
});
```

## References

- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [Rate Limiting Best Practices](./rate-limiting.md)
- [CORS Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)