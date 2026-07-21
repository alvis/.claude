#!/usr/bin/env python3
"""Validate the staged Discover presentation contract without dependencies."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path


DISCOVER_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = DISCOVER_ROOT / "examples" / "html"
EXAMPLES_SRC_ROOT = DISCOVER_ROOT / "examples" / "src"
TEMPLATES_SRC_ROOT = DISCOVER_ROOT / "templates" / "src"
# The template's modular source directory (templates/html/page.html <-> src/page/).
TEMPLATE_SRC = TEMPLATES_SRC_ROOT / "page"
TEMPLATE = DISCOVER_ROOT / "templates" / "html" / "page.html"
CSS = DISCOVER_ROOT / "assets" / "html" / "discovery.css"
JAVASCRIPT = DISCOVER_ROOT / "assets" / "html" / "discovery.js"
VENDOR_DIR = DISCOVER_ROOT / "assets" / "html" / "vendor"
# The Tailwind runtime is downloaded on demand; the pinned vendor file must no
# longer be committed, and the gitignored cache below is an optional fallback.
TAILWIND_CACHE = VENDOR_DIR / "tailwind-browser.cache.js"
BUILDER = DISCOVER_ROOT / "scripts" / "build_artifact.py"
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
# Additional convention-demonstration boards (provenance/trade-offs/pins/hub best
# bits). Iterated + validated + pattern-scanned at --stage complete only, separate
# from the required-8 ACTIONS/REPRESENTATIVE_ACTION contract, which stays unchanged.
CONVENTION_EXAMPLES = ("specimen-board", "board-hub", "architecture-board")
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
    # "Best bits" fold-in: provenance pills, honest trade-offs/invented-data flag,
    # author annotation pins + browser-frame chrome, multi-board hub, specimen
    # brand-palette scoping. Marked on the two new CONVENTION_EXAMPLES boards
    # and/or woven into ranked-options.html / risk-context-report.html.
    "provenance-pill", "provenance-row", "tradeoffs-honestly", "invented-data-flag",
    "annotation-pins", "browser-frame", "board-hub", "board-index", "specimen-scope",
    # Stage-3 catalog additions, grouped by owning board exactly as coverage.md
    # records them. IDs are flat here (the coverage map records ownership); the
    # cross-cutting structural checks below fire per-marker where meaningful.
    # domain-explainer:
    "source-ref-chip", "faq-block", "glossary-sync", "live-sim",
    "accordion-exclusive", "anchor-flash",
    # risk-context-report:
    "risk-matrix", "owner-routing", "tldr-block",
    # ranked-options:
    "verdict-table", "variant-rationale", "scope-cuts",
    # brainstorm-spectrum:
    "spectrum-minimap", "reaction-chips",
    # guided-interview:
    "wizard-steps", "nl-reply",
    # semantics-map:
    "syntax-tokens", "rich-diff", "code-pair-highlight", "code-tabs",
    # interactive-prototype:
    "drag-probe", "motion-specimen", "demo-loop", "specimen-code-map",
    # readiness-check:
    "milestone-timeline", "inline-chart", "filter-chips",
    # specimen-board:
    "global-rig", "artboard-frame", "theme-direction-gallery", "mock-frame",
    # architecture-board:
    "node-edge-diagram", "diagram-detail", "prompt-echo", "source-manifest",
)

# Structural hooks prove that each example demonstrates its action-specific
# information architecture. Pattern markers alone only prove catalog presence.
#
# Counts are (attribute, minimum, maximum). Section-bearing hooks are VARIABLE
# by design: their entries are MINIMUMS (maximum is None) so any board may carry
# more sections of that type — e.g. more than the demonstrated number of option
# frames or decision-question sections. Do NOT reintroduce a fixed maximum on a
# section-repeatable hook; a board must never fail for having extra sections.
# Intrinsic equalities (one panel per tab, one note per pin, one dot per card)
# are enforced elsewhere as count == count pairs, not as caps here.
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
        # Direction frames and the final selection are variable: a board may
        # compare more than the demonstrated number of directions, so these are
        # minimums (no cap). The one-to-one direction-choice mapping enforced in
        # the ranked-options block keeps the final selection honest regardless.
        ("data-option-frame", 3, None),
        ("data-option-reaction", 3, None),
        ("data-final-selection", 1, None),
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
    # Convention-demonstration boards (CONVENTION_EXAMPLES), not part of the
    # required-8 ACTIONS contract. Minimums per the locked component API.
    "specimen-board": (
        ("data-tradeoffs-honestly", 1, None),
        ("data-fabricated", 1, None),
        ("data-invented-tag", 1, None),
        ("data-annotation-pin", 3, None),
        ("data-browser-frame", 1, None),
        ("data-specimen", 1, None),
        ("data-provenance", 2, None),
    ),
    "board-hub": (
        ("data-board-hub", 1, None),
        ("data-board-index", 1, None),
        ("data-board-link", 2, None),
    ),
    # Architecture/diagram specimen board: a layered blueprint rather than a
    # browser-frame mockup, so it demonstrates the pins + provenance + honest
    # trade-offs conventions over a code-architecture subject WITHOUT requiring
    # data-browser-frame. Structural hooks prove the layered decomposition IA.
    "architecture-board": (
        ("data-arch-layer", 3, None),
        ("data-arch-module", 5, None),
        ("data-tradeoffs-honestly", 1, None),
        ("data-fabricated", 1, None),
        ("data-invented-tag", 1, None),
        ("data-annotation-pin", 4, None),
        ("data-specimen", 1, None),
        ("data-provenance", 2, None),
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
        self.attribute_value_counts: Counter[tuple[str, str]] = Counter()
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
        for attr_name, attr_value in attributes.items():
            if attr_value is not None:
                self.attribute_value_counts[(attr_name, attr_value)] += 1
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

    # Section counts are VARIABLE by design: a page carries any number (>= 1) of
    # [data-discovery-section] regions, and ANY section type may repeat (several
    # decision-question sections, several mapping/file/deviation/finding
    # sections). Section ids are free-form, per-instance ids — unique per page,
    # not a fixed slot set. The only per-page singleton is the generated-brief
    # prompt host (enforced separately below via prompt_hosts == 1).
    if not parser.sections:
        errors.append(f"{path}: needs at least one [data-discovery-section] region")

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
    # Asset self-containment: a composed page or shell carries NO external or
    # relatively linked assets. The build step (scripts/build_artifact.py)
    # injects the Tailwind runtime plus discovery.css/js into the FINAL artifact;
    # sources and shells reference none. Require their ABSENCE — no
    # <link rel="stylesheet">, no <script src>, and no {{DISCOVERY_*_URL}}
    # placeholder (external OR relative refs both caught). The inline
    # <style type="text/tailwindcss"> @theme block below stays required.
    if parser.stylesheets:
        errors.append(
            f"{path}: must not link any stylesheet (assets are inlined by the "
            f"build step); found {parser.stylesheets}"
        )
    if parser.scripts:
        errors.append(
            f"{path}: must not link any external or relative script (assets are "
            f"inlined by the build step); found {parser.scripts}"
        )
    for dead_placeholder in ("{{DISCOVERY_CSS_URL}}", "{{DISCOVERY_JS_URL}}"):
        if dead_placeholder in text:
            errors.append(
                f"{path}: must not contain asset placeholder {dead_placeholder} "
                f"(the build step injects assets directly)"
            )
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
        if action in CONVENTION_EXAMPLES:
            if not parser.page_roots[0].get("data-board-id"):
                errors.append(f"{path}: board root is missing data-board-id")
        if action == "specimen-board":
            for group in ("wins", "costs", "fails-when"):
                if parser.attribute_value_counts[("data-tradeoff-group", group)] < 1:
                    errors.append(
                        f"{path}: specimen-board trade-offs block is missing the "
                        f"required data-tradeoff-group={group!r} group"
                    )
            pin_count = parser.attribute_counts["data-annotation-pin"]
            pin_note_count = parser.attribute_counts["data-pin-note"]
            if pin_count != pin_note_count:
                errors.append(
                    f"{path}: specimen-board data-annotation-pin count "
                    f"({pin_count}) must match data-pin-note count "
                    f"({pin_note_count})"
                )
        if action == "architecture-board":
            for group in ("wins", "costs", "fails-when"):
                if parser.attribute_value_counts[("data-tradeoff-group", group)] < 1:
                    errors.append(
                        f"{path}: architecture-board trade-offs block is missing "
                        f"the required data-tradeoff-group={group!r} group"
                    )
            pin_count = parser.attribute_counts["data-annotation-pin"]
            pin_note_count = parser.attribute_counts["data-pin-note"]
            if pin_count != pin_note_count:
                errors.append(
                    f"{path}: architecture-board data-annotation-pin count "
                    f"({pin_count}) must match data-pin-note count "
                    f"({pin_note_count})"
                )
        if action == "ranked-options":
            if text.count("discovery-review-frame-code") < 1:
                errors.append(
                    f"{path}: ranked options need at least one readable code-surface "
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

    errors.extend(_validate_stage3_structure(path, parser))
    return errors


def _validate_stage3_structure(path: Path, parser: ContractParser) -> list[str]:
    """Cheap structural checks for the stage-3 catalog patterns.

    Each check is presence-gated on its own marker, so a board (or the
    placeholder template) that does not demonstrate the pattern is unaffected.
    These prove the load-bearing pairing/count invariants of the interactive
    patterns; they are not a substitute for rendered review.
    """

    errors: list[str] = []
    counts = parser.attribute_counts

    # code-tabs: one panel per tab, so every representation is reachable.
    if counts["data-code-tabs"] or counts["data-code-tab"] or counts["data-code-panel"]:
        tabs = counts["data-code-tab"]
        panels = counts["data-code-panel"]
        if tabs != panels:
            errors.append(
                f"{path}: code-tabs must have one [data-code-panel] per "
                f"[data-code-tab]; found {tabs} tabs, {panels} panels"
            )

    # spectrum-minimap: one dot per idea card, so the minimap mirrors the axis.
    if counts["data-minimap-dot"]:
        dots = counts["data-minimap-dot"]
        cards = counts["data-idea-card"]
        if dots != cards:
            errors.append(
                f"{path}: spectrum-minimap must have one [data-minimap-dot] per "
                f"[data-idea-card]; found {dots} dots, {cards} cards"
            )

    # drag-probe: needs at least three draggable items to feel like an ordering.
    if counts["data-drag-probe"] or counts["data-drag-item"]:
        items = counts["data-drag-item"]
        if items < 3:
            errors.append(
                f"{path}: drag-probe needs at least 3 [data-drag-item] elements; "
                f"found {items}"
            )

    # Synchronized-highlight idioms: every keyed group needs at least two
    # members (a source and its counterpart) or there is nothing to sync. Each
    # idiom's key is carried across its source + target attributes.
    sync_idioms = {
        "data-code-pair": ("data-code-pair",),
        "data-term": ("data-term", "data-term-def"),
        "data-code-map": ("data-code-map", "data-code-map-target"),
    }
    for idiom, attrs in sync_idioms.items():
        if not any(counts[attr] for attr in attrs):
            continue
        members: Counter[str] = Counter()
        for (attr, value), count in parser.attribute_value_counts.items():
            if attr in attrs:
                members[value] += count
        for value, count in sorted(members.items()):
            if count < 2:
                errors.append(
                    f"{path}: {idiom}={value!r} needs at least 2 members "
                    f"(source + counterpart); found {count}"
                )

    # wizard-steps: a wizard must present at least three ordered steps.
    if counts["data-wizard"]:
        steps = counts["data-interview-step"]
        if steps < 3:
            errors.append(
                f"{path}: wizard needs at least 3 [data-interview-step] steps; "
                f"found {steps}"
            )

    # theme-direction-gallery: at least two competing specimen scopes side by side.
    if "theme-direction-gallery" in parser.presentation_patterns:
        specimens = counts["data-specimen"]
        if specimens < 2:
            errors.append(
                f"{path}: theme-direction-gallery needs at least 2 [data-specimen] "
                f"scopes; found {specimens}"
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
        # "Best bits" fold-in: generated-prompt sections for provenance and
        # trade-offs, plus the pin-linking hook. Only "data-annotation-pin" is
        # required here (not "data-pin-note"): the pin<->note association is
        # spec'd via aria-describedby/id lookup, not a dataset scan, so the
        # note-side literal is not guaranteed to appear in the JS source even
        # in a correct implementation.
        "Provenance of claims",
        "Trade-offs surfaced",
        "data-annotation-pin",
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
        # "Best bits" fold-in: provenance pills, honest trade-offs/invented-data
        # flag, annotation pins, board-index, specimen brand-palette scoping.
        ".discovery-provenance",
        "[data-provenance",
        ".discovery-tradeoffs",
        ".discovery-invented-tag",
        ".discovery-pin",
        ".discovery-pin-layer",
        ".discovery-pin-note",
        ".discovery-board-index",
        "[data-specimen]",
        ".discovery-artifact-url",
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


_BUILD_ARTIFACT = None


def _load_builder():
    """Import build_artifact by path, caching the module.

    The scripts directory is a plain directory (not a package), so the module is
    loaded via sys.path in the same style validate_artifact_builder already uses.
    """

    global _BUILD_ARTIFACT
    if _BUILD_ARTIFACT is not None:
        return _BUILD_ARTIFACT
    sys.path.insert(0, str(BUILDER.parent))
    sys.dont_write_bytecode = True  # keep scripts/__pycache__ out of the tree
    import build_artifact  # noqa: PLC0415 — local script import by design

    _BUILD_ARTIFACT = build_artifact
    return build_artifact


def validate_source_drift(page_path: Path, source_dir: Path) -> list[str]:
    """Require a committed page to be byte-identical to its composed source.

    Every committed single-file board page must be authored as a modular source
    directory (examples/src/<name>/ or templates/src/page/) whose composition
    reproduces the page byte-for-byte. This forbids giant-file-only boards from
    being added going forward, and catches a committed page that has drifted out
    of lockstep with its modular sources.
    """

    if not source_dir.is_dir():
        return [
            f"{page_path}: committed page has no modular source directory "
            f"(expected {source_dir}); every board must be authored as modular "
            f"sources — add {source_dir}/page.html + sections/*.html and run "
            f"'build_artifact.py {source_dir} --emit-page'"
        ]
    try:
        build_artifact = _load_builder()
        composed = build_artifact.compose_directory(source_dir)
    except Exception as error:  # pragma: no cover - compose/import failure is the finding
        return [
            f"{source_dir}: could not compose modular source for {page_path}: "
            f"{error!r}"
        ]
    if composed.encode("utf-8") != page_path.read_bytes():
        return [
            f"{page_path}: committed page has drifted from its modular source "
            f"{source_dir}; edit the sources and run "
            f"'build_artifact.py {source_dir} --emit-page' to regenerate it"
        ]
    return []


def validate_artifact_builder() -> list[str]:
    """Verify build_artifact.py emits genuinely self-contained output.

    Guards the publish pipeline: a compiled board must inline the Tailwind
    runtime plus discovery.css/js with zero external hosts, zero unfilled
    template placeholders, and zero raw U+FFFD byte (the sentinel the Artifact
    deploy validator rejects). Both output modes are checked; the compiled blob
    is never read into the test's own reporting — only asserted against.
    """

    errors: list[str] = []
    if not BUILDER.is_file():
        errors.append(f"{BUILDER}: required builder artifact is missing")

    # The version-pinned vendor file must no longer be committed \u2014 the runtime is
    # downloaded on demand now.
    for pinned in sorted(VENDOR_DIR.glob("tailwind-browser-*.js")):
        errors.append(
            f"{pinned}: committed pinned Tailwind vendor file must be removed "
            "(the runtime is downloaded on demand)"
        )
    # The gitignored cache is optional (a missing cache is fine); if present it
    # must itself carry no raw U+FFFD (patched at download time).
    if TAILWIND_CACHE.is_file() and TAILWIND_CACHE.read_bytes().count(
        "\ufffd".encode("utf-8")
    ):
        errors.append(f"{TAILWIND_CACHE}: contains raw U+FFFD (deploy would 400)")

    if errors:
        return errors

    try:
        build_artifact = _load_builder()
    except Exception as error:  # pragma: no cover - import failure is the finding
        return errors + [f"build_artifact import failed: {error!r}"]

    source = EXAMPLES_ROOT / "specimen-board.html"
    if not source.is_file():
        return errors + [f"{source}: builder test source is missing"]

    # Independently defined (not imported from the builder) so a loosened builder
    # regex cannot blind this gate: Discover placeholders are {{UPPER_SNAKE}}.
    placeholder = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
    for mode, artifact in (("full", False), ("fragment", True)):
        try:
            output = build_artifact.build(source, artifact=artifact)
        except Exception as error:  # build's own validation raises on failure
            errors.append(f"builder {mode} mode failed: {error}")
            continue
        raw_bytes = output.encode("utf-8")
        if b'src="http' in raw_bytes:
            errors.append(f"builder {mode}: external src=http host present")
        if b'href="http' in raw_bytes:
            errors.append(f"builder {mode}: external href=http host present")
        if raw_bytes.count("\ufffd".encode("utf-8")):
            errors.append(f"builder {mode}: raw U+FFFD present (deploy would 400)")
        if placeholder.search(output):
            errors.append(f"builder {mode}: unfilled template placeholder present")
        if "@tailwindcss/browser" not in output:
            errors.append(f"builder {mode}: Tailwind runtime not inlined")
        if "--ui-canvas" not in output:
            errors.append(f"builder {mode}: discovery.css not inlined")
        if "[data-discovery-prompt-host]" not in output:
            errors.append(f"builder {mode}: discovery.js not inlined")
        if "data-discovery-prompt-host" not in output:
            errors.append(f"builder {mode}: board markup missing")
        if artifact:
            lowered = output.lower()
            if "<!doctype" in lowered or "<html" in lowered or "<body" in lowered:
                errors.append("builder fragment: must omit doctype/html/body")
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
        errors.extend(validate_source_drift(TEMPLATE, TEMPLATE_SRC))
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
            errors.extend(validate_source_drift(example, EXAMPLES_SRC_ROOT / action))
            covered_patterns.update(presentation_patterns(example))
        if not reference.is_file():
            errors.append(f"{reference}: required {stage} action reference is missing")

    # Convention-demonstration boards (specimen-board, board-hub) are validated
    # and pattern-scanned at --stage complete only, separate from the required-8
    # ACTIONS above, so their coverage does not leak into --stage representative.
    convention_examples = CONVENTION_EXAMPLES if stage == "complete" else ()
    for action in convention_examples:
        example = EXAMPLES_ROOT / f"{action}.html"
        if not example.is_file():
            errors.append(f"{example}: required convention example is missing")
        else:
            errors.extend(validate_html(example))
            errors.extend(validate_source_drift(example, EXAMPLES_SRC_ROOT / action))
            covered_patterns.update(presentation_patterns(example))

    if stage == "complete":
        errors.extend(validate_direction_reference_contract())
        errors.extend(validate_artifact_builder())
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
        "examples_required": list(expected_actions) + list(convention_examples),
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
