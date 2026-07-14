# Decisions

## Architectural incompatibility during PR CI repair

- **Status:** active workflow rule
- **Decision:** When CI evidence points to an architectural incompatibility or
  inconsistency rather than a localized defect, pause before editing, ask the
  user which architectural direction to take, and record the user's decision
  here before continuing.
- **Reason:** A fixer must not silently choose a cross-cutting design change
  while trying to make one PR green.
