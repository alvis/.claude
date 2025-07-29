# Project Operations Standards

*Standards for version control, deployment, project setup, and operational tasks*

## Table of Contents

- [🔀 Version Control Standards](#version_control) `version_control` - **workflow:** `commit-with-git`
- [📝 Pull Request Process](#pull_request_process) `pull_request_process` - **workflow:** `create-pr`
- [🚀 Deployment Standards](#deployment_standards) `deployment_standards`
- [⚙️ Project Setup Standards](#project_setup) `project_setup`
- [📊 Monitoring & Logging](#monitoring_logging) `monitoring_logging`
- [🔐 Security Operations](#security_operations) `security_operations`
- [🤖 Automation Scripts](#automation_scripts) `automation_scripts`

<version_control>

## 🔀 Version Control Standards

### Commit Format

```plaintext
<type>(<scope>): <summary>   # ≤72 chars, imperative

<body>

<footer>
```

### Commit Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting (no logic change)
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `test` - Test updates
- `build` - Build system changes
- `ci` - CI/CD changes
- `chore` - Routine tasks/dependencies
- `revert` - Revert previous commit

### Commit Rules

- Scope = directory/module (optional)
- Present tense, imperative mood
- Reference issues: `(#123)`
- Footer: `Closes #123, #456`

### Branch Naming

Format: `<type>/<scope>/<topic>`

Examples:

- `feat/web-talent/add-job-filter`
- `fix/profile/correct-validation`
- `chore/update-dependencies`

Use lowercase-kebab-case only.

<workflow name="commit-with-git">

### Git Workflow

1. **Create Feature Branch**

   ```bash
   git checkout -b feat/auth/add-oauth
   ```

2. **Follow TDD Process**
   - Write tests first (see general-coding.md for TDD workflow)
   - Implement code to pass tests
   - Commit frequently with descriptive messages

3. **Pre-commit Verification** (MANDATORY)

   **🔴 CRITICAL: Always run these commands before committing:**

   ```bash
   npm run lint             # Fix linting issues
   npm run test            # Ensure tests pass
   npm run typecheck       # Verify types (if available)
   ```

   **⚠️ NEVER proceed with commit if any of these fail**

4. **Commit and Push**

   ```bash
   git add .
   git commit -m "feat(auth): implement OAuth2 login"
   git push -u origin feat/auth/add-oauth
   ```

5. **Create Pull Request**
   - Use PR template (see pull request section)
   - Request reviews from appropriate team members
   - Address feedback and update PR

</workflow>

### Critical Rules

**🚨 ABSOLUTE PROHIBITIONS:**

- **NEVER use `--no-verify`** when committing - this bypasses essential quality gates
- **NEVER commit without running** `npm run test` and `npm run lint` first
- **NEVER commit failing tests or linting errors**

**📋 COMMIT REQUIREMENTS:**

- All commits must pass linting and tests
- Keep commit messages clear and atomic
- Follow TDD practices (see general-coding.md)

</version_control>

<pull_request_process>

## 📝 Pull Request Process

<workflow name="create-pr">

### PR Title

Same as commit format: `feat(api): add user export`

### PR Description Template

```markdown
### 📌
**> Purpose and main changes in <3 sentences**

### 📝 Context
Why this change is needed, related tickets

### 🛠️ Implementation
What was implemented and how

### ✅ Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Manually tested

### 💥 Breaking Changes
(omit if none)

### 🔗 Related Issues
Closes #123, See #456

### 🧪 Manual Testing
(omit if not needed)

### 📋 Additional Notes
(omit if none)
```

### PR Workflow

1. Start with draft PR
2. Update as code evolves
3. Request review when ready
4. Address feedback
5. Merge when approved

</workflow>

</pull_request_process>

<deployment_standards>

## 🚀 Deployment Standards

### Environment Configuration

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

// Environment validation
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

### Deployment Pipeline

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
      - run: npm run test -- --coverage
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

### Health Checks

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

</deployment_standards>

<project_setup>

## ⚙️ Project Setup Standards

### Repository Structure

```plaintext
project/
├── services/          # TypeScript backend services
├── data/              # DB schemas & migrations
├── manifests/         # Service operation specs
├── packages/          # Shared utilities & components
├── infrastructure/    # Pulumi IaC
├── mocks/             # Test doubles
├── supabase/          # Supabase configs
├── .github/           # GitHub workflows
├── docs/              # Documentation
└── scripts/           # Build and deployment scripts
```

### Initial Project Setup Workflow

1. **Clone and Dependencies**

   ```bash
   git clone <repo-url>
   cd <project>
   npm ci                    # Install dependencies
   ```

2. **Environment Configuration**

   ```bash
   cp .env.example .env      # Copy environment template
   # Edit .env with your configuration
   ```

3. **Database Setup**

   ```bash
   npm run db:migrate        # Apply database migrations
   npm run db:seed          # Seed initial data
   ```

4. **Verify Installation**

   ```bash
   npm run typecheck        # Verify TypeScript
   npm run lint             # Check code quality
   npm run test            # Run test suite
   npm run build           # Build project
   ```

5. **Development Server**

   ```bash
   npm run dev             # Start development server
   ```

### Package.json Standards

```json
{
  "name": "@company/project-name",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  },
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "typecheck": "tsc --noEmit",
    "clean": "rm -rf dist coverage"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "tsx": "^4.0.0",
    "vitest": "^1.0.0",
    "eslint": "^8.0.0"
  }
}
```

### Environment Files

```bash
# .env.example - Required for all projects
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
LOG_LEVEL=info

# .env.development
NODE_ENV=development
DATABASE_URL=postgresql://localhost:5432/myapp_dev

# .env.test
NODE_ENV=test
DATABASE_URL=postgresql://localhost:5432/myapp_test

# .env.production (not committed)
NODE_ENV=production
DATABASE_URL=postgresql://prod-host:5432/myapp_prod
```

</project_setup>

<monitoring_logging>

## 📊 Monitoring & Logging

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

</monitoring_logging>

<security_operations>

## 🔐 Security Operations

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

  async set(key: string, value: string): Promise<void> {
    // In production, this would integrate with a proper secret store
    process.env[key] = value;
  }

  async delete(key: string): Promise<void> {
    delete process.env[key];
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
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  };
}
```

</security_operations>

<automation_scripts>

## 🤖 Automation Scripts

### Development Scripts

```bash
#!/bin/bash
# scripts/dev-setup.sh

set -e

echo "Setting up development environment..."

# Check Node.js version
required_node_version="18"
current_node_version=$(node -v | cut -d. -f1 | sed 's/v//')

if [ "$current_node_version" -lt "$required_node_version" ]; then
  echo "Error: Node.js $required_node_version or higher is required"
  exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm ci

# Set up environment
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "Please update .env with your local configuration"
fi

# Run initial checks
echo "Running initial checks..."
npm run typecheck
npm run lint
npm run test

echo "Development environment setup complete!"
```

### Release Scripts

```bash
#!/bin/bash
# scripts/release.sh

set -e

# Validate current branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
  echo "Error: Releases must be made from main branch"
  exit 1
fi

# Ensure clean working directory
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: Working directory must be clean"
  exit 1
fi

# Run full test suite
echo "Running full test suite..."
npm run typecheck
npm run lint
npm run test -- --coverage

# Build production
echo "Building for production..."
npm run build

# Version bump (using npm version)
version_type=${1:-patch}
new_version=$(npm version $version_type --no-git-tag-version)

# Commit version bump
git add package.json package-lock.json
git commit -m "chore: bump version to $new_version"

# Create tag
git tag -a "$new_version" -m "Release $new_version"

echo "Release $new_version prepared. Push with:"
echo "git push origin main --tags"
```

</automation_scripts>
