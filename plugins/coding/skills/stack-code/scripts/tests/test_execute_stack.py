"""Tests for execute-stack.py private helpers.

The SUT lives at `../execute-stack.py`. Because the filename uses a hyphen it
cannot be imported via the normal `import` syntax, so we load it through
`importlib.util.spec_from_file_location` once at module scope (mirrors the
loader pattern in `tests/test_sync_codex_skills.py`).

Scope:
- `_is_substantive`        - boilerplate / metadata padding rejection
- `_validate_slice_body`   - hard-fail naming + sentinel-rejection contract
- `_delivered_items`       - diff-shape + Delivered-trailer derivation
- `_reviewer_items`        - change-shape + Reviewer-trailer derivation
- `_compose_body`          - section drop + section-order + stack-metadata absence
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest


# --- MODULE LOADING ------------------------------------------------------- #

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_MODULE_PATH = _SCRIPTS_DIR / "execute-stack.py"


def _load_execute_stack() -> Any:
    """Load `execute-stack.py` as a module named `execute_stack`.

    The sibling `lib` and `restack` modules are stdlib-only, so adding the
    scripts directory to `sys.path` is sufficient for the top-level `import
    restack` / `from lib import ...` statements inside the SUT to resolve.
    """
    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("execute_stack", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


execute_stack = _load_execute_stack()


# --- SHARED FIXTURES ------------------------------------------------------ #

# A minimally-valid slice for `_compose_body` happy-path checks. Tests that
# need to vary specific fields construct a new dict via `{**SLICE, ...}` so
# the shared base is never mutated (TST-DATA-01 spirit applied to Python).
SLICE: dict[str, Any] = {
    "n": 1,
    "bookmark": "feature-x/01-core",
    "scope": "core",
    "title": "feat(core): add widget",
    "summary": "Adds the widget to the core package.",
    "context_body": "Users have been asking for a widget for months.",
    "implementation_body": "Introduce Widget class with three public methods.",
    "files": ["src/core/widget.ts"],
    "delivered_trailer": [],
    "reviewer_trailer": [],
}


# --- _is_substantive ------------------------------------------------------ #


class TestIsSubstantive:
    """fn:_is_substantive — substantive-narrative gate."""

    def test_returns_false_for_empty_string(self) -> None:
        assert execute_stack._is_substantive("") is False

    def test_returns_false_for_whitespace_only(self) -> None:
        assert execute_stack._is_substantive("   \n\t  ") is False

    def test_returns_false_when_text_contains_part_of_stack_marker(self) -> None:
        assert execute_stack._is_substantive("Part of stack foo/bar") is False

    def test_returns_false_when_text_contains_files_in_this_slice_marker(self) -> None:
        assert execute_stack._is_substantive("Files in this slice: a.py, b.py") is False

    def test_returns_false_when_text_contains_no_file_list_marker(self) -> None:
        assert execute_stack._is_substantive("(no file list available)") is False

    def test_returns_false_when_marker_is_embedded_in_otherwise_real_prose(self) -> None:
        # Defensive: any presence of a marker poisons the whole value, because
        # mixed boilerplate still hides the absence of standalone reasoning.
        mixed = "Real prose here.\n\nPart of stack abc\nMore prose."
        assert execute_stack._is_substantive(mixed) is False

    def test_returns_true_for_substantive_prose(self) -> None:
        assert execute_stack._is_substantive("This change fixes a race condition.") is True


# --- _validate_slice_body ------------------------------------------------- #


class TestValidateSliceBody:
    """fn:_validate_slice_body — hard-fail contract."""

    def test_raises_when_summary_missing(self) -> None:
        slice_data = {**SLICE, "summary": ""}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_raises_when_summary_is_whitespace_only(self) -> None:
        slice_data = {**SLICE, "summary": "   \n  "}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_raises_when_summary_is_stack_metadata_only(self) -> None:
        slice_data = {**SLICE, "summary": "Part of stack feature-x"}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_raises_when_context_body_missing(self) -> None:
        slice_data = {**SLICE, "context_body": ""}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_raises_when_context_body_is_stack_metadata_only(self) -> None:
        slice_data = {**SLICE, "context_body": "Part of stack feature-x"}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_raises_when_implementation_body_missing(self) -> None:
        slice_data = {**SLICE, "implementation_body": "   "}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_raises_when_implementation_body_is_stack_metadata_only(self) -> None:
        slice_data = {**SLICE, "implementation_body": "Files in this slice: a.py"}

        with pytest.raises(SystemExit):
            execute_stack._validate_slice_body(slice_data)

    def test_error_message_names_the_offending_bookmark_for_context(self) -> None:
        slice_data = {**SLICE, "bookmark": "feature-x/07-auth", "context_body": ""}

        with pytest.raises(SystemExit) as excinfo:
            execute_stack._validate_slice_body(slice_data)

        assert "feature-x/07-auth" in str(excinfo.value)

    def test_error_message_names_the_offending_slice_number_for_implementation(self) -> None:
        slice_data = {**SLICE, "n": 7, "implementation_body": ""}

        with pytest.raises(SystemExit) as excinfo:
            execute_stack._validate_slice_body(slice_data)

        assert "#07" in str(excinfo.value)

    def test_passes_silently_when_both_bodies_are_substantive(self) -> None:
        # No raise == pass; assert the function returns None to make the
        # happy-path expectation explicit.
        assert execute_stack._validate_slice_body(SLICE) is None


# --- _delivered_items ----------------------------------------------------- #


class TestDeliveredItems:
    """fn:_delivered_items — Delivered checklist derivation."""

    def test_always_emits_no_new_lint_or_type_errors_line(self) -> None:
        rendered = execute_stack._delivered_items([], [])

        assert "No new lint or type errors" in rendered

    def test_emits_tests_line_when_diff_contains_spec_file(self) -> None:
        rendered = execute_stack._delivered_items(["src/foo.spec.ts"], [])

        assert "Tests added/updated" in rendered

    def test_emits_tests_line_when_diff_contains_test_file(self) -> None:
        rendered = execute_stack._delivered_items(["src/foo.test.py"], [])

        assert "Tests added/updated" in rendered

    def test_emits_tests_line_when_diff_contains_underscore_test_file(self) -> None:
        rendered = execute_stack._delivered_items(["pkg/widget_test.go"], [])

        assert "Tests added/updated" in rendered

    def test_emits_tests_line_when_diff_contains_tests_directory(self) -> None:
        rendered = execute_stack._delivered_items(["src/__tests__/foo.ts"], [])

        assert "Tests added/updated" in rendered

    def test_omits_tests_line_when_no_test_paths_in_diff(self) -> None:
        rendered = execute_stack._delivered_items(["src/foo.ts"], [])

        assert "Tests added/updated" not in rendered

    def test_emits_documentation_line_when_diff_contains_markdown_file(self) -> None:
        rendered = execute_stack._delivered_items(["README.md"], [])

        assert "Documentation updated" in rendered

    def test_emits_documentation_line_when_diff_contains_docs_directory(self) -> None:
        rendered = execute_stack._delivered_items(["docs/intro.txt"], [])

        assert "Documentation updated" in rendered

    def test_omits_documentation_line_when_no_docs_paths_in_diff(self) -> None:
        rendered = execute_stack._delivered_items(["src/foo.ts"], [])

        assert "Documentation updated" not in rendered

    def test_appends_items_from_delivered_trailer(self) -> None:
        rendered = execute_stack._delivered_items([], ["Custom delivery note"])

        assert "Custom delivery note" in rendered

    def test_deduplicates_trailer_item_already_present(self) -> None:
        rendered = execute_stack._delivered_items([], ["No new lint or type errors"])

        # The line must appear exactly once even though the trailer repeats it.
        assert rendered.count("No new lint or type errors") == 1

    def test_ignores_blank_trailer_items(self) -> None:
        rendered = execute_stack._delivered_items([], ["   ", ""])

        # The only bullet that should render is the always-on lint-clean line.
        assert rendered == "- [x] No new lint or type errors"

    def test_renders_each_bullet_with_checked_box(self) -> None:
        rendered = execute_stack._delivered_items(["a.spec.ts", "README.md"], [])

        assert rendered == (
            "- [x] Tests added/updated\n"
            "- [x] Documentation updated\n"
            "- [x] No new lint or type errors"
        )


# --- _reviewer_items ------------------------------------------------------ #


class TestReviewerItems:
    """fn:_reviewer_items — Reviewer checklist derivation."""

    def test_always_emits_behaviour_matches_summary_line(self) -> None:
        rendered = execute_stack._reviewer_items(
            [], breaking=False, notes_present=False, trailer_items=[]
        )

        assert "Behaviour matches the Summary above" in rendered

    def test_emits_migration_line_when_breaking_flag_set(self) -> None:
        rendered = execute_stack._reviewer_items(
            [], breaking=True, notes_present=False, trailer_items=[]
        )

        assert "Migration steps in `## Breaking Changes`" in rendered

    def test_omits_migration_line_when_not_breaking(self) -> None:
        rendered = execute_stack._reviewer_items(
            [], breaking=False, notes_present=False, trailer_items=[]
        )

        assert "Migration steps" not in rendered

    def test_emits_security_line_when_diff_touches_auth_directory(self) -> None:
        rendered = execute_stack._reviewer_items(
            ["src/auth/login.ts"],
            breaking=False,
            notes_present=False,
            trailer_items=[],
        )

        assert "Security-sensitive paths reviewed" in rendered

    def test_emits_security_line_when_diff_touches_crypto_directory(self) -> None:
        rendered = execute_stack._reviewer_items(
            ["pkg/crypto/aes.go"],
            breaking=False,
            notes_present=False,
            trailer_items=[],
        )

        assert "Security-sensitive paths reviewed" in rendered

    def test_emits_security_line_when_filename_contains_secret(self) -> None:
        rendered = execute_stack._reviewer_items(
            ["config/secrets.yaml"],
            breaking=False,
            notes_present=False,
            trailer_items=[],
        )

        assert "Security-sensitive paths reviewed" in rendered

    def test_emits_security_line_when_filename_contains_token(self) -> None:
        rendered = execute_stack._reviewer_items(
            ["src/token-store.ts"],
            breaking=False,
            notes_present=False,
            trailer_items=[],
        )

        assert "Security-sensitive paths reviewed" in rendered

    def test_omits_security_line_for_non_security_paths(self) -> None:
        rendered = execute_stack._reviewer_items(
            ["src/widget.ts"],
            breaking=False,
            notes_present=False,
            trailer_items=[],
        )

        assert "Security-sensitive paths reviewed" not in rendered

    def test_emits_follow_up_line_when_notes_present(self) -> None:
        rendered = execute_stack._reviewer_items(
            [], breaking=False, notes_present=True, trailer_items=[]
        )

        assert "Follow-ups listed in Additional Notes" in rendered

    def test_omits_follow_up_line_when_notes_absent(self) -> None:
        rendered = execute_stack._reviewer_items(
            [], breaking=False, notes_present=False, trailer_items=[]
        )

        assert "Follow-ups listed in Additional Notes" not in rendered

    def test_appends_items_from_reviewer_trailer(self) -> None:
        rendered = execute_stack._reviewer_items(
            [], breaking=False, notes_present=False, trailer_items=["Verify cache hit ratio"],
        )

        assert "Verify cache hit ratio" in rendered

    def test_renders_each_bullet_with_unchecked_box(self) -> None:
        rendered = execute_stack._reviewer_items(
            ["src/auth/login.ts"],
            breaking=True,
            notes_present=True,
            trailer_items=["Extra reviewer note"],
        )

        assert rendered == (
            "- [ ] Behaviour matches the Summary above\n"
            "- [ ] Migration steps in `## Breaking Changes` are complete and accurate\n"
            "- [ ] Security-sensitive paths reviewed\n"
            "- [ ] Follow-ups listed in Additional Notes are tracked (issue links present)\n"
            "- [ ] Extra reviewer note"
        )


# --- _compose_body -------------------------------------------------------- #


class TestComposeBody:
    """fn:_compose_body — full PR-body render."""

    def test_includes_summary_paragraph(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Adds the widget to the core package." in body

    def test_includes_context_body_when_present(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Users have been asking for a widget for months." in body

    def test_includes_implementation_body_when_present(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Introduce Widget class with three public methods." in body

    def test_drops_breaking_changes_section_when_body_absent_and_no_marker(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Breaking Changes" not in body

    def test_renders_breaking_changes_section_when_subject_carries_bang_marker(self) -> None:
        slice_data = {
            **SLICE,
            "title": "feat(core)!: drop legacy API",
        }

        body = execute_stack._compose_body(slice_data)

        assert "Breaking Changes" in body

    def test_defaults_breaking_changes_body_to_none_when_bang_present_but_body_empty(self) -> None:
        slice_data = {
            **SLICE,
            "title": "feat(core)!: drop legacy API",
        }

        body = execute_stack._compose_body(slice_data)

        assert "None." in body

    def test_drops_related_issues_section_when_body_absent(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Related Issues" not in body

    def test_drops_manual_testing_section_when_body_absent(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Manual Testing" not in body

    def test_drops_additional_notes_section_when_body_absent(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Additional Notes" not in body

    def test_renders_additional_notes_section_when_body_present(self) -> None:
        slice_data = {
            **SLICE,
            "additional_notes_body": "Follow-up: track issue #42 for migration.",
        }

        body = execute_stack._compose_body(slice_data)

        assert "Follow-up: track issue #42 for migration." in body

    def test_does_not_emit_part_of_stack_metadata(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Part of stack" not in body

    def test_does_not_emit_files_in_this_slice_metadata(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "Files in this slice" not in body

    def test_preserves_emoji_section_header_for_summary(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "## 📑 Summary" in body

    def test_preserves_emoji_section_header_for_implementation(self) -> None:
        body = execute_stack._compose_body(SLICE)

        assert "## 🛠️ Implementation" in body

    def test_renders_sections_in_canonical_order(self) -> None:
        slice_data = {
            **SLICE,
            "title": "feat(core)!: drop legacy API",
            "breaking_changes_body": "Remove the deprecated foo() shim.",
            "related_issues_body": "Closes #100",
            "manual_testing_body": "Smoke-tested locally.",
            "additional_notes_body": "Follow-up tracked in #101.",
        }

        body = execute_stack._compose_body(slice_data)
        positions = [
            body.index("## 📑 Summary"),
            body.index("## 📝 Context"),
            body.index("## 🛠️ Implementation"),
            body.index("## 💥 Breaking Changes"),
            body.index("## 🔗 Related Issues"),
            body.index("## 🧪 Manual Testing"),
            body.index("## 📋 Additional Notes"),
            body.index("## ✅ Checklist"),
        ]

        assert positions == sorted(positions)

    def test_renders_breaking_changes_section_when_body_carries_breaking_marker(self) -> None:
        # When the commit body contains "BREAKING CHANGE:" the reviewer
        # migration-steps checklist line MUST appear in the rendered output
        # (the body itself is not what populates the Breaking section here,
        # so the section drops; we assert via the reviewer checklist instead).
        slice_data = {
            **SLICE,
            "body": "Some long body.\n\nBREAKING CHANGE: foo() removed.",
        }

        body = execute_stack._compose_body(slice_data)

        assert "Migration steps in `## Breaking Changes`" in body

    def test_renders_delivered_trailer_line_in_body(self) -> None:
        slice_data = {
            **SLICE,
            "delivered_trailer": ["Manual end-to-end smoke complete"],
        }

        body = execute_stack._compose_body(slice_data)

        assert "- [x] Manual end-to-end smoke complete" in body

    def test_renders_reviewer_security_line_when_diff_touches_auth_path(self) -> None:
        slice_data = {**SLICE, "files": ["src/auth/login.ts"]}

        body = execute_stack._compose_body(slice_data)

        assert "- [ ] Security-sensitive paths reviewed" in body
