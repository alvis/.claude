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
  });

  let state = loadState();
  let activeSectionId = null;
  let programmaticControlUpdate = false;

  function loadState() {
    try {
      const saved = window.localStorage.getItem(storageKey);
      if (!saved) return emptyState();
      const parsed = JSON.parse(saved);
      return {
        answers: parsed.answers || {},
        touched: parsed.touched || {},
        annotations: parsed.annotations || {},
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

    const trigger = makeElement(
      "button",
      "discovery-annotation-trigger",
    );
    trigger.type = "button";
    trigger.dataset.annotationFor = id;
    trigger.addEventListener("click", () => openAnnotationEditor(id));

    const summary = makeElement(
      "div",
      "discovery-annotation-summary",
    );
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
    const dialog = makeElement(
      "dialog",
      "discovery-annotation-dialog",
    );
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
  function installAnnotationPins() {
    const pins = [...root.querySelectorAll(".discovery-pin[data-annotation-pin]")];
    const notes = [
      ...root.querySelectorAll(".discovery-pin-note[data-pin-note]"),
    ];
    if (pins.length === 0 && notes.length === 0) return;

    const pinsByIndex = new Map();
    const notesByIndex = new Map();
    const register = (map, key, element) => {
      if (!key) return;
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(element);
    };
    pins.forEach((pin) => register(pinsByIndex, pin.dataset.annotationPin, pin));
    notes.forEach((note) => register(notesByIndex, note.dataset.pinNote, note));

    const activeCounts = new Map();
    const setPairActive = (index, active) => {
      [
        ...(pinsByIndex.get(index) || []),
        ...(notesByIndex.get(index) || []),
      ].forEach((member) => member.classList.toggle("is-active", active));
    };
    // Reference-count engage/disengage so overlapping hover + focus on the same
    // pair does not drop the highlight early.
    const engage = (index) => {
      const next = (activeCounts.get(index) || 0) + 1;
      activeCounts.set(index, next);
      if (next === 1) setPairActive(index, true);
    };
    const disengage = (index) => {
      const next = Math.max(0, (activeCounts.get(index) || 0) - 1);
      activeCounts.set(index, next);
      if (next === 0) setPairActive(index, false);
    };
    const wire = (element, index) => {
      if (!index) return;
      element.addEventListener("mouseenter", () => engage(index));
      element.addEventListener("mouseleave", () => disengage(index));
      element.addEventListener("focus", () => engage(index));
      element.addEventListener("blur", () => disengage(index));
    };

    pins.forEach((pin) => {
      // Pins are authored as <button> (natively focusable). Guard the case where
      // a pin is authored as a plain element so keyboard focus wiring still fires;
      // a native button already reports tabIndex 0, so this leaves it untouched.
      if (!pin.hasAttribute("tabindex") && pin.tabIndex < 0) pin.tabIndex = 0;
      wire(pin, pin.dataset.annotationPin);
    });
    notes.forEach((note) => {
      // Notes are <li>; make them focusable so focus wiring is bidirectional.
      if (!note.hasAttribute("tabindex")) note.tabIndex = 0;
      wire(note, note.dataset.pinNote);
    });
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
  copyPromptButton.addEventListener("click", copyPrompt);
  clearButton?.addEventListener("click", clearState);
  installPresentationShell();
  renderPrompt();
})();
