(() => {
  "use strict";

  const root = document.querySelector("[data-discovery-page]");
  if (!root) return;

  const promptHost = root.querySelector("[data-discovery-prompt-host]");
  const copyPromptButton = root.querySelector("[data-copy-generated-prompt]");
  if (!promptHost || !copyPromptButton) return;

  const pageId = root.dataset.pageId || "temporary-page";
  const storageKey = `essential.discover.v1:${pageId}`;
  const sections = [...root.querySelectorAll("[data-discovery-section]")];
  const questions = [...root.querySelectorAll("[data-discovery-question]")];
  const copyStatus = root.querySelector("[data-copy-status]");
  const clearButton = root.querySelector("[data-clear-discovery-state]");
  const sidebar = document.querySelector(".essential-docnav");
  const promptFold = document.querySelector(".essential-prompt-fold");
  const promptFoldTarget = document.querySelector("[data-prompt-fold-target]");
  const promptSection = document.querySelector("#generated-brief");
  const decisionCount = document.querySelector("[data-decision-count]");
  const noteCount = document.querySelector("[data-note-count]");
  const decisionLabel = document.querySelector("[data-decision-label]");
  const decisionSummaries = document.querySelector("[data-decision-summaries]");
  const noteSummaries = document.querySelector("[data-note-summaries]");

  const emptyState = () => ({
    answers: {},
    touched: {},
    annotations: {},
    dragOrders: {},
    dragTouched: {},
  });

  let state = loadState();
  let activeSectionId = null;
  let programmaticControlUpdate = false;

  // Components that depend on the current answer set register a refresh here;
  // renderPrompt() runs them after every prompt rebuild so their views stay in
  // step with the one canonical prompt (wizard summary, natural-language reply).
  const afterRenderHooks = [];
  // Drag-probe controllers, populated by installDragProbes(); buildPrompt() and
  // clearState() read them to serialize / restore probe order.
  const dragProbes = [];

  function prefersReducedMotion() {
    return (
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function loadState() {
    try {
      const saved = window.localStorage.getItem(storageKey);
      if (!saved) return emptyState();
      const parsed = JSON.parse(saved);
      return {
        answers: parsed.answers || {},
        touched: parsed.touched || {},
        annotations: parsed.annotations || {},
        dragOrders: parsed.dragOrders || {},
        dragTouched: parsed.dragTouched || {},
      };
    } catch (_error) {
      return emptyState();
    }
  }

  function saveState() {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(state));
    } catch (_error) {
      // The page remains fully usable with in-memory state.
    }
  }

  function questionId(question) {
    return question.dataset.questionId || "unidentified-question";
  }

  function questionLabel(question) {
    return (
      question.dataset.questionLabel ||
      question.querySelector("legend, label")?.textContent?.trim() ||
      questionId(question)
    );
  }

  function responseKind(question) {
    return question.dataset.responseKind === "follow-up"
      ? "follow-up"
      : "decision";
  }

  function controlValue(control) {
    if (control instanceof HTMLInputElement && control.type === "checkbox") {
      return control.checked ? control.value : null;
    }
    if (control instanceof HTMLInputElement && control.type === "radio") {
      return control.checked ? control.value : null;
    }
    return control.value.trim();
  }

  function readAnswer(question) {
    const controls = [
      ...question.querySelectorAll(
        "input:not([type='button']), select, textarea",
      ),
    ];
    const checkboxes = controls.filter(
      (control) =>
        control instanceof HTMLInputElement && control.type === "checkbox",
    );
    if (checkboxes.length > 0) {
      return checkboxes.map(controlValue).filter(Boolean);
    }

    const radios = controls.filter(
      (control) =>
        control instanceof HTMLInputElement && control.type === "radio",
    );
    if (radios.length > 0) {
      return radios.map(controlValue).find(Boolean) || "";
    }

    return controls.length > 0 ? controlValue(controls[0]) : "";
  }

  function defaultControlValue(control) {
    if (control instanceof HTMLInputElement) return control.defaultValue;
    if (control instanceof HTMLTextAreaElement) return control.defaultValue;
    if (control instanceof HTMLOptionElement) return control.value;
    if (control instanceof HTMLSelectElement) {
      return [...control.options]
        .filter((option) => option.defaultSelected)
        .map((option) => option.value);
    }
    return control.value;
  }

  function recommendedValues(question) {
    return [...question.querySelectorAll("[data-recommended='true']")]
      .flatMap(defaultControlValue)
      .filter(Boolean);
  }

  function hasValue(answer) {
    return Array.isArray(answer) ? answer.length > 0 : Boolean(answer);
  }

  function formatAnswer(answer) {
    if (Array.isArray(answer))
      return answer.length ? answer.join(", ") : "No selection";
    return answer || "No answer";
  }

  function answerMatchesRecommendation(answer, recommendations) {
    if (recommendations.length === 0) return false;
    if (Array.isArray(answer)) {
      return (
        answer.length === recommendations.length &&
        answer.every((value) => recommendations.includes(value))
      );
    }
    return recommendations.includes(answer);
  }

  function notifyQuestionControls(question) {
    const controls = [
      ...question.querySelectorAll(
        "input:not([type='button']), select, textarea",
      ),
    ];
    programmaticControlUpdate = true;
    try {
      controls.forEach((control) => {
        control.dispatchEvent(new Event("input", { bubbles: true }));
        control.dispatchEvent(new Event("change", { bubbles: true }));
      });
    } finally {
      programmaticControlUpdate = false;
    }
  }

  function hydrateQuestion(question) {
    const id = questionId(question);
    if (!(id in state.answers)) {
      state.answers[id] = readAnswer(question);
      return;
    }

    const saved = state.answers[id];
    const controls = [
      ...question.querySelectorAll(
        "input:not([type='button']), select, textarea",
      ),
    ];
    controls.forEach((control) => {
      if (control instanceof HTMLInputElement && control.type === "radio") {
        control.checked = control.value === saved;
      } else if (
        control instanceof HTMLInputElement &&
        control.type === "checkbox"
      ) {
        control.checked = Array.isArray(saved) && saved.includes(control.value);
      } else if (!Array.isArray(saved)) {
        control.value = saved;
      }
    });
  }

  function sectionTitle(section) {
    return (
      section.dataset.sectionLabel ||
      section.querySelector("h1, h2, h3")?.textContent?.trim() ||
      section.dataset.sectionId ||
      "Untitled section"
    );
  }

  function makeElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function installSectionAnnotation(section) {
    const id = section.dataset.sectionId;
    if (!id) return;

    const trigger = makeElement("button", "discovery-annotation-trigger");
    trigger.type = "button";
    trigger.dataset.annotationFor = id;
    trigger.addEventListener("click", () => openAnnotationEditor(id));

    const summary = makeElement("div", "discovery-annotation-summary");
    summary.dataset.annotationSummary = id;
    summary.setAttribute("role", "note");

    section.prepend(trigger);
    section.append(summary);
    updateSectionAnnotation(id);
  }

  function updateSectionAnnotation(id) {
    const trigger = document.querySelector(
      `[data-annotation-for="${CSS.escape(id)}"]`,
    );
    const summary = document.querySelector(
      `[data-annotation-summary="${CSS.escape(id)}"]`,
    );
    const annotation = state.annotations[id]?.trim() || "";
    if (!trigger || !summary) return;

    trigger.textContent = annotation ? "Edit note" : "Add note";
    trigger.dataset.hasAnnotation = annotation ? "true" : "false";
    summary.replaceChildren();
    summary.hidden = !annotation;

    if (annotation) {
      summary.append(makeElement("strong", "", "Your annotation"));
      summary.append(document.createTextNode(annotation));
    }
  }

  function buildAnnotationDialog() {
    const dialog = makeElement("dialog", "discovery-annotation-dialog");
    dialog.dataset.annotationDialog = "";

    const form = makeElement("form", "discovery-annotation-form");
    form.method = "dialog";

    const eyebrow = makeElement("p", "discovery-eyebrow", "Section note");
    const title = makeElement("h2", "", "Annotate this section");
    title.dataset.annotationDialogTitle = "";

    const label = makeElement("label", "", "What should the coder know?");
    label.htmlFor = `${pageId}-annotation-text`;
    const textarea = makeElement("textarea");
    textarea.id = label.htmlFor;
    textarea.dataset.annotationInput = "";
    textarea.placeholder =
      "Add a correction, preference, question, or implementation note…";

    const actions = makeElement("div", "discovery-dialog-actions");
    const remove = makeElement(
      "button",
      "discovery-button discovery-button-secondary",
      "Remove note",
    );
    remove.type = "button";
    remove.dataset.removeAnnotation = "";
    const cancel = makeElement(
      "button",
      "discovery-button discovery-button-secondary",
      "Cancel",
    );
    cancel.type = "button";
    cancel.addEventListener("click", () => closeAnnotationDialog());
    const save = makeElement("button", "discovery-button", "Save note");
    save.type = "submit";

    actions.append(remove, cancel, save);
    form.append(eyebrow, title, label, textarea, actions);
    dialog.append(form);
    root.append(dialog);

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!activeSectionId) return;
      const value = textarea.value.trim();
      if (value) state.annotations[activeSectionId] = value;
      else delete state.annotations[activeSectionId];
      saveState();
      updateSectionAnnotation(activeSectionId);
      renderPrompt();
      closeAnnotationDialog();
    });

    remove.addEventListener("click", () => {
      if (!activeSectionId) return;
      delete state.annotations[activeSectionId];
      saveState();
      updateSectionAnnotation(activeSectionId);
      renderPrompt();
      closeAnnotationDialog();
    });

    dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      closeAnnotationDialog();
    });

    return dialog;
  }

  const annotationDialog = buildAnnotationDialog();

  function openAnnotationEditor(id) {
    activeSectionId = id;
    const section = sections.find(
      (candidate) => candidate.dataset.sectionId === id,
    );
    const title = annotationDialog.querySelector(
      "[data-annotation-dialog-title]",
    );
    const textarea = annotationDialog.querySelector("[data-annotation-input]");
    title.textContent = section
      ? sectionTitle(section)
      : "Annotate this section";
    textarea.value = state.annotations[id] || "";

    if (typeof annotationDialog.showModal === "function")
      annotationDialog.showModal();
    else annotationDialog.setAttribute("open", "");
    textarea.focus();
  }

  function closeAnnotationDialog() {
    if (typeof annotationDialog.close === "function") annotationDialog.close();
    else annotationDialog.removeAttribute("open");
    activeSectionId = null;
  }

  function collapseText(value) {
    return String(value ?? "")
      .replace(/\s+/g, " ")
      .trim();
  }

  // Read the surrounding claim while dropping the provenance pill's own label,
  // so the prompt records the claim text, not the status word twice.
  function readableClaimText(container) {
    if (!container) return "";
    const clone = container.cloneNode(true);
    clone
      .querySelectorAll(".discovery-provenance[data-provenance]")
      .forEach((pill) => pill.remove());
    return collapseText(clone.textContent);
  }

  function collectProvenanceClaims() {
    const claims = [];
    root
      .querySelectorAll(".discovery-provenance[data-provenance]")
      .forEach((pill) => {
        const status = collapseText(pill.dataset.provenance);
        if (!status) return;
        const container =
          pill.closest("tr") ||
          pill.closest("li, p, dd, dt, td, th, figure, blockquote, div") ||
          pill.parentElement ||
          pill;
        claims.push({ status, claim: readableClaimText(container) });
      });
    root.querySelectorAll("tr[data-provenance]").forEach((row) => {
      // A row that carries a pill is already collected via that pill above.
      if (row.querySelector(".discovery-provenance[data-provenance]")) return;
      const status = collapseText(row.dataset.provenance);
      if (!status) return;
      claims.push({ status, claim: readableClaimText(row) });
    });
    return claims;
  }

  function formatTradeoffGroupKey(key) {
    const cleaned = collapseText((key || "").replace(/[-_]+/g, " "));
    if (!cleaned) return "Trade-off";
    return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
  }

  function collectTradeOffs() {
    const block = root.querySelector(
      ".discovery-tradeoffs[data-tradeoffs-honestly]",
    );
    if (!block) return null;
    const groupLines = [];
    block.querySelectorAll("[data-tradeoff-group]").forEach((group) => {
      const label =
        collapseText(
          group.querySelector("h2, h3, h4, h5, h6")?.textContent || "",
        ) || formatTradeoffGroupKey(group.dataset.tradeoffGroup);
      const items = [...group.querySelectorAll("li")]
        .map((item) => collapseText(item.textContent))
        .filter(Boolean);
      if (items.length) groupLines.push(`- **${label}:** ${items.join("; ")}`);
    });
    return {
      lines: groupLines,
      hasFabricated: Boolean(root.querySelector("[data-fabricated]")),
    };
  }

  function buildPrompt() {
    const goal = root.dataset.discoveryGoal || "Review this discovery result";
    const action = root.dataset.discoveryAction || "discovery review";
    const hasDecisionQuestions = questions.some(
      (question) => responseKind(question) === "decision",
    );
    const hasFollowUpQuestions = questions.some(
      (question) => responseKind(question) === "follow-up",
    );
    const confirmed = [];
    const followUps = [];
    const unresolved = [];

    questions.forEach((question) => {
      const id = questionId(question);
      const label = questionLabel(question);
      const answer = state.answers[id] ?? readAnswer(question);
      const recommendations = recommendedValues(question);
      const touched = Boolean(state.touched[id]);
      const kind = responseKind(question);

      if (touched && (hasValue(answer) || kind === "decision")) {
        if (kind === "follow-up") {
          followUps.push(`- **${label}:** ${formatAnswer(answer)}`);
          return;
        }
        const disposition = answerMatchesRecommendation(answer, recommendations)
          ? "confirmed recommendation"
          : recommendations.length > 0
            ? "user override"
            : "user response";
        confirmed.push(
          `- **${label}:** ${formatAnswer(answer)} _(${disposition})_`,
        );
      } else if (recommendations.length > 0) {
        unresolved.push(
          kind === "follow-up"
            ? `- **${label}:** optional follow-up ${recommendations.join(", ")}; not yet requested`
            : `- **${label}:** suggested ${recommendations.join(", ")}; not yet confirmed`,
        );
      } else if (kind === "decision") {
        unresolved.push(`- **${label}:** unanswered`);
      }
    });

    const annotations = [];
    sections.forEach((section) => {
      const id = section.dataset.sectionId;
      const value = state.annotations[id]?.trim();
      if (value) annotations.push(`- **${sectionTitle(section)}:** ${value}`);
    });

    const lines = [
      "# Feedback for the LLM coder",
      "",
      "## Goal",
      goal,
      "",
      "## Review context",
      `This feedback was collected from the **${action}** discovery page. Treat explicit user responses and annotations as authoritative. Do not treat an untouched suggestion or optional follow-up as approval or a request.`,
    ];

    const boardId = collapseText(root.dataset.boardId || "");
    if (boardId) lines.push("", `Board: ${boardId}`);

    const provenanceClaims = collectProvenanceClaims();
    if (provenanceClaims.length) {
      lines.push("", "## Provenance of claims");
      provenanceClaims.forEach(({ status, claim }) => {
        lines.push(
          claim
            ? `- ${claim} _(provenance: ${status})_`
            : `- _(provenance: ${status})_`,
        );
      });
    }

    const tradeOffs = collectTradeOffs();
    if (tradeOffs && (tradeOffs.lines.length || tradeOffs.hasFabricated)) {
      lines.push("", "## Trade-offs surfaced");
      if (tradeOffs.lines.length) lines.push(...tradeOffs.lines);
      if (tradeOffs.hasFabricated) {
        lines.push(
          '- Note: some illustrative data on this page is invented (marked "invented"); treat it as filler, not real data.',
        );
      }
    }

    if (hasDecisionQuestions) {
      lines.push("", "## Confirmed decisions");
      lines.push(
        ...(confirmed.length
          ? confirmed
          : ["- No decision has been explicitly confirmed yet."]),
      );
    }
    if (hasFollowUpQuestions) {
      lines.push("", "## Requested follow-up actions");
      lines.push(
        ...(followUps.length
          ? followUps
          : ["- No follow-up action has been requested yet."]),
      );
    }
    lines.push("", "## Section annotations");
    lines.push(
      ...(annotations.length ? annotations : ["- No section annotations yet."]),
    );

    const dragResults = collectDragResults();
    if (dragResults.length) {
      lines.push("", "## Interaction results");
      dragResults.forEach(({ label, order }) => {
        lines.push(`- **${label}:** ${order.join(" → ")}`);
      });
    }

    lines.push("", "## Still unresolved");
    lines.push(
      ...(unresolved.length ? unresolved : ["- No unresolved page questions."]),
    );
    lines.push(
      "",
      "## Requested next action",
      hasDecisionQuestions && hasFollowUpQuestions
        ? "Update the implementation or plan using confirmed decisions and every annotation above, then answer each requested follow-up. Preserve unresolved items as questions; do not silently choose suggested defaults or optional follow-ups."
        : hasFollowUpQuestions
          ? "Answer each requested follow-up using the page context and annotations above. Do not treat untouched optional follow-ups as requests."
          : hasDecisionQuestions
            ? "Update the implementation or plan using the confirmed decisions and every annotation above. Preserve unresolved items as questions; do not silently choose their suggested defaults. Report what changed and what still needs a user decision."
            : "Use the page context and every annotation above as review guidance. Preserve the absence of decision questions; do not invent confirmed decisions or implementation orders.",
    );
    return lines.join("\n");
  }

  function renderPrompt() {
    promptHost.value = buildPrompt();
    updatePresentationSummary();
    afterRenderHooks.forEach((hook) => hook());
  }

  // Read a drag-probe's human label the same way questionLabel reads a
  // fieldset's: prefer the data-probe-label attribute, then a descendant
  // [data-probe-label] element, then the probe id.
  function probeLabel(probe) {
    return (
      collapseText(probe.dataset.probeLabel) ||
      collapseText(probe.querySelector("[data-probe-label]")?.textContent) ||
      probeId(probe)
    );
  }

  function probeId(probe) {
    return probe.dataset.dragProbe || probe.dataset.probeLabel || "drag-probe";
  }

  function dragItemLabel(item) {
    return (
      collapseText(item.dataset.dragLabel) ||
      collapseText(item.textContent) ||
      item.dataset.dragItem ||
      "item"
    );
  }

  // A probe contributes an Interaction-results entry only once its order has
  // been changed from the authored default (dragTouched). The final order is
  // read live from the DOM, which hydration has already reconciled with the
  // persisted order, so this stays correct after a reload.
  function collectDragResults() {
    return dragProbes.flatMap(({ probe }) => {
      const id = probeId(probe);
      if (!state.dragTouched[id]) return [];
      const order = [...probe.querySelectorAll("[data-drag-item]")].map(
        dragItemLabel,
      );
      if (!order.length) return [];
      return [{ label: probeLabel(probe), order }];
    });
  }

  function presentationResponses() {
    return questions.flatMap((question) => {
      const id = questionId(question);
      const label = questionLabel(question);
      const answer = state.answers[id] ?? readAnswer(question);
      const recommendations = recommendedValues(question);
      const touched = Boolean(state.touched[id]);
      const kind = responseKind(question);

      if (touched && (hasValue(answer) || kind === "decision")) {
        const stateName = kind === "follow-up" ? "requested" : "confirmed";
        return [
          {
            content: `${label}: ${formatAnswer(answer)}`,
            full: `${stateName} · ${label}: ${formatAnswer(answer)}`,
            state: stateName,
            kind,
          },
        ];
      }
      if (recommendations.length > 0) {
        return [
          {
            content: `${label}: ${recommendations.join(", ")}`,
            full: `${kind === "follow-up" ? "optional" : "suggested"} · ${label}: ${recommendations.join(", ")}`,
            state: kind === "follow-up" ? "optional" : "suggested",
            kind,
          },
        ];
      }
      return [];
    });
  }

  function presentationNotes() {
    return sections.flatMap((section) => {
      const value = state.annotations[section.dataset.sectionId]?.trim();
      return value
        ? [
            {
              content: `${sectionTitle(section)}: ${value}`,
              full: `${sectionTitle(section)}: ${value}`,
              state: "noted",
            },
          ]
        : [];
    });
  }

  function renderPresentationItems(container, items) {
    if (!container) return;
    const fragment = document.createDocumentFragment();
    items.forEach(({ content, full, state: stateName }) => {
      const item = makeElement("li", "", content);
      item.title = full;
      item.dataset.summaryState = stateName;
      fragment.append(item);
    });
    container.replaceChildren(fragment);
  }

  let promptFrame = 0;

  function resizePromptHost() {
    if (!promptHost.offsetParent) return;
    promptHost.style.height = "auto";
    promptHost.style.height = `${promptHost.scrollHeight}px`;
  }

  function schedulePromptResize() {
    if (promptFrame) cancelAnimationFrame(promptFrame);
    promptFrame = requestAnimationFrame(() => {
      promptFrame = 0;
      resizePromptHost();
    });
  }

  function updatePresentationSummary() {
    const responses = presentationResponses();
    const notes = presentationNotes();
    const kinds = new Set(questions.map(responseKind));
    if (decisionLabel) {
      decisionLabel.textContent =
        kinds.size === 1 && kinds.has("follow-up")
          ? "Follow-up actions"
          : kinds.has("follow-up")
            ? "Decisions & actions"
            : "Decisions";
    }
    if (decisionCount) decisionCount.textContent = String(responses.length);
    if (noteCount) noteCount.textContent = String(notes.length);
    renderPresentationItems(decisionSummaries, responses);
    renderPresentationItems(noteSummaries, notes);
    schedulePromptResize();
  }

  function installPresentationShell() {
    if (promptFoldTarget && promptSection)
      promptFoldTarget.append(promptSection);

    const links = [
      ...document.querySelectorAll(".essential-docnav a[href^='#']"),
    ];
    const sectionLinks = links
      .map((link) => ({ link, section: document.querySelector(link.hash) }))
      .filter(({ section }) => section && section.id !== "generated-brief");

    const setActive = (activeLink) => {
      links.forEach((link) => {
        const active = link === activeLink;
        link.classList.toggle("is-active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    };

    let navigationTarget = null;
    let navigationTimer = 0;

    const updateActiveSection = () => {
      if (navigationTarget) {
        setActive(navigationTarget);
        return;
      }
      const readingLine = Math.min(
        220,
        Math.max(110, window.innerHeight * 0.26),
      );
      let current = sectionLinks[0];
      sectionLinks.forEach((candidate) => {
        if (candidate.section.getBoundingClientRect().top <= readingLine) {
          current = candidate;
        }
      });
      if (current) setActive(current.link);
    };

    let scrollFrame = 0;
    const scheduleSectionUpdate = () => {
      if (scrollFrame) return;
      scrollFrame = requestAnimationFrame(() => {
        scrollFrame = 0;
        updateActiveSection();
      });
    };

    links.forEach((link) =>
      link.addEventListener("click", () => {
        navigationTarget = link;
        setActive(link);
        window.clearTimeout(navigationTimer);
        navigationTimer = window.setTimeout(() => {
          navigationTarget = null;
          updateActiveSection();
        }, 1200);
      }),
    );
    window.addEventListener("scroll", scheduleSectionUpdate, { passive: true });
    window.addEventListener("resize", scheduleSectionUpdate);
    updateActiveSection();

    const promptLink = document.querySelector(
      '.essential-docbar a[href="#generated-brief"]',
    );
    promptLink?.addEventListener("click", (event) => {
      event.preventDefault();
      if (promptFold) promptFold.open = true;
      requestAnimationFrame(() => {
        if (window.matchMedia("(max-width: 82rem)").matches) {
          promptFold?.scrollIntoView({ block: "start", behavior: "smooth" });
        } else if (sidebar && promptFold) {
          sidebar.scrollTo({
            top: promptFold.offsetTop - 24,
            behavior: "smooth",
          });
        }
        schedulePromptResize();
      });
    });

    promptFold?.addEventListener("toggle", () => {
      sidebar?.classList.toggle("has-open-prompt", promptFold.open);
      schedulePromptResize();
    });
    window.addEventListener("load", schedulePromptResize);
  }

  function updateQuestion(question) {
    const id = questionId(question);
    state.answers[id] = readAnswer(question);
    if (!programmaticControlUpdate) state.touched[id] = true;
    saveState();
    renderPrompt();
  }

  async function copyPrompt() {
    const prompt = promptHost.value;
    let copied = false;

    try {
      await navigator.clipboard.writeText(prompt);
      copied = true;
    } catch (_error) {
      promptHost.focus();
      promptHost.select();
      copied = document.execCommand("copy");
      promptHost.setSelectionRange(0, 0);
    }

    if (copyStatus) {
      copyStatus.textContent = copied
        ? "Prompt copied. Paste it into your LLM coder."
        : "Copy was blocked. Select the prompt and copy it manually.";
      window.setTimeout(() => {
        copyStatus.textContent = "";
      }, 4000);
    }
  }

  function clearState() {
    const confirmed = window.confirm(
      "Clear every answer and section annotation saved for this temporary page?",
    );
    if (!confirmed) return;

    try {
      window.localStorage.removeItem(storageKey);
    } catch (_error) {
      // In-memory clearing still succeeds.
    }
    state = emptyState();
    questions.forEach((question) => {
      const controls = [
        ...question.querySelectorAll(
          "input:not([type='button']), select, textarea",
        ),
      ];
      controls.forEach((control) => {
        if (control instanceof HTMLInputElement) {
          if (control.type === "radio" || control.type === "checkbox") {
            control.checked = control.defaultChecked;
          } else {
            control.value = control.defaultValue;
          }
        } else if (control instanceof HTMLTextAreaElement) {
          control.value = control.defaultValue;
        } else if (control instanceof HTMLSelectElement) {
          const defaultIndex = [...control.options].findIndex(
            (option) => option.defaultSelected,
          );
          control.selectedIndex = defaultIndex >= 0 ? defaultIndex : 0;
        }
      });
      state.answers[questionId(question)] = readAnswer(question);
      notifyQuestionControls(question);
    });
    sections.forEach((section) =>
      updateSectionAnnotation(section.dataset.sectionId),
    );
    // State was reset above; restore each probe's authored DOM order to match.
    dragProbes.forEach((controller) => controller.restore());
    renderPrompt();
  }

  // AUTHOR-TIME provenance pills are static; give each an accessible name so a
  // screen reader announces the status without disturbing the visible label.
  function announceProvenance() {
    const srOnlyStyle =
      "position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap;border:0;";
    root
      .querySelectorAll(".discovery-provenance[data-provenance]")
      .forEach((pill) => {
        if (pill.hasAttribute("aria-label")) return;
        if (pill.querySelector("[data-provenance-sr]")) return;
        const status = collapseText(pill.dataset.provenance);
        if (!status) return;
        const prefix = makeElement("span", "", "provenance: ");
        prefix.dataset.provenanceSr = "";
        prefix.style.cssText = srOnlyStyle;
        pill.prepend(prefix);
      });
    // Pure row-level pills have no inner element to host the prefix text, so
    // name the row itself instead.
    root.querySelectorAll("tr[data-provenance]").forEach((row) => {
      if (row.hasAttribute("aria-label")) return;
      if (row.querySelector(".discovery-provenance[data-provenance]")) return;
      const status = collapseText(row.dataset.provenance);
      if (!status) return;
      row.setAttribute("aria-label", `provenance: ${status}`);
    });
  }

  // AUTHOR annotation pins are distinct from the user "Add note" dialog. Focus or
  // hover on a pin highlights its paired note and vice versa. Highlight is a
  // static class toggle (no JS motion), so it is reduced-motion-safe by
  // construction; any transition on `.is-active` is the stylesheet's to gate.
  // Generic synchronized-highlight group: the annotation-pin idiom lifted into a
  // reusable primitive. Members carry a key; hover or focus on any member
  // toggles `.is-active` on every member sharing that key. Engage/disengage is
  // reference-counted so overlapping hover + focus on one group never drops the
  // highlight early. Highlight is a static class toggle (no JS motion), so the
  // group is reduced-motion-safe by construction; any transition on `.is-active`
  // is the stylesheet's to gate. `focusable` gives non-interactive members
  // (list items, spans) a tabindex so keyboard focus wiring is bidirectional.
  function installSyncGroup(members, options = {}) {
    const groups = new Map();
    members.forEach(({ element, key }) => {
      if (!key) return;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(element);
    });
    if (groups.size === 0) return;

    const activeCounts = new Map();
    const setGroupActive = (key, active) => {
      (groups.get(key) || []).forEach((member) =>
        member.classList.toggle("is-active", active),
      );
    };
    const engage = (key) => {
      const next = (activeCounts.get(key) || 0) + 1;
      activeCounts.set(key, next);
      if (next === 1) setGroupActive(key, true);
    };
    const disengage = (key) => {
      const next = Math.max(0, (activeCounts.get(key) || 0) - 1);
      activeCounts.set(key, next);
      if (next === 0) setGroupActive(key, false);
    };

    members.forEach(({ element, key }) => {
      if (!key) return;
      if (
        options.focusable &&
        !element.hasAttribute("tabindex") &&
        element.tabIndex < 0
      ) {
        element.tabIndex = 0;
      }
      element.addEventListener("mouseenter", () => engage(key));
      element.addEventListener("mouseleave", () => disengage(key));
      element.addEventListener("focus", () => engage(key));
      element.addEventListener("blur", () => disengage(key));
    });
  }

  // AUTHOR annotation pins are distinct from the user "Add note" dialog. Focus or
  // hover on a pin highlights its paired note and vice versa — the generalized
  // sync-group idiom, with pins (native <button>) and notes (<li>) as the two
  // keyed member families.
  function installAnnotationPins() {
    installSyncGroup(
      [
        ...[
          ...root.querySelectorAll(".discovery-pin[data-annotation-pin]"),
        ].map((pin) => ({ element: pin, key: pin.dataset.annotationPin })),
        ...[...root.querySelectorAll(".discovery-pin-note[data-pin-note]")].map(
          (note) => ({ element: note, key: note.dataset.pinNote }),
        ),
      ],
      { focusable: true },
    );
  }

  // Code / term synchronized pairs — matched-region highlighting across
  // side-by-side code panels ([data-code-pair]), inline term <-> glossary entry
  // ([data-term] <-> [data-term-def]), and specimen region <-> source snippet
  // ([data-code-map] <-> [data-code-map-target]). All three are the same
  // sync-group primitive keyed on the shared id.
  function installSyncPairs() {
    installSyncGroup(
      [...root.querySelectorAll("[data-code-pair]")].map((el) => ({
        element: el,
        key: el.dataset.codePair,
      })),
      { focusable: true },
    );
    installSyncGroup(
      [
        ...[...root.querySelectorAll("[data-term]")].map((el) => ({
          element: el,
          key: el.dataset.term,
        })),
        ...[...root.querySelectorAll("[data-term-def]")].map((el) => ({
          element: el,
          key: el.dataset.termDef,
        })),
      ],
      { focusable: true },
    );
    installSyncGroup(
      [
        ...[...root.querySelectorAll("[data-code-map]")].map((el) => ({
          element: el,
          key: el.dataset.codeMap,
        })),
        ...[...root.querySelectorAll("[data-code-map-target]")].map((el) => ({
          element: el,
          key: el.dataset.codeMapTarget,
        })),
      ],
      { focusable: true },
    );
  }

  // Tabbed multi-representation code panels. The runtime owns aria-selected,
  // panel `hidden`, and a roving tabindex; arrow / Home / End move between tabs.
  function installCodeTabs() {
    root.querySelectorAll("[data-code-tabs]").forEach((container) => {
      const tabs = [...container.querySelectorAll("[data-code-tab]")];
      const panels = [...container.querySelectorAll("[data-code-panel]")];
      if (tabs.length === 0 || panels.length === 0) return;

      const select = (id, focus) => {
        tabs.forEach((tab) => {
          const active = tab.dataset.codeTab === id;
          tab.setAttribute("aria-selected", active ? "true" : "false");
          tab.tabIndex = active ? 0 : -1;
          if (active && focus) tab.focus();
        });
        panels.forEach((panel) => {
          panel.hidden = panel.dataset.codePanel !== id;
        });
      };

      tabs.forEach((tab, index) => {
        tab.addEventListener("click", () => select(tab.dataset.codeTab));
        tab.addEventListener("keydown", (event) => {
          const keys = ["ArrowRight", "ArrowLeft", "Home", "End"];
          if (!keys.includes(event.key)) return;
          event.preventDefault();
          let next = index;
          if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
          else if (event.key === "ArrowLeft")
            next = (index - 1 + tabs.length) % tabs.length;
          else if (event.key === "Home") next = 0;
          else if (event.key === "End") next = tabs.length - 1;
          select(tabs[next].dataset.codeTab, true);
        });
      });

      const initial =
        tabs.find((tab) => tab.getAttribute("aria-selected") === "true") ||
        tabs[0];
      select(initial.dataset.codeTab);
    });
  }

  // Clickable diagram nodes populate a sticky detail host from hidden
  // <template data-diagram-detail="<id>"> blocks (cloned, never innerHTML). The
  // host is an aria-live polite region; the selected node carries `.is-active`.
  function installDiagramDetail() {
    const host = root.querySelector("[data-diagram-detail-host]");
    const nodes = [...root.querySelectorAll("[data-diagram-node]")];
    if (!host || nodes.length === 0) return;

    const templates = new Map(
      [...root.querySelectorAll("template[data-diagram-detail]")].map(
        (template) => [template.dataset.diagramDetail, template],
      ),
    );
    host.setAttribute("aria-live", "polite");

    const activate = (node) => {
      nodes.forEach((candidate) =>
        candidate.classList.toggle("is-active", candidate === node),
      );
      const template = templates.get(node.dataset.diagramNode);
      host.replaceChildren();
      if (template && "content" in template) {
        host.append(template.content.cloneNode(true));
      }
    };

    nodes.forEach((node) => {
      // Diagram nodes are often SVG shapes with no native focusability.
      if (!node.hasAttribute("tabindex")) node.setAttribute("tabindex", "0");
      node.addEventListener("click", () => activate(node));
      node.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        activate(node);
      });
    });
  }

  // Exclusive accordions: opening one <details> closes its siblings within the
  // same [data-accordion-exclusive] group (nested groups stay independent).
  function installExclusiveAccordions() {
    root.querySelectorAll("[data-accordion-exclusive]").forEach((group) => {
      const items = [...group.querySelectorAll("details")].filter(
        (details) => details.closest("[data-accordion-exclusive]") === group,
      );
      items.forEach((details) => {
        details.addEventListener("toggle", () => {
          if (!details.open) return;
          items.forEach((other) => {
            if (other !== details) other.open = false;
          });
        });
      });
    });
  }

  // Anchor navigation flashes the destination section with a transient
  // `.discovery-anchor-flash`. Skipped entirely under reduced motion.
  function installAnchorFlash() {
    const flash = (target) => {
      if (!target || prefersReducedMotion()) return;
      target.classList.remove("discovery-anchor-flash");
      // Force reflow so re-adding the class restarts the animation.
      void target.offsetWidth;
      target.classList.add("discovery-anchor-flash");
      const clear = () => target.classList.remove("discovery-anchor-flash");
      target.addEventListener("animationend", clear, { once: true });
      window.setTimeout(clear, 1600);
    };

    document
      .querySelectorAll(
        ".essential-docnav a[href^='#'], .essential-toc a[href^='#']",
      )
      .forEach((link) => {
        link.addEventListener("click", () => {
          const id = decodeURIComponent(
            (link.getAttribute("href") || "").slice(1),
          );
          if (!id) return;
          const target = document.getElementById(id);
          requestAnimationFrame(() => flash(target));
        });
      });

    window.addEventListener("hashchange", () => {
      const id = decodeURIComponent(window.location.hash.slice(1));
      if (id) flash(document.getElementById(id));
    });
  }

  // Filter chips over an item list. Each chip carries a `data-filter` value and
  // a live `[data-filter-count]`; each item is `[data-filter-item="<tags>"]`
  // (space-separated). Selecting a chip DIMS non-matching items (`.is-dimmed`) —
  // it never hides them — so the full set stays visible and the counts stay
  // truthful. A chip value of "all" (or empty) matches every item.
  function installFilterChips() {
    root.querySelectorAll("[data-filter-chips]").forEach((bar) => {
      const chips = [...bar.querySelectorAll("[data-filter]")];
      const scope =
        bar.closest("[data-discovery-section]") || bar.parentElement || root;
      const items = [...scope.querySelectorAll("[data-filter-item]")];
      if (chips.length === 0 || items.length === 0) return;

      const tagsOf = (item) =>
        (item.dataset.filterItem || "").split(/\s+/).filter(Boolean);
      const matches = (value, item) =>
        !value || value === "all" || tagsOf(item).includes(value);

      // Live counts are a property of the data, not the current selection.
      chips.forEach((chip) => {
        const value = chip.dataset.filter;
        const countHost = chip.querySelector("[data-filter-count]");
        if (countHost) {
          countHost.textContent = String(
            items.filter((item) => matches(value, item)).length,
          );
        }
      });

      const apply = (value) => {
        chips.forEach((chip) => {
          const active = chip.dataset.filter === value;
          chip.classList.toggle("is-active", active);
          if (chip.matches("button, [role='tab'], [aria-pressed]")) {
            chip.setAttribute("aria-pressed", active ? "true" : "false");
          }
        });
        items.forEach((item) => {
          item.classList.toggle("is-dimmed", !matches(value, item));
        });
      };

      chips.forEach((chip) => {
        chip.addEventListener("click", () => apply(chip.dataset.filter));
      });

      const initial =
        chips.find((chip) => chip.classList.contains("is-active")) || chips[0];
      apply(initial.dataset.filter);
    });
  }

  // Spectrum mini-map: numbered dots along the idea axis. Clicking a dot
  // smooth-scrolls to its idea card; each dot mirrors the card's reaction state
  // (a checked input adds `.is-active`, and a checked input's reaction kind adds
  // `.is-<kind>`), listening to the card's own question inputs for two-way sync.
  function installSpectrumMinimap() {
    const dots = [...root.querySelectorAll("[data-minimap-dot]")];
    if (dots.length === 0) return;

    const cardById = new Map(
      [...root.querySelectorAll("[data-idea-card][data-idea-id]")].map(
        (card) => [card.dataset.ideaId, card],
      ),
    );
    const reactionKinds = ["keep", "steal", "skip", "reject"];

    const syncDot = (dot, card) => {
      const checked = [...card.querySelectorAll("input")].filter(
        (input) => input.checked,
      );
      dot.classList.toggle("is-active", checked.length > 0);
      const kind =
        checked.map((input) => input.dataset.reactionKind).find(Boolean) || "";
      reactionKinds.forEach((name) =>
        dot.classList.toggle(`is-${name}`, kind === name),
      );
    };

    dots.forEach((dot) => {
      const card = cardById.get(dot.dataset.minimapDot);
      dot.addEventListener("click", () => {
        if (!card) return;
        card.scrollIntoView({
          block: "center",
          behavior: prefersReducedMotion() ? "auto" : "smooth",
        });
      });
      if (!card) return;
      syncDot(dot, card);
      card.querySelectorAll("input").forEach((input) => {
        input.addEventListener("change", () => syncDot(dot, card));
      });
    });
  }

  // Wizard: focused one-step-at-a-time presentation over the existing stepper.
  // Progressive enhancement only — without JS every [data-interview-step] stays
  // visible. The runtime shows one step at a time with prev/next, an
  // all-questions toggle, and a live summary list that jumps back to any step.
  function installWizard() {
    const wizard = root.querySelector("[data-wizard]");
    if (!wizard) return;
    const steps = [...wizard.querySelectorAll("[data-interview-step]")].sort(
      (a, b) =>
        Number(a.dataset.interviewStep) - Number(b.dataset.interviewStep),
    );
    if (steps.length < 2) return;

    const prevButton = wizard.querySelector("[data-wizard-prev]");
    const nextButton = wizard.querySelector("[data-wizard-next]");
    const toggle = wizard.querySelector("[data-wizard-toggle]");
    const summaryHost = wizard.querySelector("[data-wizard-summary]");

    let index = 0;
    let showAll = false;

    const stepLabel = (step, position) =>
      step.dataset.sectionLabel ||
      collapseText(step.querySelector("h1, h2, h3")?.textContent) ||
      `Step ${position + 1}`;

    const goTo = (target) => {
      index = Math.max(0, Math.min(steps.length - 1, target));
      showAll = false;
      renderStep();
      steps[index].scrollIntoView({
        block: "start",
        behavior: prefersReducedMotion() ? "auto" : "smooth",
      });
      const firstControl = steps[index].querySelector(
        "input:not([type='hidden']), select, textarea, button",
      );
      firstControl?.focus?.({ preventScroll: true });
    };

    const renderStep = () => {
      steps.forEach((step, position) => {
        const visible = showAll || position === index;
        // Steps are `.discovery-section` (author `display: grid`), and an
        // author display rule outranks the UA `[hidden]` rule, so pair the
        // attribute with an inline display toggle that reliably wins. Clearing
        // the inline value on show reverts to the stylesheet's grid.
        step.hidden = !visible;
        step.style.display = visible ? "" : "none";
      });
      if (prevButton) prevButton.disabled = showAll || index === 0;
      if (nextButton)
        nextButton.disabled = showAll || index === steps.length - 1;
      if (toggle)
        toggle.setAttribute("aria-pressed", showAll ? "true" : "false");
    };

    const renderSummary = () => {
      if (!summaryHost) return;
      const fragment = document.createDocumentFragment();
      steps.forEach((step, position) => {
        const stepQuestions = questions.filter((question) =>
          step.contains(question),
        );
        const answered = stepQuestions
          .map((question) => {
            const id = questionId(question);
            if (!state.touched[id]) return "";
            const answer = state.answers[id] ?? readAnswer(question);
            return hasValue(answer) ? formatAnswer(answer) : "";
          })
          .filter(Boolean);

        const entry = makeElement("li", "discovery-wizard-summary-item");
        const jump = makeElement("button", "discovery-wizard-summary-jump");
        jump.type = "button";
        jump.append(
          makeElement(
            "span",
            "discovery-wizard-summary-step",
            stepLabel(step, position),
          ),
          makeElement(
            "span",
            "discovery-wizard-summary-answer",
            answered.length ? answered.join(", ") : "Not answered yet",
          ),
        );
        jump.dataset.summaryState = answered.length ? "answered" : "empty";
        jump.addEventListener("click", () => goTo(position));
        entry.append(jump);
        fragment.append(entry);
      });
      summaryHost.replaceChildren(fragment);
    };

    prevButton?.addEventListener("click", () => goTo(index - 1));
    nextButton?.addEventListener("click", () => goTo(index + 1));
    toggle?.addEventListener("click", () => {
      showAll = !showAll;
      renderStep();
    });

    renderStep();
    renderSummary();
    // Summary answers track the live answer set through the render cycle.
    afterRenderHooks.push(renderSummary);
  }

  // Native HTML5 drag-and-drop feel probe. Items ([data-drag-item]) reorder
  // within a probe ([data-drag-probe]); the order persists through the state
  // store and, once changed from the authored default, surfaces in the prompt's
  // `## Interaction results` section. Keyboard reorder (arrow keys on a focused
  // item) keeps the probe operable without a pointer.
  function installDragProbes() {
    root.querySelectorAll("[data-drag-probe]").forEach((probe) => {
      const id = probeId(probe);
      const listOf = () => [...probe.querySelectorAll("[data-drag-item]")];
      const initialOrder = listOf().map((item) => item.dataset.dragItem);

      const applyOrder = (order) => {
        const byId = new Map(
          listOf().map((item) => [item.dataset.dragItem, item]),
        );
        order.forEach((itemId) => {
          const item = byId.get(itemId);
          if (item) item.parentNode.append(item);
        });
      };

      const finalize = () => {
        const order = listOf().map((item) => item.dataset.dragItem);
        state.dragOrders[id] = order;
        state.dragTouched[id] = order.some(
          (itemId, position) => itemId !== initialOrder[position],
        );
        saveState();
        renderPrompt();
      };

      const horizontal =
        probe.dataset.dragAxis === "horizontal" ||
        (() => {
          const list = listOf();
          if (list.length < 2) return false;
          const a = list[0].getBoundingClientRect();
          const b = list[1].getBoundingClientRect();
          return (
            b.left !== a.left &&
            Math.abs(b.top - a.top) < Math.max(a.height, b.height) * 0.5
          );
        })();

      const moveBefore = (item, reference) => {
        if (!reference) item.parentNode.append(item);
        else reference.parentNode.insertBefore(item, reference);
      };

      // Hydrate persisted order before wiring interaction.
      const saved = state.dragOrders[id];
      if (Array.isArray(saved) && saved.length) applyOrder(saved);

      let dragged = null;
      probe.addEventListener("dragstart", (event) => {
        const item = event.target.closest("[data-drag-item]");
        if (!item || !probe.contains(item)) return;
        dragged = item;
        item.classList.add("is-dragging");
        probe.classList.add("is-drag-active");
        if (event.dataTransfer) {
          event.dataTransfer.effectAllowed = "move";
          try {
            event.dataTransfer.setData(
              "text/plain",
              item.dataset.dragItem || "",
            );
          } catch (_error) {
            // Some browsers reject setData outside a user gesture; harmless.
          }
        }
      });
      probe.addEventListener("dragover", (event) => {
        if (!dragged) return;
        const target = event.target.closest("[data-drag-item]");
        if (!target || target === dragged || !probe.contains(target)) return;
        event.preventDefault();
        if (event.dataTransfer) event.dataTransfer.dropEffect = "move";
        const rect = target.getBoundingClientRect();
        const after = horizontal
          ? event.clientX > rect.left + rect.width / 2
          : event.clientY > rect.top + rect.height / 2;
        moveBefore(dragged, after ? target.nextSibling : target);
      });
      probe.addEventListener("drop", (event) => {
        if (!dragged) return;
        event.preventDefault();
      });
      probe.addEventListener("dragend", () => {
        if (!dragged) return;
        dragged.classList.remove("is-dragging");
        probe.classList.remove("is-drag-active");
        dragged = null;
        finalize();
      });

      listOf().forEach((item) => {
        if (!item.hasAttribute("draggable")) item.draggable = true;
        if (!item.hasAttribute("tabindex")) item.tabIndex = 0;
        item.addEventListener("keydown", (event) => {
          const back = horizontal ? "ArrowLeft" : "ArrowUp";
          const forward = horizontal ? "ArrowRight" : "ArrowDown";
          if (event.key !== back && event.key !== forward) return;
          event.preventDefault();
          if (event.key === back && item.previousElementSibling) {
            moveBefore(item, item.previousElementSibling);
          } else if (event.key === forward && item.nextElementSibling) {
            moveBefore(item, item.nextElementSibling.nextSibling);
          } else {
            return;
          }
          item.focus();
          finalize();
        });
      });

      dragProbes.push({
        probe,
        restore: () => applyOrder(initialOrder),
      });
    });
  }

  // Natural-language reply: a one-paragraph conversational preview of the reply,
  // assembled from touched answers, note counts, and changed probes, rendered
  // into [data-nl-reply] with textContent only. It regenerates with the prompt;
  // the canonical copy control still copies the full Markdown prompt.
  function installNlReply() {
    const host = root.querySelector("[data-nl-reply]");
    if (!host) return;

    const joinWithAnd = (parts) => {
      if (parts.length <= 1) return parts.join("");
      return `${parts.slice(0, -1).join(", ")} and ${parts[parts.length - 1]}`;
    };
    const plural = (count, noun) => `${count} ${noun}${count === 1 ? "" : "s"}`;

    const compose = () => {
      const decided = [];
      const requested = [];
      questions.forEach((question) => {
        const id = questionId(question);
        if (!state.touched[id]) return;
        const answer = state.answers[id] ?? readAnswer(question);
        const kind = responseKind(question);
        if (kind !== "decision" && !hasValue(answer)) return;
        (kind === "follow-up" ? requested : decided).push({
          label: questionLabel(question),
          answer: formatAnswer(answer),
        });
      });
      const notes = sections.filter((section) =>
        state.annotations[section.dataset.sectionId]?.trim(),
      ).length;
      const probes = collectDragResults().length;

      const parts = [];
      if (decided.length) {
        const first = decided[0];
        const lead = `settled ${first.label.toLowerCase()} as “${first.answer}”`;
        const more = decided.length - 1;
        parts.push(
          more > 0 ? `${lead}, plus ${plural(more, "more decision")}` : lead,
        );
      }
      if (requested.length)
        parts.push(`asked for ${plural(requested.length, "follow-up")}`);
      if (notes) parts.push(`left ${plural(notes, "section note")}`);
      if (probes)
        parts.push(`re-ordered ${plural(probes, "interaction probe")}`);

      if (parts.length === 0) {
        return "Nothing is locked in yet — answer a question or add a note and this line will summarize your reply to the coder.";
      }
      return `So far I've ${joinWithAnd(parts)}. Copy the prompt to send the coder the full detail.`;
    };

    const render = () => {
      host.textContent = compose();
    };
    render();
    afterRenderHooks.push(render);
  }

  questions.forEach((question) => {
    hydrateQuestion(question);
    notifyQuestionControls(question);
    question.addEventListener("input", () => updateQuestion(question));
    question.addEventListener("change", () => updateQuestion(question));
  });
  sections.forEach(installSectionAnnotation);
  announceProvenance();
  installAnnotationPins();
  installSyncPairs();
  installCodeTabs();
  installDiagramDetail();
  installExclusiveAccordions();
  installAnchorFlash();
  installFilterChips();
  installSpectrumMinimap();
  installDragProbes();
  installWizard();
  installNlReply();
  copyPromptButton.addEventListener("click", copyPrompt);
  clearButton?.addEventListener("click", clearState);
  installPresentationShell();
  renderPrompt();
})();
