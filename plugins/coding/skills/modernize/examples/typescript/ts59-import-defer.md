---
since: "TS 5.9"
min-es-target: "any"
module: "esnext or nodenext"
---

## Detection

`await import\(` used for lazy/deferred module loading, or `require\(` used for lazy loading in ESM files

## Before

```typescript
// Dynamic import() — async, requires await, cannot be used at module scope synchronously
export async function renderChart(data: number[]) {
  // Heavy charting library loaded only when needed
  const { Chart } = await import("chart.js");
  return new Chart(data);
}

export async function generatePDF(html: string) {
  // Loaded on demand to reduce startup time
  const puppeteer = await import("puppeteer");
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(html);
  return page.pdf();
}
```

```typescript
// Eager import — loaded and evaluated immediately at startup even if rarely used
import * as heavyLib from "heavy-computation-lib";
import * as reportGenerator from "./reports/generator.ts";

export function handleRequest(type: string) {
  if (type === "compute") {
    return heavyLib.process();
  }
  if (type === "report") {
    return reportGenerator.generate();
  }
  return null;
}
```

## After

```typescript
// import defer — synchronous access, but module evaluation is deferred
import defer * as Chart from "chart.js";
import defer * as puppeteer from "puppeteer";

export function renderChart(data: number[]) {
  // chart.js is loaded and evaluated on first property access
  return new Chart.Chart(data);
}

export async function generatePDF(html: string) {
  // puppeteer is loaded on first access — no await needed for the import
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(html);
  return page.pdf();
}
```

```typescript
// Deferred imports for conditionally-used heavy dependencies
import defer * as heavyLib from "heavy-computation-lib";
import defer * as reportGenerator from "./reports/generator.ts";

export function handleRequest(type: string) {
  if (type === "compute") {
    // heavyLib is evaluated here on first access
    return heavyLib.process();
  }
  if (type === "report") {
    // reportGenerator is evaluated here on first access
    return reportGenerator.generate();
  }
  return null;
}
```

## Conditions

- TC39 Stage 3 proposal (Deferred Module Evaluation); supported in TS 5.9 with `--module esnext` or `--module nodenext`
- Only works with namespace imports (`import defer * as name from "..."`); named imports are not supported with `defer`
- Module evaluation is deferred until the first property access on the namespace object
- The module is still fetched/linked at load time; only evaluation (execution of module body) is deferred
- Particularly useful for improving application startup time by deferring heavy dependencies
- If the deferred module has side effects that must run at import time, do not use `defer`
- Cannot defer modules with top-level `await` in all environments (behavior may vary by runtime)
