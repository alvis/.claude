# Automation Scripts Reference

*Collection of useful automation scripts for development and deployment*

## Development Scripts

### Development Environment Setup

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
npm run coverage

echo "Development environment setup complete!"
```

### Code Quality Check

```bash
#!/bin/bash
# scripts/quality-check.sh

set -e

echo "Running code quality checks..."

# TypeScript compilation
echo "Checking TypeScript..."
npm run typecheck

# Linting
echo "Running linter..."
npm run lint

# Tests with coverage
echo "Running tests..."
npm run coverage

# Build verification
echo "Verifying build..."
npm run build

echo "All quality checks passed!"
```

### Database Scripts

```bash
#!/bin/bash
# scripts/db-reset.sh

set -e

echo "Resetting database..."

# Drop and recreate database
npm run db:drop
npm run db:create

# Run migrations
npm run db:migrate

# Seed with test data
npm run db:seed

echo "Database reset complete!"
```

## Release Scripts

### Release Preparation

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
npm run coverage

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

### Changelog Generation

```bash
#!/bin/bash
# scripts/generate-changelog.sh

set -e

# Get version from package.json
version=$(node -p "require('./package.json').version")

# Get previous tag
previous_tag=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")

if [ -z "$previous_tag" ]; then
  echo "No previous tag found, generating full changelog"
  git log --pretty=format:"- %s (%h)" > CHANGELOG.md
else
  echo "Generating changelog from $previous_tag to HEAD..."
  
  {
    echo "# Changelog"
    echo ""
    echo "## [$version] - $(date +%Y-%m-%d)"
    echo ""
    git log $previous_tag..HEAD --pretty=format:"- %s (%h)" --reverse
    echo ""
    echo ""
    
    # Append existing changelog if it exists
    if [ -f CHANGELOG.md ]; then
      tail -n +2 CHANGELOG.md
    fi
  } > CHANGELOG.tmp
  
  mv CHANGELOG.tmp CHANGELOG.md
fi

echo "Changelog updated for version $version"
```

## Deployment Scripts

### Docker Build

```bash
#!/bin/bash
# scripts/docker-build.sh

set -e

# Get version from package.json
version=$(node -p "require('./package.json').version")
image_name="myapp"

echo "Building Docker image $image_name:$version..."

# Build image
docker build -t "$image_name:$version" .
docker tag "$image_name:$version" "$image_name:latest"

# Run security scan
echo "Running security scan..."
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)":/src \
  aquasec/trivy:latest image "$image_name:$version"

echo "Docker image built successfully: $image_name:$version"
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

set -e

url=${1:-"http://localhost:3000"}
max_attempts=${2:-30}
wait_time=${3:-2}

echo "Checking health of $url..."

for i in $(seq 1 $max_attempts); do
  if curl -f -s "$url/health" > /dev/null; then
    echo "Service is healthy after $i attempts"
    exit 0
  fi
  
  echo "Attempt $i/$max_attempts failed, waiting $wait_time seconds..."
  sleep $wait_time
done

echo "Service failed to become healthy after $max_attempts attempts"
exit 1
```

## Maintenance Scripts

### Dependency Update

```bash
#!/bin/bash
# scripts/update-deps.sh

set -e

echo "Updating dependencies..."

# Update package.json
npm update

# Run security audit
npm audit --audit-level=high

# Run tests to ensure nothing broke
npm run coverage

# Check for outdated packages
echo "Checking for outdated packages..."
npm outdated

echo "Dependencies updated successfully!"
```

### Log Cleanup

```bash
#!/bin/bash
# scripts/cleanup-logs.sh

set -e

log_dir=${1:-"/var/log/myapp"}
days_to_keep=${2:-7}

echo "Cleaning up logs older than $days_to_keep days in $log_dir..."

find "$log_dir" -name "*.log" -type f -mtime +$days_to_keep -delete
find "$log_dir" -name "*.log.gz" -type f -mtime +$days_to_keep -delete

echo "Log cleanup completed"
```

### Database Backup

```bash
#!/bin/bash
# scripts/backup-db.sh

set -e

database_url=${DATABASE_URL:-""}
backup_dir=${1:-"./backups"}
timestamp=$(date +"%Y%m%d_%H%M%S")

if [ -z "$database_url" ]; then
  echo "Error: DATABASE_URL environment variable is required"
  exit 1
fi

mkdir -p "$backup_dir"

backup_file="$backup_dir/backup_$timestamp.sql"

echo "Creating database backup: $backup_file"

pg_dump "$database_url" > "$backup_file"

# Compress backup
gzip "$backup_file"

echo "Backup completed: $backup_file.gz"

# Clean up old backups (keep last 10)
ls -t "$backup_dir"/backup_*.sql.gz | tail -n +11 | xargs -r rm

echo "Old backups cleaned up"
```

## Utility Scripts

### Environment Validation

```bash
#!/bin/bash
# scripts/validate-env.sh

set -e

required_vars=(
  "NODE_ENV"
  "DATABASE_URL"
  "SECRET_KEY"
  "API_BASE_URL"
)

echo "Validating environment variables..."

missing_vars=()

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: Missing required environment variables:"
  printf ' - %s\n' "${missing_vars[@]}"
  exit 1
fi

echo "All required environment variables are set"
```

### Performance Benchmark

```bash
#!/bin/bash
# scripts/benchmark.sh

set -e

url=${1:-"http://localhost:3000"}
duration=${2:-"30s"}
connections=${3:-10}

echo "Running performance benchmark against $url..."

# Install wrk if not available
if ! command -v wrk &> /dev/null; then
  echo "wrk not found. Please install wrk for benchmarking."
  exit 1
fi

wrk -t4 -c$connections -d$duration --latency "$url"

echo "Benchmark completed"
```

## Usage Notes

### Making Scripts Executable

```bash
chmod +x scripts/*.sh
```

### Running Scripts

```bash
# Development setup
./scripts/dev-setup.sh

# Quality checks
./scripts/quality-check.sh

# Release preparation
./scripts/release.sh minor

# Health check
./scripts/health-check.sh http://localhost:3000 60 5
```

### Integration with npm scripts

```json
{
  "scripts": {
    "setup": "./scripts/dev-setup.sh",
    "quality": "./scripts/quality-check.sh",
    "release": "./scripts/release.sh",
    "docker:build": "./scripts/docker-build.sh"
  }
}
```
