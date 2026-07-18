#!/usr/bin/env python3
"""Validate the staged Discover presentation contract without dependencies."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path


DISCOVER_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = DISCOVER_ROOT / "examples" / "html"
TEMPLATE = DISCOVER_ROOT / "templates" / "html" / "page.html"
CSS = DISCOVER_ROOT / "assets" / "html" / "discovery.css"
JAVASCRIPT = DISCOVER_ROOT / "assets" / "html" / "discovery.js"
ACTION_ROOT = DISCOVER_ROOT / "references" / "presentation" / "actions"
COVERAGE_REFERENCE = DISCOVER_ROOT / "references" / "presentation" / "coverage.md"
COMPONENTS_REFERENCE = DISCOVER_ROOT / "references" / "presentation" / "components.md"
RANKED_REFERENCE = ACTION_ROOT / "ranked-options.md"

ACTIONS = (
    "risk-context-report",
    "domain-explainer",
    "ranked-options",
    "brainstorm-spectrum",
    "guided-interview",
    "semantics-map",
    "interactive-prototype",
    "readiness-check",
)
REPRESENTATIVE_ACTION = "domain-explainer"
FORBIDDEN_HTML_TEXT = (
    "thariqs.github.io",
    "html-effectiveness",
    "know your unknowns",
    "copyright",
    "essential-editorial",
    "no confirmed decisions yet",
    "no notes yet",
)
PRESENTATION_PATTERNS = (
    "colors", "type", "nav-pattern", "prompt", "artifact", "cards", "badges",
    "callout", "finding", "assembly", "codeblock", "stats", "segmented",
    "table", "columns", "sequence", "accordion", "confirm", "stepper",
    "annotated", "scrubber", "avatars", "diagrams", "choice-toggle",
    "flow-strip", "schema-box", "inline-chip", "timeline-rail", "split-reveal",
    "tool-palette", "toggle-switch", "unified-diff", "sidebar-toc",
    "decision-box", "expect-reality", "approach-comparison", "flow-terminus",
    "blindspot-report", "brainstorm-spectrum", "tweakable-plan",
    "data-model-card", "guided-question-card", "pr-file-review",
    "callstack-walkthrough", "light-code-card", "annotation-drawer",
    "semantics-map", "design-variant-gallery", "variant-matrix",
    "reviewable-option-frame", "preset-live-preview", "prototype-mock",
    "term-rung", "teach-me-explainer", "signoff-block", "pitch-doc",
    "status-checklist", "activity-filter-bar", "quiz-gate", "sticky-reply",
    "live-editor-panel", "entity-card",
)

# Structural hooks prove that each example demonstrates its action-specific
# information architecture. Pattern markers alone only prove catalog presence.
ACTION_STRUCTURE: dict[str, tuple[tuple[str, int, int | None], ...]] = {
    "risk-context-report": (
        ("data-risk-finding", 5, None),
        ("data-risk-response", 1, None),
    ),
    "domain-explainer": (
        ("data-mechanism-stage", 4, None),
        ("data-domain-term", 4, None),
        ("data-domain-simulation", 1, None),
        ("data-response-kind", 1, None),
    ),
    "ranked-options": (
        ("data-option-frame", 3, 5),
        ("data-option-reaction", 3, None),
        ("data-final-selection", 1, 1),
    ),
    "brainstorm-spectrum": (
        ("data-horizon-lane", 3, None),
        ("data-idea-card", 8, None),
        ("data-spectrum-reaction", 1, None),
    ),
    "guided-interview": (
        ("data-interview-step", 4, None),
        ("data-decision-synthesis", 1, None),
    ),
    "semantics-map": (
        ("data-semantics-mapping", 3, None),
        ("data-code-evidence", 2, None),
        ("data-edge-case-table", 1, None),
    ),
    "interactive-prototype": (
        ("data-prototype-variant", 3, None),
        ("data-prototype-control", 3, None),
        ("data-prototype-observation", 1, None),
    ),
    "readiness-check": (
        ("data-readiness-gate", 4, None),
        ("data-readiness-verdict", 1, None),
        ("data-readiness-probe", 1, None),
    ),
}


class ContractParser(HTMLParser):
    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.page_roots: list[dict[str, str | None]] = []
        self.sections: list[dict[str, str | None]] = []
        self.user_regions: list[tuple[str, dict[str, str | None]]] = []
        self.questions: list[dict[str, str | None]] = []
        self.prompt_hosts = 0
        self.copy_prompt_controls = 0
        self.docnavs = 0
        self.prompt_folds = 0
        self.decision_summary_hosts = 0
        self.note_summary_hosts = 0
        self.search_controls = 0
        self.stylesheets: list[str | None] = []
        self.scripts: list[str | None] = []
        self.presentation_patterns: set[str] = set()
        self.attribute_counts: Counter[str] = Counter()
        self.ids: Counter[str] = Counter()
        self.option_frames: list[dict[str, object]] = []
        self.final_direction_choices: list[str] = []
        self._active_option_frames: list[dict[str, object]] = []
        self._element_stack: list[tuple[str, dict[str, object] | None]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        self.attribute_counts.update(attributes.keys())
        opened_frame: dict[str, object] | None = None
        if "data-option-frame" in attributes:
            opened_frame = {
                "scenario_id": attributes.get("data-scenario-id"),
                "direction_id": attributes.get("data-direction-id"),
                "composition": attributes.get("data-direction-composition"),
                "artifacts": 0,
                "traits": set(),
                "reaction_kinds": set(),
                "reaction_groups": 0,
                "tags": Counter(),
            }
            self.option_frames.append(opened_frame)
            self._active_option_frames.append(opened_frame)
        if self._active_option_frames:
            frame = self._active_option_frames[-1]
            frame["tags"][tag] += 1
            if "data-direction-artifact" in attributes:
                frame["artifacts"] += 1
            trait = attributes.get("data-direction-trait")
            if trait:
                frame["traits"].add(trait)
            reaction_kind = attributes.get("data-reaction-kind")
            if reaction_kind:
                frame["reaction_kinds"].add(reaction_kind)
            if "data-option-reaction" in attributes:
                frame["reaction_groups"] += 1
        direction_choice = attributes.get("data-direction-choice")
        if direction_choice:
            self.final_direction_choices.append(direction_choice)
        if attributes.get("id"):
            self.ids[attributes["id"]] += 1
        if "data-discovery-page" in attributes:
            self.page_roots.append(attributes)
        if "data-discovery-section" in attributes:
            self.sections.append(attributes)
        if tag in {"header", "section"}:
            self.user_regions.append((tag, attributes))
        if "data-discovery-question" in attributes:
            self.questions.append(attributes)
        if "data-discovery-prompt-host" in attributes:
            self.prompt_hosts += 1
        if "data-copy-generated-prompt" in attributes:
            self.copy_prompt_controls += 1
        classes = set((attributes.get("class") or "").split())
        if "essential-docnav" in classes:
            self.docnavs += 1
        if "essential-prompt-fold" in classes:
            self.prompt_folds += 1
        if "data-decision-summaries" in attributes:
            self.decision_summary_hosts += 1
        if "data-note-summaries" in attributes:
            self.note_summary_hosts += 1
        if tag == "input" and attributes.get("type") == "search":
            self.search_controls += 1
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.stylesheets.append(attributes.get("href"))
        if tag == "script" and attributes.get("src"):
            self.scripts.append(attributes.get("src"))
        self.presentation_patterns.update(
            (attributes.get("data-presentation-pattern") or "").split()
        )
        if tag not in self.VOID_TAGS:
            self._element_stack.append((tag, opened_frame))

    def handle_endtag(self, tag: str) -> None:
        while self._element_stack:
            opened_tag, opened_frame = self._element_stack.pop()
            if opened_frame is not None:
                self._active_option_frames.remove(opened_frame)
            if opened_tag == tag:
                break

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.handle_endtag(tag)


def validate_html(path: Path, *, allow_placeholders: bool = False) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    parser = ContractParser()
    parser.feed(text)
    lowered = text.lower()

    for forbidden in FORBIDDEN_HTML_TEXT:
        if forbidden in lowered:
            errors.append(f"{path}: contains forbidden source framing {forbidden!r}")

    if len(parser.page_roots) != 1:
        errors.append(f"{path}: expected exactly one data-discovery-page root")
    elif not allow_placeholders:
        root = parser.page_roots[0]
        for attr in ("data-page-id", "data-discovery-action", "data-discovery-goal"):
            if not root.get(attr):
                errors.append(f"{path}: page root is missing {attr}")

    if len(parser.sections) != len(parser.user_regions):
        errors.append(f"{path}: every header/section must be annotatable")

    section_ids = [section.get("data-section-id") for section in parser.sections]
    if any(not section_id for section_id in section_ids):
        errors.append(f"{path}: every annotatable section needs data-section-id")
    if len(section_ids) != len(set(section_ids)):
        errors.append(f"{path}: section IDs must be unique")
    duplicate_ids = sorted(element_id for element_id, count in parser.ids.items() if count > 1)
    if duplicate_ids:
        errors.append(f"{path}: element IDs must be unique; duplicated {duplicate_ids}")

    for question in parser.questions:
        if not question.get("data-question-id"):
            errors.append(f"{path}: question missing data-question-id")
        if not question.get("data-question-label"):
            errors.append(f"{path}: question missing data-question-label")

    if parser.prompt_hosts != 1:
        errors.append(f"{path}: expected exactly one generated prompt host")
    if parser.copy_prompt_controls != 1:
        errors.append(f"{path}: expected exactly one prompt copy control")
    if parser.docnavs != 1:
        errors.append(f"{path}: expected exactly one shared document navigation")
    if parser.prompt_folds != 1:
        errors.append(f"{path}: expected exactly one folded prompt region")
    if parser.decision_summary_hosts != 1:
        errors.append(f"{path}: expected one multi-decision summary host")
    if parser.attribute_counts["data-decision-label"] != 1:
        errors.append(f"{path}: expected one dynamic decision/action label host")
    if parser.note_summary_hosts != 1:
        errors.append(f"{path}: expected one multi-note summary host")
    if parser.search_controls:
        errors.append(f"{path}: static single-page artifact must not include search")
    stylesheet_urls = {"../../assets/html/discovery.css", "{{DISCOVERY_CSS_URL}}"}
    runtime_urls = {"../../assets/html/discovery.js", "{{DISCOVERY_JS_URL}}"}
    if not stylesheet_urls.intersection(parser.stylesheets):
        errors.append(f"{path}: does not link the shared discovery stylesheet")
    if not runtime_urls.intersection(parser.scripts):
        errors.append(f"{path}: does not link the shared discovery runtime")
    if parser.scripts.count("https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4") != 1:
        errors.append(f"{path}: expected exactly one Tailwind browser runtime")
    for theme_fragment in (
        "@theme inline",
        "--color-canvas: var(--ui-canvas)",
        "--color-glass: var(--ui-glass)",
    ):
        if theme_fragment not in text:
            errors.append(
                f"{path}: missing shared Tailwind theme mapping {theme_fragment!r}"
            )
    if "Copy prompt for LLM coder" not in text:
        errors.append(f"{path}: prompt copy control has the wrong label")
    unknown_patterns = parser.presentation_patterns.difference(PRESENTATION_PATTERNS)
    if unknown_patterns:
        errors.append(
            f"{path}: unknown presentation pattern markers {sorted(unknown_patterns)}"
        )

    if not allow_placeholders and len(parser.page_roots) == 1:
        action = parser.page_roots[0].get("data-discovery-action")
        if action not in ACTION_STRUCTURE:
            errors.append(f"{path}: unknown discovery action {action!r}")
        else:
            for attribute, minimum, maximum in ACTION_STRUCTURE[action]:
                count = parser.attribute_counts[attribute]
                if count < minimum:
                    errors.append(
                        f"{path}: {action} needs at least {minimum} [{attribute}] "
                        f"elements; found {count}"
                    )
                if maximum is not None and count > maximum:
                    errors.append(
                        f"{path}: {action} allows at most {maximum} [{attribute}] "
                        f"elements; found {count}"
                    )
        if action == "ranked-options":
            if text.count("discovery-review-frame-code") != 1:
                errors.append(
                    f"{path}: ranked options need exactly one readable code-surface "
                    "direction frame"
                )
            frames = parser.attribute_counts["data-option-frame"]
            reactions = parser.attribute_counts["data-option-reaction"]
            if reactions < frames:
                errors.append(
                    f"{path}: every ranked option frame needs a local reaction "
                    f"control; found {reactions} reactions for {frames} frames"
                )
            root_scenario = parser.page_roots[0].get("data-scenario-id")
            if not root_scenario:
                errors.append(f"{path}: ranked options need a shared root scenario ID")
            direction_ids = [frame["direction_id"] for frame in parser.option_frames]
            compositions = [frame["composition"] for frame in parser.option_frames]
            if any(not direction_id for direction_id in direction_ids):
                errors.append(f"{path}: every option frame needs data-direction-id")
            if len(direction_ids) != len(set(direction_ids)):
                errors.append(f"{path}: option frame direction IDs must be unique")
            if any(not composition for composition in compositions):
                errors.append(
                    f"{path}: every option frame needs data-direction-composition"
                )
            if len(compositions) != len(set(compositions)):
                errors.append(f"{path}: option frame compositions must be unique")
            for frame in parser.option_frames:
                direction_id = frame["direction_id"] or "<missing>"
                if frame["scenario_id"] != root_scenario:
                    errors.append(
                        f"{path}: option {direction_id!r} must use shared scenario "
                        f"{root_scenario!r}"
                    )
                if frame["artifacts"] != 1:
                    errors.append(
                        f"{path}: option {direction_id!r} needs exactly one "
                        f"data-direction-artifact; found {frame['artifacts']}"
                    )
                if len(frame["traits"]) < 2:
                    errors.append(
                        f"{path}: option {direction_id!r} needs at least two named "
                        f"direction traits; found {len(frame['traits'])}"
                    )
                if frame["reaction_groups"] != 1:
                    errors.append(
                        f"{path}: option {direction_id!r} needs exactly one local "
                        f"reaction group; found {frame['reaction_groups']}"
                    )
                required_reactions = {"keep", "steal", "reject"}
                if frame["reaction_kinds"] != required_reactions:
                    errors.append(
                        f"{path}: option {direction_id!r} reaction kinds must be "
                        f"{sorted(required_reactions)}; found "
                        f"{sorted(frame['reaction_kinds'])}"
                    )
            if Counter(parser.final_direction_choices) != Counter(direction_ids):
                errors.append(
                    f"{path}: final direction choices must map one-to-one to option "
                    f"frame IDs; found {parser.final_direction_choices!r} for "
                    f"{direction_ids!r}"
                )
            signatures = [
                tuple(sorted(frame["tags"].items()))
                for frame in parser.option_frames
            ]
            if len(signatures) != len(set(signatures)):
                errors.append(
                    f"{path}: option frames must use materially distinct structures, "
                    "not renamed copies"
                )

    return errors


def presentation_patterns(path: Path) -> set[str]:
    parser = ContractParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.presentation_patterns


def validate_runtime() -> list[str]:
    errors: list[str] = []
    source = JAVASCRIPT.read_text(encoding="utf-8")
    required_fragments = (
        "essential.discover.v1:",
        "data-discovery-section",
        "data-discovery-prompt-host",
        "data-copy-generated-prompt",
        "navigator.clipboard.writeText",
        "localStorage",
        "touched",
        "annotations",
        "data-decision-summaries",
        "data-note-summaries",
        "dataset.responseKind",
        "Requested follow-up actions",
        "item.dataset.summaryState",
        "promptFoldTarget.append(promptSection)",
    )
    for fragment in required_fragments:
        if fragment not in source:
            errors.append(f"{JAVASCRIPT}: missing runtime behavior {fragment!r}")
    if ".innerHTML" in source:
        errors.append(f"{JAVASCRIPT}: user-facing runtime must not use innerHTML")

    result = subprocess.run(
        ["node", "--check", str(JAVASCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append(f"{JAVASCRIPT}: JavaScript syntax check failed: {result.stderr.strip()}")
    return errors


def validate_stylesheet() -> list[str]:
    errors: list[str] = []
    source = CSS.read_text(encoding="utf-8")
    required_fragments = (
        "container-name: direction-artifact",
        "container-type: inline-size",
        ".discovery-direction-stats",
        ".discovery-direction-flow",
        ".discovery-direction-columns-main-aside",
        "@container direction-artifact (min-width: 44rem)",
        "@media (min-width: 82.01rem)",
        "mask-image: linear-gradient",
        ".discovery-review-frame-code",
        "width: 18.6rem",
    )
    for fragment in required_fragments:
        if fragment not in source:
            errors.append(f"{CSS}: missing responsive direction layout {fragment!r}")
    return errors


def validate_direction_reference_contract() -> list[str]:
    errors: list[str] = []
    required_fragments = {
        COMPONENTS_REFERENCE: (
            "## Direction frame and trait reactions",
            "data-scenario-id",
            "data-direction-artifact",
            "data-direction-trait",
            'data-reaction-kind="keep"',
            'data-reaction-kind="steal"',
            'data-reaction-kind="reject"',
            "data-direction-choice",
        ),
        RANKED_REFERENCE: (
            "## Direction-decision acceptance",
            "### Visual-direction worked mapping",
            "shared scenario ID",
            "keep/steal/reject",
            "one-to-one",
            "`web:design`",
        ),
    }
    for path, fragments in required_fragments.items():
        if not path.is_file():
            errors.append(f"{path}: direction reference is missing")
            continue
        source = path.read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in source:
                errors.append(
                    f"{path}: missing direction contract guidance {fragment!r}"
                )
    return errors


def run(stage: str) -> dict[str, object]:
    errors: list[str] = []
    expected_actions = (
        (REPRESENTATIVE_ACTION,) if stage == "representative" else ACTIONS
    )
    covered_patterns: set[str] = set()

    for required in (TEMPLATE, CSS, JAVASCRIPT, COVERAGE_REFERENCE):
        if not required.is_file():
            errors.append(f"{required}: required shared artifact is missing")

    if TEMPLATE.is_file():
        errors.extend(validate_html(TEMPLATE, allow_placeholders=True))
    if JAVASCRIPT.is_file():
        errors.extend(validate_runtime())
    if CSS.is_file():
        errors.extend(validate_stylesheet())

    for action in expected_actions:
        example = EXAMPLES_ROOT / f"{action}.html"
        reference = ACTION_ROOT / f"{action}.md"
        if not example.is_file():
            errors.append(f"{example}: required {stage} example is missing")
        else:
            errors.extend(validate_html(example))
            covered_patterns.update(presentation_patterns(example))
        if not reference.is_file():
            errors.append(f"{reference}: required {stage} action reference is missing")

    if stage == "complete":
        errors.extend(validate_direction_reference_contract())
        missing_patterns = set(PRESENTATION_PATTERNS).difference(covered_patterns)
        if missing_patterns:
            errors.append(
                "examples do not cover every presentation pattern: "
                + ", ".join(sorted(missing_patterns))
            )
    present_examples = sorted(path.stem for path in EXAMPLES_ROOT.glob("*.html"))
    return {
        "status": "pass" if not errors else "fail",
        "stage": stage,
        "examples_present": present_examples,
        "examples_required": list(expected_actions),
        "presentation_patterns_covered": len(covered_patterns),
        "presentation_patterns_required": len(PRESENTATION_PATTERNS),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=("representative", "complete"),
        default="complete",
        help="Validate the approval-gate artifact or the final eight-action library.",
    )
    args = parser.parse_args()
    result = run(args.stage)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
