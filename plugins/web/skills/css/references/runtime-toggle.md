# Runtime `data-theme` Toggle — Consumer Recipe

> **Guidance only.** The `web:css` skill emits CSS, not JavaScript. This document is for downstream consumers who want an explicit light/dark toggle on top of the CSS-only scaffold. If your product is happy following the OS preference only, you can skip everything below — leave `<html>` without `data-theme` and `prefers-color-scheme` resolves it.

## Three States

| State | `<html>` attribute | Resolves via |
|-------|--------------------|--------------|
| Light (explicit) | `data-theme="light"` | `:root[data-theme="light"]` selector |
| Dark (explicit) | `data-theme="dark"` | `:root[data-theme="dark"]` selector |
| System (default) | _attribute absent_ | `prefers-color-scheme` media query against `:root:not([data-theme])` |

Setting `data-theme=""` or `data-theme="system"` is **not** how system mode is expressed — the attribute must be removed entirely.

## localStorage Persistence

Pick one key (suggested: `theme`) and store one of `"light"`, `"dark"`, or nothing (key removed) for system. Read on every toggle and rehydrate before paint.

## FOUC Prevention — Inline `<head>` Script

Run **before** any stylesheet that paints the page. Place this as the first child of `<head>` (after `<meta charset>`), synchronously, **not** as a deferred or module script.

```html
<script>
  (function () {
    try {
      var stored = localStorage.getItem('theme');
      if (stored === 'light' || stored === 'dark') {
        document.documentElement.setAttribute('data-theme', stored);
      }
    } catch (_) {
      /* localStorage unavailable; fall through to system */
    }
  })();
</script>
```

## Vanilla Toggle

```js
function setTheme(next /* 'light' | 'dark' | 'system' */) {
  const root = document.documentElement;
  if (next === 'system') {
    root.removeAttribute('data-theme');
    localStorage.removeItem('theme');
  } else {
    root.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  }
}
```

## Framework Notes

- **React (client component)** — call `setTheme` from a `useCallback`; do not put the inline script in a `useEffect` (it runs after paint, defeats FOUC fix).
- **Next.js App Router** — keep the inline script in `app/layout.tsx` rendered directly inside `<head>` (Server Component); the toggle UI itself lives in a `'use client'` component.
- **Vue / Nuxt** — equivalent pattern: inline script in `app.html` / `nuxt.config` `head` array; toggle component is client-only.
