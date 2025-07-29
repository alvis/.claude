# Repository Structure

## Table of Contents

- [Repository Layout](#layout) `layout`
- [Project Structure](#patterns) `patterns`
- [File Naming](#naming) `naming`

<layout>
```
services/          # TypeScript backend services
data/              # DB schemas & migrations
manifests/         # Service operation specs
packages/          # Shared utilities & components
infrastructure/    # Pulumi IaC
mocks/             # Test doubles
supabase/          # Supabase configs
```
</layout>

<patterns>

## Project Structure

* `src/` or `source/` - Source code
* `spec/` - Tests (mirrors src/ structure)
* React tests - See `06-react-conventions.md`

## Build Outputs

```plaintext
<project>/
├── lib/           # Compiled JS + declarations
├── coverage/      # Test reports
└── generated/     # Generated code (Prisma, etc)
```

## Domain Alignment

Services, data, and manifests align by domain:

```plaintext
services/profile/
data/profile/
manifests/profile/
```

</patterns>

<naming>

## Files

* Code files: `camelCase.ts`
  * ✅ `getUserProfile.ts`
  * ❌ `get-user-profile.ts`

## Environment Files

* Must start with `.env`
  * ✅ `.env.development`
  * ✅ `.env.supabase.local`
  * ❌ `env.local`
  * ❌ `.supabase.env`

</naming>
