# Deployment & Operations

## CI/CD Pipeline (GitHub Actions)

### Workflow Structure

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '22'
      - uses: pnpm/action-setup@v2
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install --frozen-lockfile
      - run: pnpm run test -- --coverage --reporter=github-actions
      - uses: codecov/codecov-action@v3

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: pnpm/action-setup@v2
      - run: pnpm install --frozen-lockfile
      - run: pnpm run build
      - uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            **/lib
            **/dist
            **/.next
```

### Environment-Specific Workflows

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      - name: Deploy with Pulumi
        uses: pulumi/actions@v3
        with:
          command: up
          stack-name: staging
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Infrastructure as Code (Pulumi)

### Stack Configuration

```typescript
// infrastructure/index.ts
import * as pulumi from '@pulumi/pulumi';
import * as aws from '@pulumi/aws';

const config = new pulumi.Config();
const env = pulumi.getStack();

// environment-specific configuration
const settings =
  {
    production: {
      instanceType: 't3.medium',
      minSize: 2,
      maxSize: 10,
      dbInstanceClass: 'db.r5.large',
    },
    staging: {
      instanceType: 't3.small',
      minSize: 1,
      maxSize: 3,
      dbInstanceClass: 'db.t3.medium',
    },
  }[env] || settings.staging;

// export stack outputs
export const apiEndpoint = api.url;
export const dbEndpoint = database.endpoint;
```

### Resource Tagging

```typescript
// consistent tagging strategy
const tags = {
  Environment: env,
  Project: 'theriety-core',
  ManagedBy: 'pulumi',
  Team: 'platform',
  CostCenter: config.require('costCenter'),
};

const bucket = new aws.s3.Bucket('assets', {
// apply to all resources
  tags,
  versioning: {
    enabled: env === 'production',
  },
});
```

## Deployment Strategies

(To be confirmed)

## Health Checks & Monitoring

- Each http based service has a heath check endpoint at `/health`

(To be confirmed)

## Database Migrations

### Migration Strategy

```json
// package.json scripts
{
  "scripts": {
    "db:migrate": "prisma migrate deploy",
    "db:migrate:dev": "prisma migrate dev",
    "db:migrate:create": "prisma migrate dev --create-only",
    "db:migrate:status": "prisma migrate status",
    "db:seed": "tsx prisma/seed.ts"
  }
}
```

### Safe Migration Practices

```typescript
// pre-deployment migration check
async function checkMigrations() {
  const pending = await prisma.$queryRaw`
    SELECT * FROM _prisma_migrations 
    WHERE applied_steps_count < migration_steps_count
  `;

  if (pending.length > 0) {
    throw new Error('Pending migrations detected');
  }
}

// backward-compatible migrations
/*
1. Add new column (nullable)
2. Deploy code that writes to both old and new
3. Backfill data
4. Deploy code that reads from new column
5. Remove old column
*/
```

## Secrets Management

### Environment Variables

```bash
# .env.example (commit this)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
API_KEY=your-api-key-here
NODE_ENV=development

# .env.production (never commit)
DATABASE_URL=${{ secrets.DATABASE_URL }}
REDIS_URL=${{ secrets.REDIS_URL }}
API_KEY=${{ secrets.API_KEY }}
NODE_ENV=production
```

### AWS Secrets Manager

```typescript
// fetch secrets at runtime
import { SecretsManager } from 'aws-sdk';
const secretsManager = new SecretsManager();

async function getSecret(secretName: string): Promise<Record<string, string>> {
  const data = await secretsManager
    .getSecretValue({
      SecretId: secretName,
    })
    .promise();

  return JSON.parse(data.SecretString || '{}');
}

// initialize on startup
const secrets = await getSecret(`theriety/${env}/api`);
process.env.DATABASE_URL = secrets.DATABASE_URL;
```

--- END ---
