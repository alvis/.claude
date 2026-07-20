## 🏗️ Advanced

### Extension points

- **<extension hook 1>** — <how to plug in custom behaviour and why you would>
- **<extension hook 2>** — <same>

### Gotchas

- **<gotcha 1>** — <the surprising behaviour, the rationale, the workaround>
- **<gotcha 2>** — <same>

### Performance notes

<When it matters, which options trade latency for memory, which operations are O(n) vs O(1), etc.>

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Alternatives -->
<!--
When to include: standalone OSS library in a well-populated category where readers will (and should) compare. Skip for monorepo-internal packages and niche tools with no peers.
Purpose: honest side-by-side so readers pick the right tool — builds trust even when the answer isn't "us."
-->

## ⚔️ Alternatives

| Project            | Strengths                           | Trade-offs                          | Pick it when                        |
| ------------------ | ----------------------------------- | ----------------------------------- | ----------------------------------- |
| **<this package>** | <what we do best>                   | <what we give up>                   | <the reader's situation>            |
| <alternative 1>    | <what they do best>                 | <where they struggle>               | <the reader's situation>            |
| <alternative 2>    | <what they do best>                 | <where they struggle>               | <the reader's situation>            |

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Ecosystem -->
<!--
When to include: standalone OSS library that ships (or plays with) companion packages, plugins, adapters, or templates. Skip for solo packages.
Purpose: help readers discover the full surface and integrations.
-->

## 🔌 Ecosystem

- [`<companion-package-1>`](<link>) — <one-line relationship>
- [`<companion-package-2>`](<link>) — <one-line relationship>
- [`<community-plugin>`](<link>) — <one-line relationship, mark community vs official>

---

<!-- OSS-ONLY END -->

## 📦 Related Packages

<!--
ALWAYS include this section. List packages that:
- This package depends on
- Work well with this package
- Are commonly used together
- Provide complementary functionality

Use relative links to other packages in the monorepo.
-->

- [`@theriety/<related-package-1>`](../<related-package-1>): Brief description of relationship
- [`@theriety/<related-package-2>`](../<related-package-2>): How it relates to this package
<!-- Add more as needed -->

---

<!-- OSS-ONLY START: FAQ -->
<!--
When to include: standalone OSS library, CLI, microservice, or any package that gets repeat questions in issues/Discord. Skip for monorepo-internal packages.
Purpose: pre-empt the top 3–7 recurring misconceptions so issues stay focused on real bugs.
-->

## ❓ FAQ

<details>
<summary><strong><Common question 1 that readers actually ask?></strong></summary>

<Short, direct answer. Link to the relevant section/API if deeper reading helps.>

</details>

<details>
<summary><strong><Common question 2?></strong></summary>

<Short, direct answer.>

</details>

<details>
<summary><strong><Common question 3?></strong></summary>

<Short, direct answer.>

</details>

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Troubleshooting -->
<!--
When to include: standalone OSS library, CLI, iac, or microservice with known friction points (install, env, permissions, version skew). Skip for pure in-process libraries with no side effects.
Purpose: give readers a first-line checklist before they open an issue.
-->

## 🛠️ Troubleshooting

### <Symptom 1: short description of what the reader sees>

**Cause:** <what actually triggers this>
**Fix:** <concrete steps or config change>

### <Symptom 2>

**Cause:** <what actually triggers this>
**Fix:** <concrete steps or config change>

### Still stuck?

Open an issue with the output of `<diagnostic command>` and your <runtime/version info>.

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Philosophy -->
<!--
When to include: flagship OSS projects and OSS monorepo roots where values/trade-offs shape the whole ecosystem. Skip for individual packages — link up to the root instead.
Purpose: make the project's non-negotiables legible so contributors and users can align (or self-select out).
-->

## 🌟 Philosophy

- **<Principle 1>** — <the value, and the trade-off it forces>
- **<Principle 2>** — <same>
- **<Principle 3>** — <same>

<Optional closing paragraph tying the principles back to concrete design decisions readers will encounter.>

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Contributing -->
<!--
When to include: any OSS package that accepts external contributions. Skip for monorepo-internal packages (the monorepo root handles this).
Purpose: point contributors to the canonical `contributing.md` instead of duplicating it here.
-->

## 🤝 Contributing

Contributions are welcome. See [`contributing.md`](./contributing.md) for the dev setup, branching model, and review process.

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Changelog -->
<!--
When to include: any OSS package published to a registry. Skip for monorepo-internal packages without independent release cadence.
Purpose: single link to the canonical change history.
-->

## 📜 Changelog

See [`changelog.md`](./changelog.md) for the full release history.

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: Security -->
<!--
When to include: any OSS package that handles untrusted input, credentials, network IO, or runs in a security-sensitive context. Skip for pure-math utilities or presentation-only libraries.
Purpose: tell reporters where to disclose privately instead of filing a public issue.
-->

## 🛡️ Security

Please report vulnerabilities via the process in [`security.md`](./security.md). Do not open public issues for security reports.

---

<!-- OSS-ONLY END -->

<!-- OSS-ONLY START: License -->
<!--
When to include: standalone OSS library or OSS monorepo root. Skip for monorepo-internal packages (covered at monorepo level).
Purpose: state the license plainly at the end of the README, as readers expect.
-->

## 📄 License

<SPDX identifier, e.g. `MIT`> © <year> <copyright holder>. See [`license`](./license) for the full text.

<!-- OSS-ONLY END -->

<!--
FOOTER NOTES:
- DO NOT include a "License" section (handled at monorepo level)
- DO NOT include a "Contributing" section (handled at monorepo level)
- DO NOT include installation instructions (users should refer to monorepo docs)
- Keep the footer minimal and focused on navigation
-->
