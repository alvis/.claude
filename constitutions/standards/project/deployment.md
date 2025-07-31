# Deployment Standards

*Standards for environment configuration, deployment pipelines, and operational monitoring*

## Environment Configuration

### Environment Types

- **development** - Local development
- **staging** - Pre-production testing
- **production** - Live production environment

### Configuration Structure

```typescript
interface EnvironmentConfig {
  NODE_ENV: 'development' | 'staging' | 'production';
  PORT: number;
  DATABASE_URL: string;
  REDIS_URL?: string;
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error';
  SECRET_KEY: string;
  API_BASE_URL: string;
}
```

### Environment Validation

```typescript
function validateEnvironment(): EnvironmentConfig {
  const config = {
    NODE_ENV: process.env.NODE_ENV as EnvironmentConfig['NODE_ENV'],
    PORT: parseInt(process.env.PORT || '3000', 10),
    DATABASE_URL: process.env.DATABASE_URL,
    REDIS_URL: process.env.REDIS_URL,
    LOG_LEVEL: process.env.LOG_LEVEL as EnvironmentConfig['LOG_LEVEL'] || 'info',
    SECRET_KEY: process.env.SECRET_KEY,
    API_BASE_URL: process.env.API_BASE_URL,
  };

  // Validate required fields
  const required = ['DATABASE_URL', 'SECRET_KEY', 'API_BASE_URL'];
  for (const field of required) {
    if (!config[field as keyof EnvironmentConfig]) {
      throw new Error(`Missing required environment variable: ${field}`);
    }
  }

  return config;
}
```

## Deployment Pipeline

### CI/CD Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run coverage
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Deployment commands
          echo "Deploying to production"
```

### Quality Gates

All deployments must pass:

1. **Linting**: Code style standards
2. **Type checking**: TypeScript validation
3. **Tests**: Full test suite with coverage
4. **Build**: Successful compilation
5. **Security scan**: Dependency vulnerabilities

### Deployment Strategies

#### Blue-Green Deployment

- Maintain two identical environments
- Switch traffic between them
- Zero-downtime deployments
- Easy rollback capability

#### Rolling Deployment

- Gradually update instances
- Maintain service availability
- Monitor during rollout
- Automatic rollback on failure

#### Canary Deployment

- Deploy to small subset of users
- Monitor metrics closely
- Gradually increase traffic
- Data-driven rollout decisions

## Health Checks

### Health Check Interface

```typescript
interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  version: string;
  uptime: number;
  checks: {
    database: boolean;
    cache: boolean;
    external_api: boolean;
  };
  timestamp: string;
}
```

### Implementation

```typescript
export async function healthCheck(): Promise<HealthCheck> {
  const startTime = Date.now();
  
  const checks = await Promise.allSettled([
    checkDatabase(),
    checkCache(),
    checkExternalAPI(),
  ]);

  const [database, cache, external_api] = checks.map(
    result => result.status === 'fulfilled' && result.value
  );

  const allHealthy = database && cache && external_api;
  const anyHealthy = database || cache || external_api;

  return {
    status: allHealthy ? 'healthy' : anyHealthy ? 'degraded' : 'unhealthy',
    version: process.env.npm_package_version || 'unknown',
    uptime: process.uptime(),
    checks: { database, cache, external_api },
    timestamp: new Date().toISOString(),
  };
}
```

### Health Check Endpoints

- `GET /health` - Basic health status
- `GET /health/detailed` - Detailed component status
- `GET /ready` - Readiness probe for load balancers
- `GET /live` - Liveness probe for orchestrators

## Monitoring & Logging

### Structured Logging

```typescript
interface LogContext {
  requestId?: string;
  userId?: string;
  operation: string;
  duration?: number;
  [key: string]: unknown;
}

class Logger {
  private context: LogContext;

  constructor(context: LogContext) {
    this.context = context;
  }

  info(message: string, data?: Record<string, unknown>): void {
    this.log('info', message, data);
  }

  error(message: string, error?: Error, data?: Record<string, unknown>): void {
    this.log('error', message, {
      ...data,
      error: {
        name: error?.name,
        message: error?.message,
        stack: error?.stack,
      },
    });
  }

  private log(level: string, message: string, data?: Record<string, unknown>): void {
    const logEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      context: this.context,
      ...data,
    };

    console.log(JSON.stringify(logEntry));
  }
}
```

### Performance Monitoring

```typescript
interface PerformanceMetrics {
  operation: string;
  duration: number;
  success: boolean;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

class PerformanceMonitor {
  async measure<T>(
    operation: string,
    fn: () => Promise<T>,
    metadata?: Record<string, unknown>
  ): Promise<T> {
    const start = Date.now();
    let success = false;

    try {
      const result = await fn();
      success = true;
      return result;
    } finally {
      const duration = Date.now() - start;
      
      const metrics: PerformanceMetrics = {
        operation,
        duration,
        success,
        timestamp: new Date().toISOString(),
        metadata,
      };

      this.recordMetrics(metrics);
    }
  }

  private recordMetrics(metrics: PerformanceMetrics): void {
    // Send to monitoring service
    console.log('METRICS:', JSON.stringify(metrics));
  }
}
```

## Security Operations

### Secret Management

```typescript
interface SecretManager {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
  rotate(key: string): Promise<string>;
}

class EnvironmentSecretManager implements SecretManager {
  async get(key: string): Promise<string | null> {
    const value = process.env[key];
    if (!value) {
      throw new Error(`Secret ${key} not found in environment`);
    }
    return value;
  }

  async rotate(key: string): Promise<string> {
    const newValue = this.generateSecret();
    await this.set(key, newValue);
    return newValue;
  }

  private generateSecret(): string {
    return require('crypto').randomBytes(32).toString('hex');
  }
}
```

### Security Headers

```typescript
interface SecurityHeaders {
  'Content-Security-Policy': string;
  'X-Frame-Options': string;
  'X-Content-Type-Options': string;
  'Referrer-Policy': string;
  'Permissions-Policy': string;
}

export function getSecurityHeaders(): SecurityHeaders {
  return {
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline';",
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  };
}
```

## Rollback Procedures

### Automated Rollback Triggers

- Health check failures
- Error rate spikes
- Performance degradation
- Custom metric thresholds

### Manual Rollback Process

1. **Assess Impact**: Determine scope of issues
2. **Notify Team**: Alert relevant stakeholders
3. **Execute Rollback**: Use deployment tools
4. **Verify Status**: Confirm services restored
5. **Investigate**: Root cause analysis
6. **Document**: Post-incident report

### Rollback Testing

- Regular rollback drills
- Automated rollback validation
- Database migration rollbacks
- Configuration rollbacks
