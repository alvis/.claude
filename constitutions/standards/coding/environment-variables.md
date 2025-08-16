# Environment Variables Standards

_Standards for environment variable management, configuration, and security_

## Core Principles

### Required Documentation

**`.env.example` Required**

If the application uses environment variables, you **MUST** provide a sample `.env.example` file with:

- All consumed environment variable keys
- Clear explanations for each variable
- Example values (never real secrets)
- Required vs optional indicators

## Environment File Standards

### File Naming Convention

Environment files must follow this naming pattern: `.env.<environment>`

Examples: `.env.local`, `.env.development`, `.env.staging`, `.env.production`

### Example .env.example File

```bash
# Application
NODE_ENV=development        # Environment: development | staging | production
PORT=3000                   # Server port

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# Auth - REQUIRED
JWT_SECRET=your-secret-key-here  # Generate with: openssl rand -hex 32

# External Services - REQUIRED
STRIPE_API_KEY=sk_test_...
SENDGRID_API_KEY=SG.xxx
```

## Variable Naming Standards

- Use **UPPER_SNAKE_CASE** for all environment variables
- Group related variables with common prefixes (DATABASE_, AWS_, SERVICE_)
- Use descriptive names (avoid abbreviations)

## Best Practices

## Security Guidelines

- **Never commit real secrets** - Use placeholders in .env.example
- **No private keys except in unit tests** - Use mocks for testing
- **Generate strong secrets**: `openssl rand -hex 32`
- **Use secret managers** in production environments
