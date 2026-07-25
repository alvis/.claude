"""Behavior tests for the doc-path resolution gate.

Every case builds a throwaway repository fixture and asserts on the
checker's findings — never on the content of any real document, which
would recreate the change-detector antipattern the gate replaces.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent / "check_doc_paths.py"
SPEC = importlib.util.spec_from_file_location("check_doc_paths", MODULE_PATH)
check_doc_paths = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_doc_paths)


class CheckDocPathsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        (self.root / "plugins").mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def check(self) -> list[str]:
        return check_doc_paths.check(self.root)

    def test_resolves_relative_to_the_containing_file(self) -> None:
        self.write("plugins/alpha/references/target.md", "x")
        self.write(
            "plugins/alpha/references/doc.md",
            "see [target](target.md) and `references/target.md`",
        )

        self.assertEqual([], self.check())

    def test_resolves_against_ancestors_and_plugin_root(self) -> None:
        self.write("plugins/alpha/skills/demo/scripts/tool.py", "x")
        self.write("plugins/alpha/references/shared.md", "x")
        # mentions addressed to the skill root and the plugin root, written
        # from a doc nested one level below each
        self.write(
            "plugins/alpha/skills/demo/references/doc.md",
            "run `scripts/tool.py` per `references/shared.md`",
        )

        self.assertEqual([], self.check())

    def test_reports_a_missing_target_with_file_and_line(self) -> None:
        self.write(
            "plugins/alpha/references/doc.md",
            "fine line\nsee [gone](../references/missing.md)\n",
        )

        findings = self.check()

        self.assertEqual(
            ["plugins/alpha/references/doc.md:2 → ../references/missing.md"],
            findings,
        )

    def test_substitutes_plugin_dir_before_resolving(self) -> None:
        self.write("plugins/alpha/references/hook.md", "x")
        self.write(
            "plugins/alpha/CLAUDE.md",
            "read `{{PLUGIN_DIR}}/references/hook.md` "
            "but not `{{PLUGIN_DIR}}/references/gone.md`",
        )

        findings = self.check()

        self.assertEqual(
            ["plugins/alpha/CLAUDE.md:1 → {{PLUGIN_DIR}}/references/gone.md"],
            findings,
        )

    def test_skips_fenced_code_blocks(self) -> None:
        self.write(
            "plugins/alpha/doc.md",
            "```bash\ncat plugins/alpha/nowhere.md\n[x](missing/gone.md)\n```\n",
        )

        self.assertEqual([], self.check())

    def test_skips_runtime_placeholder_bare_and_absolute_mentions(self) -> None:
        self.write(
            "plugins/alpha/doc.md",
            "\n".join(
                (
                    "state under `.state/works/demo/goal.md`",
                    "promoted to `docs/architecture/index.md`",
                    "memory in `.claude/agent-memory/lead/MEMORY.md`",
                    "work state in `state/working.md`",
                    "review detail in `reviews/quality.md`",
                    "a target repo's `.github/PULL_REQUEST_TEMPLATE.md`",
                    "each `plugins/<p>/skills/<name>/SKILL.md`",
                    "template `references/{{SLUG}}.md`",
                    "generated `operations/{operationName}.ts`",
                    "the bare `SKILL.md` file",
                    "a machine path `/usr/local/bin/tool.sh`",
                )
            ),
        )

        self.assertEqual([], self.check())

    def test_skips_illustrative_paths_and_documents(self) -> None:
        # `services` is on the example-segment allowlist: a naming example
        self.write("plugins/alpha/doc.md", "name it `services/user.ts`")
        # template/example documents describe a generated tree
        self.write("plugins/alpha/references/plan.template.md", "[s](../state.md)")
        self.write("plugins/alpha/references/README.example.cli.md", "[l](./LICENSE)")

        self.assertEqual([], self.check())

    def test_reports_a_missing_directory_not_on_the_example_allowlist(self) -> None:
        # a renamed or deleted real directory must fail the gate, never
        # silently reclassify as an example
        self.write("plugins/alpha/doc.md", "see `renamed-dir/tool.py`")

        self.assertEqual(
            ["plugins/alpha/doc.md:1 → renamed-dir/tool.py"], self.check()
        )

    def test_checks_this_repos_own_github_directory(self) -> None:
        self.write(".github/workflows/ci.yml", "x")
        self.write(
            "AGENTS.md",
            "CI in `.github/workflows/ci.yml`, not `.github/workflows/gone.yml`",
        )

        self.assertEqual(
            ["AGENTS.md:1 → .github/workflows/gone.yml"], self.check()
        )

    def test_ignore_marker_skips_the_line(self) -> None:
        self.write(
            "plugins/alpha/doc.md",
            "never cite `fake-dir/ghost.md` <!-- doc-path-gate: ignore -->\n"
            "but `fake-dir/other.md` is still checked\n",
        )

        self.assertEqual(
            ["plugins/alpha/doc.md:2 → fake-dir/other.md"], self.check()
        )

    def test_link_labels_are_display_prose_not_claims(self) -> None:
        self.write("plugins/alpha/references/target.md", "x")
        # the backticked label names a package-internal path; the link
        # target is the claim, and it resolves
        self.write(
            "plugins/alpha/doc.md",
            "[`inner/module.py`](references/target.md) explains it",
        )

        self.assertEqual([], self.check())

    def test_resolves_against_the_plugin_constitution(self) -> None:
        self.write("plugins/alpha/constitution/standards/testing/write.md", "x")
        self.write(
            "plugins/alpha/skills/demo/references/doc.md",
            "read `testing/write.md` and `standards/testing/write.md`",
        )

        self.assertEqual([], self.check())

    def test_checks_root_documents_and_strips_anchors(self) -> None:
        self.write("scripts/tool.py", "x")
        self.write("AGENTS.md", "see [tool](scripts/tool.py#usage)")
        self.write("README.md", "see [gone](scripts/gone.py)")

        self.assertEqual(["README.md:1 → scripts/gone.py"], self.check())

    def test_ignores_external_links_and_pure_anchors(self) -> None:
        self.write(
            "plugins/alpha/doc.md",
            "[a](https://example.com/x.md) [b](mailto:x@y.z) [c](#section)",
        )

        self.assertEqual([], self.check())


if __name__ == "__main__":
    unittest.main()
