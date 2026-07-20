# Architecture template

This compatibility entrypoint indexes the complete bundled architecture template. Load every child in order when the bundled template is selected:

- [Authoring contract, concepts, context, and topology](architecture-template/10-authoring-and-foundations.md)
- [Components, flows, lifecycle, data, journeys, and network topology](architecture-template/20-components-runtime-and-data.md)
- [Patterns, extension points, constraints, roadmap, and split guidance](architecture-template/30-quality-roadmap-and-splitting.md)

The children are one template. Apply only sections supported by repository evidence. Generated architecture uses lowercase `docs/architecture/<architecture-slug>.md`; if split, that original remains the overview and its detail uses lowercase `<nn>-<topic-slug>.md` children.
