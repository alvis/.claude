# Deployment & Operations

## Table of Contents

- [GitHub Actions Pipeline](#cicd) `cicd`
- [Infrastructure](#infrastructure) `infrastructure`
- [Health Checks](#monitoring) `monitoring`
- [Deployment Checklist](#deployment_checklist) `deployment_checklist`

<cicd>

## GitHub Actions Pipeline

```yaml
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
      - uses: pnpm/action-setup@v2
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint

  test:
    needs: lint
    steps:
      - run: pnpm run coverage -- --reporter=github-actions
      - uses: codecov/codecov-action@v3

  build:
    needs: test
    steps:
      - run: pnpm run build
```

## Key Checks

- Lint must pass
- Tests must pass with coverage
- Build must succeed
- No secrets in code

</cicd>

<infrastructure>

## Pulumi (IaC)

- Infrastructure defined in `infrastructure/`
- Use TypeScript for all IaC
- Environment-specific stacks
- Secrets in Pulumi config only

## Environments

- `development` - Dev testing
- `staging` - Pre-production
- `production` - Live environment

</infrastructure>

<monitoring>

## Health Checks

```typescript
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    version: process.env.VERSION,
    timestamp: new Date().toISOString(),
  });
});
```

## Alerts

- Error rate > 1%
- Response time > 1s
- Memory usage > 80%
- Failed deployments

</monitoring>

<deployment_checklist>

1. All tests passing
2. Code reviewed and approved
3. Database migrations ready
4. Environment variables updated
5. Monitoring alerts configured
6. Rollback plan documented
   </deployment_checklist>
