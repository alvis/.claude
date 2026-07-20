# Claude Code Plugin Marketplace

Eight focused plugins provide composable Claude Code skills. Plugin manifests and each skill's `SKILL.md` are the source of truth; this file is generated.

## Install

```bash
claude plugin install ./plugins/<plugin>
```

Dependencies are declared in each plugin's `.claude-plugin/plugin.json`; installing a dependent plugin enables its required providers automatically.

## Plugins and skills

Use the overview below to choose a plugin, then open only that plugin's generated skill catalog.

<!-- Stable fragment entrypoints retained after moving plugin detail. -->
<a id="coding-depends-on-essential"></a>
<a id="essential"></a>
<a id="governance-depends-on-essential"></a>
<a id="react-depends-on-coding-essential"></a>
<a id="specification-depends-on-coding-essential"></a>
<a id="web-depends-on-coding-essential"></a>
<a id="theriety-depends-on-coding-specification-essential"></a>
<a id="client-depends-on-essential"></a>

| Plugin | Focus | Requires |
| --- | --- | --- |
| [`coding`](readme/10-coding-skills.md) | General code writing tools including quality checks, testing, architecture, and implementation support | `essential` |
| [`essential`](readme/20-essential-skills.md) | Documentation creation, code design, product strategy, and Notion integration for knowledge management | — |
| [`governance`](readme/30-governance-skills.md) | Tools for creating and managing Claude Code configuration files including commands, skills, standards, and agents | `essential` |
| [`react`](readme/40-react-skills.md) | React component development with UI implementation, design systems, Next.js expertise, and fullstack capabilities | `coding`, `essential` |
| [`specification`](readme/50-specification-skills.md) | Design specifications, architecture specs, requirements gathering, and technical documentation with Notion integration for knowledge management | `coding`, `essential` |
| [`web`](readme/60-web-skills.md) | Web development tools including UX design, growth optimization, rapid prototyping, browser automation via agent-browser, Next.js debugging via Chrome DevTools, and design auditing | `coding`, `essential` |
| [`theriety`](readme/70-theriety-skills.md) | Domain-specific service and data orchestrator lifecycle management for Theriety — build and audit services and data layers | `coding`, `specification`, `essential` |
| [`client`](readme/80-client-skills.md) | Client-facing screen design and UX documentation with Notion integration | `essential` |

## Agent team

<a id="roster"></a><a id="delegation-topology"></a><a id="team-shapes"></a><a id="gates"></a><a id="team-operation"></a><a id="notes"></a>

Install the 23-agent team with the `essential:install-agents` skill by asking Claude to "install the agents". The [agent-team reference](readme/90-agent-team.md) contains the roster, delegation topology, gates, and operating notes.

## Validation

```bash
claude plugin validate --strict .
python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .
```

Run `python3 scripts/generate_readme.py --check` to confirm the overview and generated catalog are current.
