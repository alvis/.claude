#!/usr/bin/env python3
"""Compile a Discover review-surface board into a self-contained HTML artifact.

The board sources under ``examples/html`` and ``templates/html`` stay small and
editable: they keep the CDN Tailwind ``<script>`` tag plus relative / placeholder
references to ``discovery.css`` and ``discovery.js``. That preserves the local
preview + template-test workflow untouched.

This builder inlines everything so the result renders under the claude.ai
Artifact CSP (``default-src 'none'`` — no external hosts allowed): the latest
Tailwind v4 browser runtime, ``discovery.css`` and ``discovery.js`` are all
streamed verbatim into the output. Nobody ever hand-edits the compiled file — to
change styling or behaviour, edit the small sources under ``assets/`` and rebuild.

Two output modes:

* default (full document) — a standalone ``.html`` for ``file://`` viewing or any
  other host. Keeps ``<!doctype>/<html>/<head>/<body>``.
* ``--artifact`` (head-less fragment) — the Artifact tool wraps supplied content
  in its own ``<!doctype><html><head></head><body>`` and ignores author-supplied
  ``<html>/<head>/<body>``. This mode emits only the inlined ``<style>``/
  ``<script>`` blocks, the ``<style type="text/tailwindcss">`` theme block, and
  the body's inner markup — ready to hand straight to the Artifact tool.

The Tailwind runtime is downloaded on request, never committed. Each build fetches
the latest 4.x runtime from the CDN, patches it (see below) at download time, and
writes it to a gitignored cache (``assets/html/vendor/tailwind-browser.cache.js``)
that exists only as an offline fallback. A default build fetches latest and, if the
network is unavailable, falls back to the cache with a warning. ``--refresh-tailwind``
force-fetches the latest into the cache and fails loudly on any network error (it is
an explicit request for the newest runtime). ``--offline`` skips fetching entirely
and uses the cache, erroring if none exists.

Board sources are authored as small modular sources — one file per section, never
one giant HTML file. A board source may be a DIRECTORY containing ``page.html`` (the
shell with the full head/chrome and exactly one ``<!-- {{SECTIONS}} -->`` marker
line) plus ``sections/NN-<slug>.html`` files, each holding a single section. The
builder composes the page by replacing the marker line with the section files'
contents concatenated verbatim in sorted filename order. ``--emit-page`` writes that
composed page back to the committed single-file location so it stays in lockstep with
its modular sources.

CRITICAL deploy gotcha the builder guarantees against: the minified Tailwind
bundle embeds literal U+FFFD replacement chars (its CSS-parser sentinel, inside
string literals). The Artifact deploy validator rejects any content containing a
raw U+FFFD byte. The fix is to escape each as the 6-char ASCII ``\\uFFFD`` — byte
different on disk, identical at JS parse time. The builder patches at download time
and fails the build if any raw U+FFFD survives in the output.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


DISCOVER_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = DISCOVER_ROOT / "assets" / "html"
VENDOR_ROOT = ASSETS_ROOT / "vendor"
EXAMPLES_ROOT = DISCOVER_ROOT / "examples" / "html"
TEMPLATES_ROOT = DISCOVER_ROOT / "templates" / "html"
EXAMPLES_SRC_ROOT = DISCOVER_ROOT / "examples" / "src"
TEMPLATES_SRC_ROOT = DISCOVER_ROOT / "templates" / "src"

DISCOVERY_CSS = ASSETS_ROOT / "discovery.css"
DISCOVERY_JS = ASSETS_ROOT / "discovery.js"
# The Tailwind runtime is downloaded on request (latest 4.x), never committed.
# The cache is a gitignored offline fallback, primed on each successful fetch.
TAILWIND_CDN_URL = "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"
TAILWIND_CACHE = VENDOR_ROOT / "tailwind-browser.cache.js"

# The single marker line a directory source's page.html carries in place of its
# composed sections.
SECTIONS_MARKER = "<!-- {{SECTIONS}} -->"

# Raw U+FFFD REPLACEMENT CHARACTER, spelled as an escape so an encoding mishap in
# this source cannot be mistaken for an intentional literal, and its safe escape.
RAW_FFFD = "\ufffd"
ESCAPED_FFFD = "\\uFFFD"

GENERATED_BANNER = (
    "GENERATED — do not edit; edit sources under "
    "plugins/essential/skills/discover/assets/ and rebuild with "
    "scripts/build_artifact.py"
)

# Restores the only body-level styling lost when the Artifact tool supplies its
# own <body> in fragment mode: the source body's selection colours. Background,
# text colour and the ambient gradient all come from discovery.css's element
# rules (body{} / body::before{}), which apply to the Artifact's own body
# unchanged. Both vars are theme-aware (redefined under [data-theme="dark"]).
SELECTION_STYLE = (
    "<style>\n"
    "      ::selection {\n"
    "        background: var(--ui-accent-soft);\n"
    "        color: var(--ui-accent-ink);\n"
    "      }\n"
    "    </style>"
)

# Matches the CDN Tailwind runtime <script> tag in a board source.
TAILWIND_TAG_RE = re.compile(
    r'<script\s+src="https://cdn\.jsdelivr\.net/npm/@tailwindcss/browser@[^"]*"\s*>'
    r"</script>"
)
# Matches the discovery.css <link>, whether a relative ref or the placeholder.
CSS_LINK_RE = re.compile(
    r'<link\s+rel="stylesheet"\s+href="'
    r"(?:[^\"]*discovery\.css|\{\{DISCOVERY_CSS_URL\}\})"
    r'"\s*/?>'
)
# Matches the discovery.js <script>, whether a relative ref or the placeholder.
JS_SCRIPT_RE = re.compile(
    r'<script\s+src="'
    r"(?:[^\"]*discovery\.js|\{\{DISCOVERY_JS_URL\}\})"
    r'"\s+defer\s*>\s*</script>'
)

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
THEME_STYLE_RE = re.compile(
    r'<style\s+type="text/tailwindcss">.*?</style>', re.DOTALL
)
BODY_RE = re.compile(r"<body\b[^>]*>(.*?)</body>", re.DOTALL)
# Discover template placeholders are {{UPPER_SNAKE}}; bare braces in minified JS
# (the Tailwind runtime) must NOT be flagged.
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")


class BuildError(RuntimeError):
    """Raised when a board source cannot be compiled into a valid artifact."""


def patch_fffd(text: str) -> str:
    """Escape every raw U+FFFD so the Artifact deploy validator accepts it."""

    return text.replace(RAW_FFFD, ESCAPED_FFFD)


def get_tailwind_runtime(*, refresh: bool = False, offline: bool = False) -> str:
    """Return the Tailwind browser runtime text, downloading the latest on request.

    * ``offline``: read the cache or raise if none exists — never touch the network.
    * otherwise: fetch the latest 4.x runtime from the CDN, patch the U+FFFD
      sentinel, fail if any raw U+FFFD survives, write the cache, and return it.
    * on fetch failure (URLError/OSError/timeout): fall back to the cache with a
      warning to stderr when one exists — unless ``refresh`` is set, in which case
      the failure is fatal (the caller explicitly asked for the newest runtime).
    """

    if offline:
        if TAILWIND_CACHE.is_file():
            return TAILWIND_CACHE.read_text(encoding="utf-8")
        raise BuildError(
            "no cached Tailwind runtime; run once with network or without --offline"
        )

    try:
        with urllib.request.urlopen(TAILWIND_CDN_URL, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as error:
        if not refresh and TAILWIND_CACHE.is_file():
            print(
                f"warning: could not fetch latest Tailwind ({error}); "
                f"falling back to cached runtime {TAILWIND_CACHE}",
                file=sys.stderr,
            )
            return TAILWIND_CACHE.read_text(encoding="utf-8")
        raise BuildError(
            f"could not fetch Tailwind runtime from {TAILWIND_CDN_URL}: {error}"
        )

    patched = patch_fffd(raw)
    if RAW_FFFD in patched:
        raise BuildError(
            "U+FFFD survived patching the downloaded Tailwind runtime"
        )
    VENDOR_ROOT.mkdir(parents=True, exist_ok=True)
    TAILWIND_CACHE.write_text(patched, encoding="utf-8")
    return patched


def _read(path: Path, label: str) -> str:
    if not path.is_file():
        raise BuildError(f"Missing {label}: {path}")
    return path.read_text(encoding="utf-8")


def _inline_script(body: str) -> str:
    """Wrap already-read JS in a script tag, escaping any </script> break-out."""

    safe = body.replace("</script", "<\\/script")
    return f"<script>\n{safe}\n</script>"


def _inline_style(body: str) -> str:
    if "</style" in body:
        raise BuildError("stylesheet contains a </style break-out sequence")
    return f"<style>\n{body}\n</style>"


def resolve_source(source: str) -> Path:
    """Resolve a board argument to a source (directory, path, example, template).

    A directory source (modular sections) is preferred over a single-file source
    of the same slug. Search order for a slug: examples/src/<slug>/,
    templates/src/<slug>/, examples/html/<slug>.html, templates/html/<slug>.html.
    """

    candidate = Path(source)
    if candidate.is_dir():
        if not (candidate / "page.html").is_file():
            raise BuildError(f"directory source missing page.html: {candidate}")
        return candidate.resolve()
    if candidate.is_file():
        return candidate.resolve()
    stem = source.removesuffix(".html")
    for src_dir in (EXAMPLES_SRC_ROOT / stem, TEMPLATES_SRC_ROOT / stem):
        if (src_dir / "page.html").is_file():
            return src_dir.resolve()
    for guess in (EXAMPLES_ROOT / f"{stem}.html", TEMPLATES_ROOT / f"{stem}.html"):
        if guess.is_file():
            return guess.resolve()
    raise BuildError(
        f"No board source found for {source!r} (looked in "
        f"{EXAMPLES_SRC_ROOT}, {TEMPLATES_SRC_ROOT}, "
        f"{EXAMPLES_ROOT} and {TEMPLATES_ROOT})"
    )


def compose_directory(source_dir: Path) -> str:
    """Compose a directory source's page.html + sections/ into one HTML string.

    The single ``<!-- {{SECTIONS}} -->`` marker line (surrounding whitespace
    allowed) is replaced verbatim — including its newline — by the concatenation
    of the ``sections/*.html`` files in sorted filename order, with no added
    separators (byte-exact concatenation).
    """

    page = source_dir / "page.html"
    if not page.is_file():
        raise BuildError(f"directory source missing page.html: {page}")
    shell = page.read_text(encoding="utf-8")

    sections_dir = source_dir / "sections"
    section_files = (
        sorted(sections_dir.glob("*.html")) if sections_dir.is_dir() else []
    )
    if not section_files:
        raise BuildError(
            f"directory source needs at least one sections/*.html file: "
            f"{sections_dir}"
        )

    marker_re = re.compile(
        r"^[^\S\n]*" + re.escape(SECTIONS_MARKER) + r"[^\S\n]*(?:\n|$)",
        re.MULTILINE,
    )
    matches = marker_re.findall(shell)
    if len(matches) != 1:
        raise BuildError(
            f"page.html must contain exactly one {SECTIONS_MARKER!r} marker "
            f"line; found {len(matches)}"
        )

    sections = "".join(f.read_text(encoding="utf-8") for f in section_files)
    return marker_re.sub(lambda _m: sections, shell, count=1)


def load_source(source_path: Path) -> tuple[str, str]:
    """Return (html_text, display_path) for a file or composed directory source."""

    if source_path.is_dir():
        return compose_directory(source_path), str(source_path)
    return _read(source_path, "board source"), str(source_path)


def build(source_path: Path, *, artifact: bool, runtime: str | None = None) -> str:
    """Compile a board source into a self-contained document or fragment.

    ``runtime`` is the Tailwind runtime text; when omitted the latest is fetched
    (with cache fallback) via ``get_tailwind_runtime()``.
    """

    html, _display = load_source(source_path)
    if runtime is None:
        runtime = get_tailwind_runtime()
    css = _read(DISCOVERY_CSS, "discovery.css")
    js = _read(DISCOVERY_JS, "discovery.js")

    # discovery.js loads with `defer` in the source; an inline script cannot
    # defer, so it is removed from its original position and re-emitted at the
    # end of <body> to preserve the "runs after DOM is parsed" ordering.
    js_block = _inline_script(js)

    if not TAILWIND_TAG_RE.search(html):
        raise BuildError("Tailwind CDN <script> tag not found in source")
    if not CSS_LINK_RE.search(html):
        raise BuildError("discovery.css <link> not found in source")
    if not JS_SCRIPT_RE.search(html):
        raise BuildError("discovery.js <script> not found in source")

    html = TAILWIND_TAG_RE.sub(lambda _m: _inline_script(runtime), html, count=1)
    html = CSS_LINK_RE.sub(lambda _m: _inline_style(css), html, count=1)
    html = JS_SCRIPT_RE.sub("", html, count=1)

    if artifact:
        output = _build_fragment(html, js_block)
    else:
        output = _build_full_doc(html, js_block)

    _validate(output, artifact=artifact)
    return output


def _build_full_doc(html: str, js_block: str) -> str:
    """Emit a standalone document with discovery.js relocated to end of body."""

    def _append_js(_match: re.Match[str]) -> str:
        return f"    {js_block}\n  </body>"

    html, count = re.subn(r"\s*</body>", _append_js, html, count=1)
    if count != 1:
        raise BuildError("Could not locate </body> to append discovery.js")
    return f"<!-- {GENERATED_BANNER} -->\n{html}"


def _build_fragment(html: str, js_block: str) -> str:
    """Emit a head-less fragment for the Artifact tool to wrap in its own body."""

    title_match = TITLE_RE.search(html)
    theme_match = THEME_STYLE_RE.search(html)
    body_match = BODY_RE.search(html)
    if not (title_match and theme_match and body_match):
        missing = [
            name
            for name, ok in (
                ("<title>", title_match),
                ('<style type="text/tailwindcss">', theme_match),
                ("<body>", body_match),
            )
            if not ok
        ]
        raise BuildError(f"Fragment source missing: {', '.join(missing)}")

    # The inlined discovery.css <style> and the Tailwind runtime <script> already
    # live in the head region of `html`; pull them out to lead the fragment.
    css_style = _find_inlined_css_style(html)
    runtime_script = _find_inlined_runtime_script(html)

    body_inner = body_match.group(1).strip()

    parts = [
        f"<!-- {GENERATED_BANNER} -->",
        f"<title>{title_match.group(1).strip()}</title>",
        theme_match.group(0),
        SELECTION_STYLE,
        css_style,
        runtime_script,
        body_inner,
        js_block,
    ]
    return "\n".join(parts) + "\n"


def _find_inlined_css_style(html: str) -> str:
    """Return the first bare <style> block — the inlined discovery.css.

    The theme block is excluded because it carries a ``type="text/tailwindcss"``
    attribute, so a bare-``<style>`` match cannot land on it; discovery.js has
    already been removed before this runs.
    """

    match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    if not match:
        raise BuildError("Inlined discovery.css <style> block not found")
    return match.group(0)


def _find_inlined_runtime_script(html: str) -> str:
    """Return the first bare <script> block — the inlined Tailwind runtime."""

    match = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    if not match:
        raise BuildError("Inlined Tailwind runtime <script> block not found")
    return match.group(0)


def _validate(output: str, *, artifact: bool) -> None:
    """Fail the build unless the output is genuinely self-contained."""

    problems: list[str] = []

    if 'src="http' in output:
        problems.append('external script host present (src="http...)')
    if 'href="http' in output:
        problems.append('external href host present (href="http...)')
    # Only Discover template placeholders ({{UPPER_SNAKE}}) count — the minified
    # Tailwind runtime legitimately contains bare `{{`/`}}` in its JS.
    leftover = PLACEHOLDER_RE.findall(output)
    if leftover:
        problems.append(f"unfilled placeholder(s) left in output: {sorted(set(leftover))}")

    raw_fffd = output.encode("utf-8").count(RAW_FFFD.encode("utf-8"))
    if raw_fffd:
        problems.append(f"{raw_fffd} raw U+FFFD byte(s) present (deploy will 400)")

    if "@tailwindcss/browser" not in output:
        problems.append("Tailwind runtime not inlined")
    if "--ui-canvas" not in output:
        problems.append("discovery.css not inlined")
    if "data-discovery-prompt-host" not in output:
        problems.append("board markup missing")
    if "[data-discovery-prompt-host]" not in output:
        problems.append("discovery.js not inlined")

    if artifact:
        if re.search(r"<!doctype", output, re.IGNORECASE):
            problems.append("fragment must not contain <!doctype>")
        if re.search(r"<html\b", output, re.IGNORECASE):
            problems.append("fragment must not contain <html>")
        if re.search(r"<body\b", output, re.IGNORECASE):
            problems.append("fragment must not contain <body>")

    if problems:
        raise BuildError(
            "self-containment validation failed:\n  - " + "\n  - ".join(problems)
        )


def emit_page_default(source_dir: Path) -> Path:
    """Default --emit-page target: the committed single-file page for a src dir."""

    parent = source_dir.parent.resolve()
    name = source_dir.name
    if parent == EXAMPLES_SRC_ROOT.resolve():
        return EXAMPLES_ROOT / f"{name}.html"
    if parent == TEMPLATES_SRC_ROOT.resolve():
        return TEMPLATES_ROOT / f"{name}.html"
    raise BuildError(
        "--emit-page needs an explicit PATH for a directory source outside "
        "examples/src/ or templates/src/"
    )


def default_output(source_path: Path, artifact: bool) -> Path:
    """Choose a throwaway dist path so compiled output never overwrites a source."""

    dist = Path(tempfile.gettempdir()) / "essential-discover-dist"
    dist.mkdir(parents=True, exist_ok=True)
    suffix = ".artifact.html" if artifact else ".html"
    return dist / f"{source_path.stem}{suffix}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "source",
        nargs="?",
        help="Board source: a path, an examples/ slug, or a templates/ slug",
    )
    parser.add_argument(
        "--artifact",
        action="store_true",
        help="Emit a head-less fragment ready for the Artifact tool",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Output path (default: a throwaway dist location under the temp dir)",
    )
    parser.add_argument(
        "--refresh-tailwind",
        action="store_true",
        help="Force-fetch the latest Tailwind runtime into the cache (fails loudly "
        "on any network error)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip fetching; use the cached Tailwind runtime only",
    )
    parser.add_argument(
        "--emit-page",
        nargs="?",
        const=True,
        default=None,
        metavar="PATH",
        help="Compose a directory source's page and write it (default: the "
        "committed examples/html or templates/html single-file page), then exit "
        "without building an artifact",
    )
    args = parser.parse_args(argv)

    try:
        runtime_text: str | None = None
        if args.refresh_tailwind:
            runtime_text = get_tailwind_runtime(refresh=True)
            print(
                f"refreshed Tailwind runtime -> {TAILWIND_CACHE}", file=sys.stderr
            )
            if not args.source:
                return 0

        if not args.source:
            parser.error("a board source is required (or use --refresh-tailwind)")

        source_path = resolve_source(args.source)

        if args.emit_page is not None:
            if not source_path.is_dir():
                raise BuildError(
                    "--emit-page is only valid for a directory (modular) source"
                )
            composed = compose_directory(source_path)
            emit_path = (
                emit_page_default(source_path)
                if args.emit_page is True
                else Path(args.emit_page)
            )
            emit_path.parent.mkdir(parents=True, exist_ok=True)
            emit_path.write_text(composed, encoding="utf-8")
            print(str(emit_path))
            return 0

        if runtime_text is None:
            runtime_text = get_tailwind_runtime(offline=args.offline)
        output = build(source_path, artifact=args.artifact, runtime=runtime_text)
        out_path = args.out or default_output(source_path, args.artifact)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    except BuildError as error:
        print(f"build failed: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        # A filesystem error writing the output — report cleanly rather than
        # dumping a traceback.
        print(f"build failed: {error}", file=sys.stderr)
        return 1

    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
