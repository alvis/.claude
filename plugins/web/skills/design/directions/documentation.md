# Documentation

Use for documentation homepages, navigation, search, tutorials, conceptual guides, and reference reading surfaces. Authoring technical facts or implementing an API belongs to its owning task; this subskill designs how those facts are found and used.

## Establish the reader's task
Inspect the actual documentation tree, product vocabulary, reader experience, versions, code languages, and common entry points. Separate learning a task from looking up a contract. Ask for missing navigation or version intent; never invent API behavior to make the example appear complete.

## Structure and interaction
- Organize navigation around reader tasks and stable concepts. Separate tutorials, explanations, how-to guides, and reference when those content types exist; do not force empty categories.
- Tutorials state prerequisites, a sequence, expected results, and recovery. Reference emphasizes exact names, parameters, return values, constraints, and examples from authoritative source content.
- Search exposes result title, context, and content type; offer recovery from no results. Preserve search context when opening and returning from a result.
- Show the current page and local section. Use deep links for headings and keep them visible below sticky navigation. Version controls, when needed, explain version scope and preserve a matching page only when it exists.
- Code needs language identification, readable overflow, and keyboard-accessible copy with success/failure feedback. Do not rely on color alone for meaning or silently claim a failed clipboard write succeeded.
- On mobile, navigation opens through a named control with accurate expanded state; selecting a page closes it and moves focus to the new content. Keep search reachable.
- Use restrained visual hierarchy, consistent callouts, and sufficient reading measure. Motion may preserve orientation but must not delay lookup.

## Handoff and acceptance
Return navigation/content-type maps, search and deep-link behavior, reading/code patterns, mobile navigation, and applicable feedback states through the parent contract.

Verify search success and no results, tutorial/reference navigation, active-page indication, keyboard/focus, code copy including an unavailable clipboard, long code overflow, and mobile open/select/close. Code samples in a fictional demonstration must be labeled illustrative; do not present them as a real service integration.

## Source and example
[Diátaxis](https://diataxis.fr/) distinguishes documentation by reader need. This is information-architecture guidance, not an award or a mandate to adopt its terminology verbatim.

Optionally open `examples/documentation/index.html` and `examples/documentation/preview.png` from this skill root for a fictional local documentation flow.

