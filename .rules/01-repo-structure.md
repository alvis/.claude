# Repository Layout

```plaintext
services/          # TypeScript back‑end services
data/              # DB schemas & migrations
manifests/         # Service operation specs
packages/          # Shared utilities & components
infrastructure/    # Pulumi IaC
mocks/             # Test doubles
supabase/          # Supabase configs
```

## Common Project Layout

> Every project (shared or product) follows this structure:

- **`src/`** _(or `source/`)_ — Source code
- **`spec/`** — Tests for non-client projects (mirrors `src/` path)
- **React component tests** — See `06-react-conventions.md` for React component file organization

## Domain Alignment Pattern

Services, data controllers, and manifests align by domain (see `10-service-design-patterns.md` for detailed service architecture).

## Build Artifacts Pattern

All projects generate consistent build outputs:

```plaintext
<project>/
├── lib/                   # Compiled JavaScript + declaration files
│   ├── *.js              # Compiled JavaScript
│   ├── *.d.ts            # TypeScript declarations
│   └── *.d.ts.map        # Source maps for declarations
├── coverage/              # Test coverage reports
└── generated/             # Generated code (e.g., Prisma client)
```

## File Naming Conventions

### General Files

Name files in camelCase unless instructed otherwise:

- ✅ `listFiles.ts`
- ✅ `getUserProfile.ts`
- ✅ `validateInput.ts`

### Environment Files

Environment files must start with `.env` and end with its relevant environment:

- ✅ `.env.supabase.local`
- ✅ `.env.development`
- ✅ `.env.production`
- ❌ `.supabase.env.local`
- ❌ `env.local`

## Example alignment across directories

Services, data controllers, and manifests align by domain:

```plaintext
services/
├── ...
└── profile/         # Profile service

data/
├── ...
└── profile/         # Profile data controller

manifests/
├── ...
└── profile/         # Profile operation specs
```

--- END ---
