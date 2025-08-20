# Environment Variables Standards

_Standards for environment variable management, configuration, and security_

## Core Principles

### Required Documentation

**`.env.example` Required** - All applications using environment variables MUST provide a sample `.env.example` file.

```bash
# .env.example
NODE_ENV=development        # Environment: development | staging | production
PORT=3000                   # Server port
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
JWT_SECRET=your-secret-key-here  # Generate with: openssl rand -hex 32
```

### Consistent Naming

Use UPPER_SNAKE_CASE with descriptive names and logical grouping.

```bash
# ✅ GOOD: clear, grouped naming
DATABASE_URL=...
DATABASE_MAX_CONNECTIONS=10
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# ❌ BAD: inconsistent, unclear naming
database_url=...
max_conn=10
awsKey=...
aws_secret=...
```

## Environment File Management

### File Naming Convention

Use `.env.<environment>` pattern for environment-specific configurations.

```bash
.env.local          # Local development overrides
.env.development    # Development environment
.env.staging        # Staging environment
.env.production     # Production environment
.env.test          # Test environment
```

### Loading Priority

Environment files should load in this order (later files override earlier ones):

1. `.env` (defaults)
2. `.env.local` (local overrides, never committed)
3. `.env.<environment>` (environment-specific)
4. `.env.<environment>.local` (local environment overrides)

## Variable Categories

### Application Configuration

```bash
# Core application settings
NODE_ENV=development        # development | staging | production
PORT=3000                  # Server port
```

### Database Configuration

```bash
# Database connection
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
DATABASE_MAX_CONNECTIONS=20
DATABASE_TIMEOUT_MS=30000
```

### External Services

```bash
# Third-party API keys
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SENDGRID_API_KEY=SG.xxx
REDIS_URL=redis://localhost:6379
```
