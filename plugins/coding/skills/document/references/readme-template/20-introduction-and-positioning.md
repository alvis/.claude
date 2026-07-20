# <project name from package.json>

<!-- OSS-ONLY START: Hero block -->
<!--
When to include: standalone OSS library OR OSS monorepo root. Skip for monorepo-internal packages, CLIs with no public landing page, and closed-source services.
Purpose: give first-time visitors a one-glance pitch, trust signals (badges), and a visual anchor before they scroll.
-->

> <one-sentence tagline — the elevator pitch. What is this, who is it for, why should they care?>

<p align="center">
  <a href="https://www.npmjs.com/package/<package-name>"><img src="https://img.shields.io/npm/v/<package-name>.svg" alt="npm version"></a>
  <a href="https://github.com/<org>/<repo>/actions"><img src="https://img.shields.io/github/actions/workflow/status/<org>/<repo>/ci.yml?branch=main" alt="CI"></a>
  <a href="https://codecov.io/gh/<org>/<repo>"><img src="https://img.shields.io/codecov/c/github/<org>/<repo>" alt="coverage"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/npm/l/<package-name>.svg" alt="license"></a>
</p>

<p align="center">
  <!-- Hero image/diagram slot: screenshot, architecture sketch, or animated GIF demo. -->
  <img src="./docs/assets/hero.png" alt="<name> hero diagram" width="720">
</p>

<!-- OSS-ONLY END -->

<!--
SCOPE BANNER:
README = usage, examples, install, API. For how-it-works, link the durable architecture path.
Keep this file focused on what the consumer needs to *use* the package. Push
internal shape, data flow, and design rationale into `docs/architecture/<architecture-slug>.md`.
-->

<!--
README TEMPLATE INSTRUCTIONS:
This is a template for creating package README files. When creating a new README:
1. Replace all placeholder text (e.g., <package-name>, <description>) with actual content
2. Remove all instruction comments (HTML comments like this one)
3. Remove optional sections that don't apply to your package
4. Ensure all code examples are validated with TypeScript compiler

EMOJI USAGE GUIDELINES:
- Always use 📌 for the overview section
- Section headings use these standard emojis:
  - 💡 Core Concept (for conceptual explanation)
  - 🧰 Support Matrix (for feature/capability/runtime overview)
  - 🔑 Environment Variables (for configuration)
  - 🔗 Package Relationships
  - 📐 Architecture
  - 📖 Usage (for usage examples)
  - 📚 API Reference (for API documentation)
  - 📦 Related Packages
- Be consistent: either use emojis for all sections or none
- Don't mix emoji styles within the same README
-->

<br/>

📌 **First paragraph:** What problem does this package solve? What is this package for? Be specific and direct.

**Second paragraph:** What are the key features and unique selling points? How does this package fit into the broader ecosystem? What makes it different or useful?

<!--
Table of Contents — DISCIPLINE:
  • The link row itself must stay on ONE line (no wrapping of the bullet list).
  • Blank lines inside the centering `<div>` are REQUIRED for GitHub's markdown
    parser to render inline links — they do NOT count as multi-line.
  • **TOC budget**: Keep the TOC ≤110 **displayed** characters. Run
    `python3 scripts/toc_width.py <file>` — it is authoritative. Key counts:
    `&emsp;` = 2, emoji/CJK = 2, `&nbsp;`/`&ensp;` = 1, `[caption](url)` drops
    to `caption` only. So `&emsp;&emsp;•&emsp;&emsp;` is 9 displayed chars
    (2+2+1+2+2), not 5. Exclude the `<div>` wrapper from the count; include
    the leading `•&emsp;&emsp;` and trailing `&emsp;&emsp;•`.
  • Prefer hard-to-spot / high-value anchors; skip anchors already obvious on
    first scroll (e.g. Quick Start at the top).
  • Shorten link captions only when the shorter form uses full English words
    and preserves full meaning. Never abbreviate (write `Architecture`, not
    `Arch`). Never drop meaning-bearing words (write `Quick Start`, not
    `Quick`). Valid shortenings collapse to a shorter synonym of equal
    meaning, e.g. `How to Deploy` → `Deployment`.
  • **Format**: Place emoji OUTSIDE the link brackets with one space:
    `💡 [Core Concept](#-core-concept)`. Never embed the emoji inside `[...]`
    — the link caption must be plain text only. Use `&emsp;&emsp;•&emsp;&emsp;`
    separators, leading `•&emsp;&emsp;` + trailing `&emsp;&emsp;•` wrap, with
    a centered `<div>` and a blank line on each side of the link row.

Sample block (copy & edit, stay under the 110 displayed-char budget):

  <div align="center">

  •&emsp;&emsp;💡 [Concept](#-concept)&emsp;&emsp;•&emsp;&emsp;📖 [Usage](#-usage)&emsp;&emsp;•&emsp;&emsp;📚 [API](#-api)&emsp;&emsp;•

  </div>
-->

<br/>
<div align="center">

•&emsp;&emsp;💡 [Concept](#-core-concept)&emsp;&emsp;•&emsp;&emsp;🔑 [Env](#-environment-variables)&emsp;&emsp;•&emsp;&emsp;🔗 [Deps](#-package-relationships)&emsp;&emsp;•&emsp;&emsp;🧰 [Matrix](#-capability-matrix)&emsp;&emsp;•&emsp;&emsp;📖 [Usage](#-usage)&emsp;&emsp;•&emsp;&emsp;📚 [API](#-api-reference)&emsp;&emsp;•

</div>
<br/>

---

<!-- OSS-ONLY START: Quick Start -->
<!--
When to include: anything a stranger installs from npm/PyPI/GitHub — standalone OSS library, CLI, microservice. Skip for monorepo-internal packages (consumers already know how to import siblings).
Purpose: get a reader from zero to first successful call in under 60 seconds.
-->

## ⚡ Quick Start

```bash
# install
npm install <package-name>
```

```ts
// first call — smallest possible happy path
import { <mainExport> } from '<package-name>';

const result = <mainExport>({ /* minimal required options */ });
console.log(result);
```

<One sentence describing what the reader just ran and where to go next (link to Usage or API Reference).>

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Why <Name>? -->
<!--
When to include: standalone OSS library entering a crowded space where differentiation matters. Skip for monorepo-internal packages and obvious-purpose utilities.
Purpose: frame the Problem → Solution narrative so readers self-select in or out before investing time.
-->

## ✨ Why <Name>?

**The problem:** <1–2 sentences describing the pain that existing tools leave on the table.>

**The solution:** <1–2 sentences describing how this package removes that pain, and what design choice makes it possible.>

- **<Pillar 1>** — <why it matters in one line>
- **<Pillar 2>** — <why it matters in one line>
- **<Pillar 3>** — <why it matters in one line>

---

<!-- OSS-ONLY END -->

<!--
OPTIONAL: Include this section for packages that have a central abstraction, architectural pattern,
or non-obvious design that requires conceptual understanding to use effectively.

When to INCLUDE this section:
- Packages with specific architectural patterns (pipeline, factory, adapter, state machine)
- Packages with a central abstraction that unifies multiple components
- Packages where understanding the "why" significantly improves usage
- Packages with non-obvious design decisions that affect how consumers use them

When to SKIP this section:
- Simple utility libraries with self-explanatory APIs
- Component collections without unifying patterns
- Straightforward adapters or wrappers where the concept is obvious
- Packages where the overview already explains everything needed

Good examples of packages that benefit from Core Concept:
- @theriety/endpoint: Explains Request → initiator pipeline and security contract
- Hypothetical scheduler: Would explain job lifecycle and execution model
- Hypothetical state-machine: Would explain state transition mechanics

Bad fits (skip this section):
- @theriety/validation: The concept (validate data against schemas) is self-evident
- @theriety/cache: Simple adapter pattern doesn't need conceptual explanation
- Component libraries: Individual components are self-explanatory

STRUCTURE & CONTENT GUIDELINES:

1. **Open with the core abstraction** (1 sentence)
   - State the central pattern or abstraction using bold on key concepts
   - Focus on nouns/concepts, not verbs: "Every capability hangs off: **each endpoint is a thin wrapper around...**"
   - This anchors the reader's mental model

2. **Document the process flow** (if applicable)
   - Use numbered steps for sequential processes or pipelines
   - Bold verb phrases for phase names: "**Resolve the `Request`**"
   - Follow pattern: WHAT (bolded) → HOW/WHERE (parenthetical) → WHY (explanatory clause)
   - Example: "**Resolve the `Request`** (via `getRequest()`) so that security context is established"

3. **Explain component relationships**
   - Reference actual filenames/functions using `code formatting`
   - Show how main components support the core concept
   - Use bold for abstractions, `code` for identifiers

4. **Include practical guidance**
   - What developers should understand to use it correctly
   - Use imperative bullets: "Treat X as Y so that Z"
   - Provide immediate causal reasoning with connectors like "so that," "because"

5. **Connect to usage patterns**
   - Link the concept to practical implications: "This means you should..."
   - Show how understanding the concept affects usage

6. **Close by reinforcing the model**
   - Tie back to the opening concept
   - Show how all pieces connect: "With that mindset, the APIs simply..."

WRITING STYLE:

- **Match structure to content type**:
  - Sequential processes: numbered steps with bold verb phrases
  - Conceptual relationships: noun-first phrasing with bold abstractions
  - Prescriptive guidance: imperative bullets with causal reasoning

- **Layer detail progressively**: Each unit follows anchor → clarify → justify
  - Start with WHAT (bolded concept)
  - Add WHERE/HOW (parenthetical details)
  - Explain WHY (consequence/rationale in explanatory clauses)

- **Use formatting intentionally**:
  - **Bold** for concepts/phase names (what to remember)
  - `code` for identifiers (what to type/trace)
  - Causal connectors ("so that," "because") signal rationale

- **Be concise**: Aim for 2-4 paragraphs maximum (plus optional numbered steps)

Remember: This section explains the "why" and "how it works conceptually".
The API Reference covers "what functions exist". Usage shows "how to call them".
This bridges the gap by answering: "What's the key insight I need to understand this package's design?"
-->
