---
name: spec-code
description: "Design or document technical specifications in the canonical template, then delegate Notion synchronization to sync-notion. Use for greenfield specs, updates to an existing DESIGN.md, or documenting an implementation without inventing requirements."
model: opus
context: fork
allowed-tools: Bash, Write, Read, Edit, Task, WebSearch, WebFetch, Glob, Grep, TodoWrite, AskUserQuestion, Skill
argument-hint: "<instruction> [--type=api|web-app|mobile|library|fullstack]"
---

# Spec Code

Design new project specifications OR retrospectively document existing implementations in DESIGN.md format, following strict Notion template structure across three modes — CREATE (greenfield design), UPDATE (modify existing specs), or DOCUMENT (analyze and document existing code) — performing 2-way merge with Notion by default. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. UPDATE and DOCUMENT modes are the high-risk surface here: new requirements must be folded into the spec's existing sections so the reader cannot tell which decisions are original and which were merged later — never as an "Addendum", "Revisions", or "Also note" trailer attached beneath the template.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Generate implementation code (specification only)
- Make technology decisions without analysis
- Add features not in the template structure
- Create custom sections outside template

**When to REJECT**:

- Vague instructions without clear context
- Requests for code implementation instead of specs
- Instructions requiring undecided implementation details
- Requests to add sections not in template

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Detect Mode and Load Materials

1. **Determine Operation Mode**:
   - **CREATE mode**: No DESIGN.md AND no Notion page AND no codebase
   - **UPDATE mode**: DESIGN.md exists OR Notion page found
   - **DOCUMENT mode**: Codebase exists but no DESIGN.md

2. **Load Existing Design** (if UPDATE mode)
3. **Analyze Existing Codebase** (if DOCUMENT mode)
4. **Fetch Notion Template**
5. **Load Reference Documentation** (if --reference provided)
6. **Parse --sync-template Flag** (if provided)

### Step 2: Resolve Merge Conflicts

(Only if existing Notion pages are found.) Record the local files and known refs for the final `Skill(sync-notion)` call. It owns remote materialization, conflict decisions, merged content, and verification; spec-code does not maintain a parallel merge protocol.

### Step 3: Gather Requirements

1. **Parse Arguments**
2. **Clarify Scope** (mode-dependent)
3. **Create Todo List**

### Step 4: Research Tech Stack

- CREATE: Research appropriate stack
- UPDATE: Research only changed technologies
- DOCUMENT: Extract from existing code (no research)

For DOCUMENT mode, see `references/document-mode.md` for the full codebase-extraction workflow (project scan, package.json parsing, tech stack derivation, mapping to spec sections).

### Step 5: Design Architecture

- CREATE: Design from scratch
- UPDATE: Modify aspects
- DOCUMENT: Extract from code

### Step 6: Specify Components

- Identify components
- Detail specifications

### Step 7: Design APIs (if applicable)

- Define API Contracts
- Design Data Models

### Step 8: Design UI (if applicable)

- Define User Interface Structure
- Specify UI Components

### Step 9: Generate or Update Files with Frontmatter

1. **Prepare Frontmatter Metadata**
2. **Compile Design Document Following Template**
3. **Apply --sync-template if Provided**
4. **Write Main File with Frontmatter**
5. **Write Child Page Files with Frontmatter**

See `references/frontmatter.md` for the exact frontmatter schema (`notion_url`, `last_edited_at`, `last_synced_at`, `related_files`), filename mapping, and update rules.

### Step 10: Sync to Notion

(Unless `--skip-notion-sync`.) Invoke `Skill(sync-notion)` with the generated files, selected mode, and any known Notion refs. That skill owns pull/push, merge resolution, verification, retries, and frontmatter metadata. Do not implement a second synchronization protocol here.

### Step 11: Reporting

**Output Format**:

```
[✅/❌] Command: spec-code "$ARGUMENTS"

## Summary
- Mode: [CREATE / UPDATE / DOCUMENT]
- Package name: [name]
- Design document: [path]
- Child documents: [count and filenames]
- Template: Notion
- Project type: [type]
- Tech stack: [technologies]
- Notion sync: [Created/Updated/Skipped]
- Sync verification: [✅ Verified / ⚠️ Partial / Skipped]

## Actions Taken
1. [Actions based on mode]

## Files Created/Updated
- DESIGN.md (with frontmatter)
- REFERENCE.md (with frontmatter)
- [Other child files]

## Template Adherence
- Structure: Follows template exactly
- Sections: Only template sections included

## Next Steps
1. Review DESIGN.md and child files
2. Share with team for feedback
3. Begin implementation following specs
```

## 📝 Examples

### CREATE Mode - New API

```bash
/spec-code "Create REST API for task management with user auth"
# Mode: CREATE
# Creates DESIGN.md with frontmatter
# Creates child page files
# Delegates synchronization to `sync-notion`
```

### UPDATE Mode - Add Feature

```bash
/spec-code "Add caching layer using Redis"
# Mode: UPDATE
# Updates Architecture section only
# Preserves all other sections
# Delegates changes to `sync-notion`
```

### DOCUMENT Mode - Document Existing Code

```bash
/spec-code "Document the existing Express API in this codebase"
# Mode: DOCUMENT (auto-detected)
# Analyzes codebase structure
# Documents actual implementation
# Creates DESIGN.md from code analysis
```

### With Type Specification

```bash
/spec-code "Create SaaS platform" --type=fullstack
# Uses fullstack template patterns
```

### Skip Notion Sync

```bash
/spec-code "Document microservices" --skip-notion-sync
# Creates local files only
# Does NOT sync to Notion
```

### Sync Template

```bash
/spec-code "Update API" --sync-template
# Updates to latest template structure
# Preserves content, reorganizes structure
```

### Error Cases

```bash
/spec-code "app"
# Error: Please provide more details
# Suggestion: Describe what the app does

/spec-code "Create API with custom section"
# Warning: Template does not include custom section
# Cannot add sections outside template
```
