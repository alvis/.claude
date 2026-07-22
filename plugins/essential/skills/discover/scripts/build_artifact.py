#!/usr/bin/env python3
"""Compile a Discover review-surface board into a self-contained HTML artifact.

The board sources under ``examples/`` and ``templates/`` stay small and editable
and carry NO asset references: no CDN Tailwind ``<script>``, no ``discovery.css``
``<link>``, and no ``discovery.js`` ``<script>`` — external OR relative. A source
keeps only its own inline markup, its inline page-behaviour ``<script>`` blocks,
inline ``<style>`` blocks, and the ``<style type="text/tailwindcss">`` ``@theme``
block. The builder injects every shared asset into every final file.

This builder injects everything so the result renders under the claude.ai
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

# SOURCE validation: board sources carry no asset references at all. Any
# <script src=...> or <link rel="stylesheet"> (external OR relative) is forbidden,
# as is the dead {{DISCOVERY_CSS_URL}}/{{DISCOVERY_JS_URL}} placeholder convention.
# Inline <script> (page behaviour) and inline <style> blocks stay allowed.
SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*\bsrc\s*=", re.IGNORECASE)
STYLESHEET_LINK_RE = re.compile(
    r"<link\b[^>]*\brel\s*=\s*[\"']?stylesheet", re.IGNORECASE
)
DEAD_ASSET_PLACEHOLDER_RE = re.compile(r"\{\{DISCOVERY_(?:CSS|JS)_URL\}\}")

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
    _validate_source(html)
    if runtime is None:
        runtime = get_tailwind_runtime()
    css = _read(DISCOVERY_CSS, "discovery.css")
    js = _read(DISCOVERY_JS, "discovery.js")

    css_style = _inline_style(css)
    runtime_script = _inline_script(runtime)
    # discovery.js loads with `defer` in the source; an inline script cannot
    # defer, so it is injected at the end of <body> to preserve the "runs after
    # DOM is parsed" ordering.
    js_block = _inline_script(js)

    if artifact:
        output = _build_fragment(html, css_style, runtime_script, js_block)
    else:
        output = _build_full_doc(html, css_style, runtime_script, js_block)

    _validate(output, artifact=artifact)
    return output


def _validate_source(html: str) -> None:
    """Fail the build unless the board source carries no asset references.

    A source must contain no ``<script src=...>`` and no ``<link
    rel="stylesheet">`` — any src/href asset reference, external OR relative, is
    forbidden — and none of the dead ``{{DISCOVERY_CSS_URL}}`` /
    ``{{DISCOVERY_JS_URL}}`` placeholders. Inline ``<script>`` (page behaviour),
    inline ``<style>`` blocks, and non-asset ``<link>`` tags (e.g. a ``data:``
    favicon) stay allowed. The builder injects every shared asset itself.
    """

    problems: list[str] = []
    if SCRIPT_SRC_RE.search(html):
        problems.append(
            "<script src=...> asset reference present (sources carry no external "
            "or relative script refs; the builder injects discovery.js)"
        )
    if STYLESHEET_LINK_RE.search(html):
        problems.append(
            '<link rel="stylesheet"> asset reference present (sources carry no '
            "external or relative stylesheet refs; the builder injects discovery.css)"
        )
    dead = DEAD_ASSET_PLACEHOLDER_RE.findall(html)
    if dead:
        problems.append(
            f"dead asset-URL placeholder(s) present: {sorted(set(dead))} "
            "(that convention is gone; the builder injects the assets)"
        )
    problems.extend(_board_theme_problems(html))
    problems.extend(_stray_color_problems(html))
    if problems:
        raise BuildError(
            "source validation failed:\n  - " + "\n  - ".join(problems)
        )


BOARD_THEME_BLOCK_RE = re.compile(
    r"<style[^>]*\bdata-board-theme\b[^>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE
)
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE)
SCRIPT_BLOCK_RE = re.compile(r"<script[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
CUSTOM_PROP_RE = re.compile(r"(--[\w-]+)\s*:")
# The only tokens a board-theme overlay may redefine (references/features.md §B).
BOARD_THEME_WHITELIST_RE = re.compile(
    r"^--ui-(?:"
    r"accent(?:-contrast|-soft|-ink)?"
    r"|verdict-[a-z]+(?:-soft|-ink)?"
    r"|status-[a-z]+(?:-soft|-ink)?"
    r"|k-[a-z]+(?:-soft|-ink)?"
    r")$"
)
# `${…}` in rendered text means a template literal escaped its script — the
# free-form-generation bug this pipeline exists to prevent. Script/style bodies
# legitimately contain template literals and are stripped before the check.
DOLLAR_LITERAL_RE = re.compile(r"\$\{[^}]{1,120}\}")


def _board_theme_problems(html: str) -> list[str]:
    """Validate the optional <style data-board-theme> overlay block."""

    problems: list[str] = []
    for block in BOARD_THEME_BLOCK_RE.findall(html):
        css = CSS_COMMENT_RE.sub("", block)
        tokens = CUSTOM_PROP_RE.findall(css)
        bad = sorted({t for t in tokens if not BOARD_THEME_WHITELIST_RE.match(t)})
        if bad:
            problems.append(
                f"board-theme overlay redefines non-whitelisted token(s): {bad} "
                "(allowed: --ui-accent*, --ui-verdict-*, --ui-status-*, --ui-k-*)"
            )
        if not tokens:
            continue
        light: set[str] = set()
        dark: set[str] = set()
        for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            selector, body = match.group(1).strip(), match.group(2)
            names = set(CUSTOM_PROP_RE.findall(body))
            if 'data-theme="dark"' in selector or "data-theme='dark'" in selector:
                dark |= names
            else:
                light |= names
        missing_dark = sorted(light - dark)
        missing_light = sorted(dark - light)
        if missing_dark:
            problems.append(
                f"board-theme overlay lacks dark values for: {missing_dark} "
                "(every redefined token needs :root AND [data-theme=\"dark\"] values)"
            )
        if missing_light:
            problems.append(
                f"board-theme overlay lacks light values for: {missing_light} "
                "(every redefined token needs :root AND [data-theme=\"dark\"] values)"
            )
    return problems


def _stray_color_problems(html: str) -> list[str]:
    """Color literals belong in the board-theme overlay or [data-specimen] CSS.

    Everything else styles through the ``--ui-*`` tokens, so raw hex /
    rgb / oklch values in ordinary inline <style> blocks are almost always a
    palette leak. Blocks that scope themselves to ``[data-specimen]`` keep the
    long-standing specimen exemption.
    """

    problems: list[str] = []
    without_board_theme = BOARD_THEME_BLOCK_RE.sub("", html)
    for block in STYLE_BLOCK_RE.findall(without_board_theme):
        if "data-specimen" in block:
            continue
        css = CSS_COMMENT_RE.sub("", block)
        # Only raw hex is flagged: color-mix()/oklch() over --ui-* tokens is a
        # legitimate idiom in bespoke section CSS.
        raw_hex = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
        if raw_hex:
            problems.append(
                f"raw color literal(s) outside the board-theme overlay: "
                f"{sorted(set(raw_hex))[:6]} (style through --ui-* tokens, or move "
                "board palette changes into <style data-board-theme>)"
            )
    return problems


def _dollar_literal_problems(output: str) -> list[str]:
    """Find `${…}` sequences in rendered text (scripts/styles stripped)."""

    visible = SCRIPT_BLOCK_RE.sub("", output)
    visible = STYLE_BLOCK_RE.sub("", visible)
    hits = DOLLAR_LITERAL_RE.findall(visible)
    if hits:
        preview = sorted(set(hits))[:5]
        return [
            f"un-interpolated template literal(s) in rendered text: {preview} "
            "(a JS card template escaped its script — interpolate before emit)"
        ]
    return []


def _build_full_doc(
    html: str, css_style: str, runtime_script: str, js_block: str
) -> str:
    """Emit a standalone document with all shared assets injected.

    The inlined discovery.css ``<style>`` then the Tailwind runtime ``<script>``
    are injected immediately before ``</head>`` (css first, runtime second);
    discovery.js is injected at the end of ``<body>``.
    """

    def _inject_head(_match: re.Match[str]) -> str:
        return f"\n    {css_style}\n    {runtime_script}\n  </head>"

    html, count = re.subn(r"\s*</head>", _inject_head, html, count=1)
    if count != 1:
        raise BuildError(
            "Could not locate </head> to inject discovery.css and the Tailwind runtime"
        )

    def _append_js(_match: re.Match[str]) -> str:
        return f"    {js_block}\n  </body>"

    html, count = re.subn(r"\s*</body>", _append_js, html, count=1)
    if count != 1:
        raise BuildError("Could not locate </body> to append discovery.js")
    return f"<!-- {GENERATED_BANNER} -->\n{html}"


def _build_fragment(
    html: str, css_style: str, runtime_script: str, js_block: str
) -> str:
    """Emit a head-less fragment for the Artifact tool to wrap in its own body.

    Part ordering: title, theme block, selection style, css, runtime, body, js.
    """

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

    problems.extend(_dollar_literal_problems(output))

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
