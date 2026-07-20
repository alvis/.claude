## 💡 Core Concept

<Open with ONE sentence establishing the core abstraction, architectural pattern, or unifying idea.>

<OPTIONAL: If there's a process flow or pipeline, document it in numbered steps:>

The <process name> always runs in the same order:

1. **Phase One** (<reference to file/function>): What happens in this phase and why
2. **Phase Two** (<reference to file/function>): What happens in this phase and why
3. **Phase Three** (<reference to file/function>): What happens in this phase and why
<!-- Add more steps as needed -->

<2-3 paragraphs explaining the implications and practical guidance>

---

<!--
OPTIONAL: Include this section *only* if the package requires environment variables.
Place this section immediately after the Core Concept (or directly after the overview if the Core Concept section does not apply).
-->

## 🔑 Environment Variables

<Describe any environment variables this package uses or requires.>

The <package name> requires/uses the following environment variables:

- `ENV_VAR_NAME`: Description of what it does and when it's required

---

<!--
OPTIONAL: Include this section *only* if this package has important relationships with other packages.
Examples: runtime/service separation, packages that extend or build upon each other.
-->

## 🔗 Package Relationships

### <package-a> vs <package-b>

<Explain how this package relates to other packages. Be clear about:>
- When to use which package
- How they work together
- What responsibilities each has
- The relationship/dependency direction

### Usage by Other Packages

<Explain how other libraries in the ecosystem may use this package:>
- Common integration patterns
- What functionality this provides to dependent packages
- Examples of packages that depend on this one and why

---

<!--
OPTIONAL: Include this section for packages with multiple files/modules or
architectural patterns.

SEPARATION RULE: When durable architecture is also being generated, keep this
section to ≤8 lines total (one-line summary + depth-2 file-tree snippet +
link to its computed relative path). All diagrams, design patterns, invariants,
data flow, and extension points belong in durable architecture, not here.

If there is no durable architecture document, you may expand this section to include a
"Main Components" bullet list. But never duplicate ARCHITECTURE content.

SNIPPETS: Reusable Mermaid diagram snippets (dependency-graph,
architecture-flow, preset-composition) live in `references/snippets/`.
Copy the closest match and edit rather than hand-rolling a new diagram.
-->

## 📐 Architecture

<One sentence naming the architectural shape (pipeline, layered adapter, plugin host, …).>

```plain
src
├── <main-component-1>  # description of component
├── <main-component-2>  # description of component
└── index.ts            # main exports
```

See [the architecture guide](<relative-path-to-docs/architecture/<architecture-slug>.md>) for module topology, data flow, design patterns, and invariants.

---

<!--
OPTIONAL: 🧰 Support Matrix
Include ONLY if the package either (a) ships an `adapters/`, `plugins/`, `drivers/`,
or `providers/` directory (interchangeable implementations worth comparing), OR
(b) is a unified interface over multiple providers, OR (c) advertises runtime /
platform support that consumers need to verify (Node/Deno/Bun/browser).
Skip otherwise.

Pick ONE of the three shapes below that matches your package; delete the others.
Legend must use the exact emoji set below so automated audits can parse it.
-->

## 🧰 Support Matrix

<!-- Shape A: adapter/provider × feature matrix -->

| Adapter | Feature A | Feature B | Notes |
|---------|-----------|-----------|-------|
| <name>  | ✅        | ⚠️        | ...   |

Legend: ✅ supported &nbsp; ⚠️ partial &nbsp; ❌ unsupported &nbsp; 🔜 planned

<!-- Shape B: providers + supported actions
**Providers:** <Provider 1>, <Provider 2>, <Provider 3>

**Supported Actions:**

<div align="center">

| Action     | Description         |
| ---------- | ------------------- |
| <action 1> | <Short description> |

</div>
-->

<!-- Shape C: runtime / platform compatibility
| Runtime       | Supported | Notes                        |
| ------------- | --------- | ---------------------------- |
| Node.js ≥ 18  | ✓         | Native `AbortController`.    |
-->

---
