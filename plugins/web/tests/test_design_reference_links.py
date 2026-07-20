from __future__ import annotations

from pathlib import Path
import re
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
FACELIFT = PLUGIN / "skills/design/references/facelift.md"


def heading_anchor(heading: str) -> str:
    without_punctuation = re.sub(r"[^a-z0-9\s-]", "", heading.lower())
    return re.sub(r"[\s-]+", "-", without_punctuation).strip("-")


class DesignReferenceLinkTest(unittest.TestCase):
    def test_facelift_motion_library_anchor_resolves(self) -> None:
        source = FACELIFT.read_text(encoding="utf-8")
        match = re.search(r"\[Motion Libraries\]\(([^)#]+)#([^)]+)\)", source)
        self.assertIsNotNone(match)
        relative, anchor = match.groups()
        target = FACELIFT.parent / relative

        self.assertTrue(target.is_file())
        headings = {
            heading_anchor(line.removeprefix("## "))
            for line in target.read_text(encoding="utf-8").splitlines()
            if line.startswith("## ")
        }
        self.assertIn(anchor, headings)


if __name__ == "__main__":
    unittest.main()
