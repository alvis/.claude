// Evaluate this expression in a freshly loaded example page. It returns behavioral
// evidence, throws at the first failed assertion, and changes only this page's DOM.
(async () => {
  const checks = [];
  const find = (selector) => {
    const element = document.querySelector(selector);
    if (!element) throw new Error(`Missing control: ${selector}`);
    return element;
  };
  const check = (name, condition) => {
    if (!condition) throw new Error(`Failed: ${name}`);
    checks.push(name);
  };
  const click = (selector) => find(selector).click();
  const enter = (selector, value) => {
    const input = find(selector);
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  };
  const surface = location.pathname.split("/").at(-2);

  if (surface === "landing-page") {
    click('[data-period="yearly"]');
    check(
      "annual total and period update together",
      [...document.querySelectorAll(".price")]
        .map((node) => node.textContent)
        .join() === "$72,$168" &&
        [...document.querySelectorAll(".period")].every((node) =>
          node.textContent.includes("year"),
        ),
    );
    click('[data-plan="Shared"] .choose');
    click('[data-plan="Quiet"] .choose');
    check(
      "plan selection replaces the previous selection",
      document.querySelectorAll(".plan.selected").length === 1 &&
        find(".plan.selected").dataset.plan === "Quiet" &&
        find("#selection").textContent.includes("Quiet"),
    );
    click('[data-period="monthly"]');
    check(
      "monthly billing restores both prices",
      [...document.querySelectorAll(".price")]
        .map((node) => node.textContent)
        .join() === "$8,$18" &&
        find('[data-period="monthly"]').getAttribute("aria-pressed") === "true",
    );
    const task = find('[aria-label="Monday task"]');
    task.focus();
    document.execCommand("selectAll", false);
    document.execCommand("insertText", false, "Prepare the field notes");
    check(
      "sample planner accepts an editable task",
      task.textContent === "Prepare the field notes",
    );
  } else if (surface === "blog") {
    click('[data-category="Places"]');
    enter("#search", "shade");
    click("#search-button");
    check(
      "category and search intersect",
      document.querySelectorAll("[data-article]").length === 1 &&
        find("[data-article]").textContent.includes(
          "A city mapped by its shade",
        ),
    );
    click("[data-article]");
    check(
      "reading view matches selected story metadata",
      find("#article").classList.contains("active") &&
        find("#article-title").textContent === "A city mapped by its shade" &&
        find(".article-header .topic").textContent.includes("Places") &&
        find(".article-header .byline").textContent.includes("Mina Cole"),
    );
    click("#back");
    check(
      "return preserves query, category, and focused result",
      find("#search").value === "shade" &&
        find('[data-category="Places"]').getAttribute("aria-pressed") ===
          "true" &&
        document.querySelectorAll("[data-article]").length === 1 &&
        document.activeElement === find("[data-article]"),
    );
    enter("#search", "unfindable-story");
    click("#search-button");
    check(
      "empty search exposes recovery",
      document.querySelectorAll("[data-article]").length === 0 &&
        !!find("#empty-reset"),
    );
    click("#empty-reset");
    check(
      "reset restores all stories and clears both filters",
      document.querySelectorAll("[data-article]").length === 5 &&
        find("#search").value === "" &&
        find('[data-category="All"]').getAttribute("aria-pressed") === "true",
    );
    click("[data-article]");
    check(
      "reading hides discovery controls while keeping return available",
      getComputedStyle(find(".controls")).display === "none" &&
        find("#back").getClientRects().length > 0,
    );
    click("#back");
    check(
      "return restores usable discovery controls",
      getComputedStyle(find(".controls")).display !== "none" &&
        find("#search").getClientRects().length > 0,
    );
    enter("#search", "shade");
    click("#search-button");
    check(
      "search after returning exposes matching discovery results",
      !find(".index").classList.contains("hidden") &&
        !find("#article").classList.contains("active") &&
        document.querySelectorAll("[data-article]").length === 1,
    );
    click("[data-article]");
    click("#brand-link");
    check(
      "masthead returns to visible journal",
      !find(".index").classList.contains("hidden") &&
        !find("#article").classList.contains("active") &&
        getComputedStyle(find(".controls")).display !== "none",
    );
  } else if (surface === "dashboard") {
    enter("#date-filter", "today");
    enter("#status-filter", "At risk");
    check(
      "date and status filters keep summary and table coherent",
      find("#jobs-count").textContent === "1" &&
        find("#attention").textContent === "1" &&
        find("#rate").textContent === "0%" &&
        document.querySelectorAll("#records-body [data-id]").length === 1 &&
        find("#records-body [data-id]").dataset.id === "NL-2048",
    );
    check(
      "filtered chart alternative matches record population",
      [...document.querySelectorAll("#chart-data tr")]
        .map((row) => Number(row.cells[1].textContent))
        .join() === "0,0,0,0,1" &&
        find("#chart-desc").textContent.includes("Today 1"),
    );
    click('[data-id="NL-2048"]');
    check(
      "inspect exposes selected record and preserves filters",
      find('[data-id="NL-2048"]').getAttribute("aria-expanded") === "true" &&
        find(".detail").textContent.includes("18 minutes") &&
        find("#date-filter").value === "today" &&
        find("#status-filter").value === "At risk",
    );
    click('[data-id="NL-2048"]');
    check("close collapses record detail", !document.querySelector(".detail"));
    click("#reset-filters");
    check(
      "filter reset restores coherent full summary",
      find("#jobs-count").textContent === "6" &&
        find("#attention").textContent === "3" &&
        find("#rate").textContent === "50%",
    );
    check(
      "reset chart accounts for every displayed job",
      [...document.querySelectorAll("#chart-data tr")]
        .map((row) => Number(row.cells[1].textContent))
        .join() === "1,1,1,0,3",
    );
    enter("#sample-state", "empty");
    check(
      "empty state distinguishes no data from an on-time zero",
      find("#jobs-count").textContent === "0" &&
        find("#rate").textContent === "—" &&
        !find("#filter-empty").hidden,
    );
    enter("#status-filter", "All");
    check(
      "empty sample remains empty when filters change",
      find("#jobs-count").textContent === "0" && !find("#filter-empty").hidden,
    );
    click("#reset-filters");
    check(
      "filter reset preserves empty fixture",
      find("#sample-state").value === "empty" &&
        find("#jobs-count").textContent === "0",
    );
    click("#empty-reset");
    check(
      "empty recovery restores populated fixture",
      find("#sample-state").value === "populated" &&
        find("#jobs-count").textContent === "6",
    );
    enter("#sample-state", "stale");
    check(
      "stale values remain visible with explicit freshness",
      !find("#dashboard-content").hidden &&
        find("#jobs-count").textContent === "6" &&
        find("#freshness").textContent.includes("stale"),
    );
    click("#reset-filters");
    check(
      "filter reset preserves stale state and freshness",
      find("#sample-state").value === "stale" &&
        find("#freshness").textContent.includes("stale") &&
        find("#state-banner").classList.contains("show"),
    );
    enter("#sample-state", "error");
    check(
      "error hides unavailable values and offers recovery",
      find("#dashboard-content").hidden &&
        find("#state-banner").classList.contains("show"),
    );
    click("#recover");
    check(
      "error recovery restores fixture and focus",
      !find("#dashboard-content").hidden &&
        find("#sample-state").value === "populated" &&
        document.activeElement === find("#sample-state"),
    );
  } else if (surface === "documentation") {
    enter("#docs-search", "attempts");
    check(
      "search returns the matching reference",
      document.querySelectorAll("[data-result]").length === 1 &&
        find("[data-result]").dataset.result === "jobs",
    );
    click('[data-result="jobs"]');
    check(
      "search navigation updates article, current page, contents, and focus",
      find(".page.active").dataset.content === "jobs" &&
        find('[data-page="jobs"]').getAttribute("aria-current") === "page" &&
        find("#contents-links a").getAttribute("href") === "#job-create" &&
        document.activeElement === find('[data-content="jobs"] h1'),
    );
    enter("#docs-search", "unfindable-document");
    check(
      "unmatched search exposes empty results",
      document.querySelectorAll("[data-result]").length === 0 &&
        find("#search-results").classList.contains("show"),
    );
    enter("#docs-search", "");
    check(
      "clearing search dismisses results",
      !find("#search-results").classList.contains("show") &&
        find("#docs-search").getAttribute("aria-expanded") === "false",
    );
    click("#mobile-nav");
    check(
      "navigation toggle exposes its expanded state",
      find("#sidebar").classList.contains("open") &&
        find("#mobile-nav").getAttribute("aria-expanded") === "true",
    );
    click('[data-page="quickstart"]');
    check(
      "navigation selection closes menu and activates tutorial",
      !find("#sidebar").classList.contains("open") &&
        find("#mobile-nav").getAttribute("aria-expanded") === "false" &&
        find(".page.active").dataset.content === "quickstart",
    );
    const originalScrollBehavior =
      document.documentElement.style.scrollBehavior;
    try {
      document.documentElement.style.scrollBehavior = "auto";
      click('#contents-links a[href="#define"]');
      // Hash navigation schedules its target after the page has been activated.
      await new Promise((resolve) => requestAnimationFrame(resolve));
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const targetTop = find("#define").getBoundingClientRect().top;
      const headerBottom = find(".topbar").getBoundingClientRect().bottom;
      check(
        "contents navigation keeps heading visible below sticky header",
        targetTop >= headerBottom && targetTop < window.innerHeight,
      );
    } finally {
      document.documentElement.style.scrollBehavior = originalScrollBehavior;
    }
    const clipboardDescriptor = Object.getOwnPropertyDescriptor(
      navigator,
      "clipboard",
    );
    const copied = [];
    try {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: {
          writeText: async (value) => {
            copied.push(value);
          },
        },
      });
      const blocks = [
        ...document.querySelectorAll('[data-content="quickstart"] .code'),
      ];
      for (const block of blocks) {
        block.querySelector(".copy").click();
        await Promise.resolve();
      }
      check(
        "copy sends the exact displayed snippets",
        JSON.stringify(copied) ===
          JSON.stringify(
            blocks.map((block) => block.querySelector("code").textContent),
          ),
      );
      check(
        "successful copy reports completion",
        blocks.every((block) =>
          block.querySelector(".copy-status").textContent.includes("copied"),
        ),
      );
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: {
          writeText: async () => {
            throw new Error("Permission denied for verification");
          },
        },
      });
      blocks[0].querySelector(".copy").click();
      await Promise.resolve();
      check(
        "clipboard rejection offers manual selection fallback",
        blocks[0]
          .querySelector(".copy-status")
          .textContent.includes("Select the code manually"),
      );
    } finally {
      if (clipboardDescriptor)
        Object.defineProperty(navigator, "clipboard", clipboardDescriptor);
      else delete navigator.clipboard;
    }
  } else if (surface === "onboarding") {
    const activeStep = () => find(".step.active").dataset.step;
    click('[data-step="0"] [data-next]');
    check(
      "blank workspace blocks progress and focuses the field",
      activeStep() === "0" &&
        document.activeElement === find("#workspace") &&
        find("#workspace").getAttribute("aria-invalid") === "true",
    );
    enter("#workspace", " Field notes ");
    click('[data-step="0"] [data-next]');
    click('[data-step="1"] [data-next]');
    check(
      "missing purpose blocks progress",
      activeStep() === "1" && find("#purpose-error").textContent.length > 0,
    );
    click('input[name="purpose"]');
    click('[data-step="1"] [data-back]');
    check(
      "back retains entered workspace",
      activeStep() === "0" && find("#workspace").value === " Field notes ",
    );
    click('[data-step="0"] [data-next]');
    check(
      "back retains purpose selection",
      find('input[name="purpose"]').checked,
    );
    click('[data-step="1"] [data-next]');
    enter("#invite", "invalid-email");
    click("#complete");
    check(
      "invalid optional email blocks explicit completion",
      activeStep() === "2" &&
        find("#invite").getAttribute("aria-invalid") === "true",
    );
    click("#skip");
    check(
      "skip bypasses invalid optional input and completes",
      activeStep() === "3" &&
        find("#summary-workspace").textContent === "Field notes" &&
        find("#summary-invite").textContent.includes("Skipped"),
    );
    click("#restart");
    check(
      "restart clears data and invalid state",
      activeStep() === "0" &&
        find("#workspace").value === "" &&
        find("#invite").value === "" &&
        !document.querySelector('input[name="purpose"]:checked') &&
        !document.querySelector('[aria-invalid="true"]'),
    );
  } else {
    throw new Error(`Unsupported example: ${surface}`);
  }

  return { surface, checks, url: location.href };
})();
