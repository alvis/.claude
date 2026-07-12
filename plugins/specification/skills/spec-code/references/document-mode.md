# DOCUMENT Mode — Codebase-Extraction Workflow

DOCUMENT mode generates a specification by analyzing an existing codebase rather than designing from scratch. It produces a DESIGN.md (and child files) that documents reality, not aspiration.

## When DOCUMENT Mode Activates

- A codebase exists but no DESIGN.md is present, OR
- The instruction explicitly requests documentation of existing code.

## Step A — Analyze Existing Codebase (Step 1.3 in parent workflow)

- Scan project structure using the Glob tool.
- Read `package.json` to identify dependencies and extract the package name.
- Analyze file organization and architecture.
- Identify key components from imports and exports.
- Extract tech stack from dependencies (with versions).
- Map the actual implementation onto the specification template structure.

## Step B — Tech Stack Extraction (Step 4 in parent workflow)

DOCUMENT mode does NOT research; it extracts.

- Pull the tech stack from the Step A codebase analysis.
- Identify versions from `package.json`.
- Document the actual technologies in use.
- Note framework and library choices made.
- Record actual versions (no speculative recommendations).

## Step C — Architecture Extraction (Step 5 in parent workflow)

- Extract architecture from code structure.
- Identify layers from file organization.
- Document actual patterns in use.
- Map component relationships from imports.
- Describe data flow from code analysis.
- Use mermaid code blocks for diagrams unless explicitly specified otherwise.

## Step D — Component Extraction (Step 6 in parent workflow)

- Analyze directory structure to identify components.
- Read key files to understand component boundaries.
- Map component responsibilities from code.
- For each component, document:
  - Purpose and responsibilities (from actual code behavior).
  - Key classes/modules/functions present.
  - Data structures and models actually used.
  - Error handling approach as implemented.

## Step E — API Extraction (Step 7, if applicable)

- Read routing files to enumerate endpoints.
- Document actual endpoints (paths, methods, handlers).
- Extract request/response shapes from code (types, schemas, validators).
- Read model/schema files to extract data models.
- Document actual database structure and relationships.
- Extract validation rules from code.

## Step F — UI Extraction (Step 8, if applicable)

- Analyze component files to map screen/page organization.
- Document actual routing from code.
- Read component files to extract props and state from TypeScript types.
- Note the actual styling approach used.
- Document reusable components as they exist.

## Step G — File Generation (Step 9 in parent workflow)

- Generate the specification based on code analysis.
- Document actual implementation under template sections.
- Fill all template sections with discovered information.
- Note where the implementation differs from best practices (if relevant).
- Apply the standard frontmatter (see `references/frontmatter.md`).

## Notion Sync Considerations (Step 10)

When syncing a DOCUMENT-mode spec to Notion:

- Set page property `Status = "Implemented"` (CREATE mode uses `"Drafting"`).
- Otherwise delegate the standard synchronization flow to `Skill(sync-notion)`; spec-code owns document generation, not Notion transport or conflict mechanics.

## Examples

```bash
/spec-code "Document the existing Express API in this codebase"
# Auto-detected DOCUMENT (codebase exists, no DESIGN.md).
# Extracts package name from package.json (e.g., "express-api").
# Analyzes structure, extracts tech stack, documents architecture from code.
# Identifies components, extracts API endpoints from route files.
# Generates DESIGN.md + child files with frontmatter.
# Searches Design Specification database for "express-api".
#   - If found: updates existing page with Status="Implemented".
#   - If not found: creates new page with Status="Implemented".
```

```bash
/spec-code "Retrospectively document this Next.js application" --type=web-app
# Scans Next.js project structure.
# Documents actual pages, components, API routes.
# Extracts UI component tree from code.
# Captures current tech decisions, follows template structure.
# All files include frontmatter; syncs to Notion with 1:1 mapping.
```

```bash
/spec-code "Document the authentication module only"
# Partial-codebase DOCUMENT.
# Analyzes auth-related files only.
# Documents auth component architecture and API endpoints.
# Produces a focused DESIGN.md following template structure.
```
