---
name: lint
description: Use when React JSX, components, hooks, accessibility, project structure, tests, or Storybook files need mechanical standards enforcement through the shared Coding lint workflow; React owns framework rules while Coding owns generic execution and reporting.
model: opus
allowed-tools: "Skill(coding:lint *)"
argument-hint: "[specifier] [--scope=SCOPE]"
---

# React Linting

Forward the request exactly once through `Skill(coding:lint *)` using `$ARGUMENTS --profile="${CLAUDE_SKILL_DIR}/profile.json"`.

Do not parse, reorder, or discard the caller's specifier or scope. Do not perform independent discovery, scanning, linting, review, aggregation, or framework dispatch. Wait for the delegated skill and return its report unchanged.
