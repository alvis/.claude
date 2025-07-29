# Code Style & Conventions

## Language

- Use American English throughout (aligns with third-party libraries)

## TypeScript

- Use TypeScript with strict typing enabled (`strict: true` in `tsconfig.json`)
  - Avoid using `any` type; prefer strict types (`unknown`, `never`, etc.)
  - Define custom types and interfaces for data models, props, and API responses
  - Use union types and discriminated unions for complex cases
  - Prefer `readonly` for immutable structures and function parameters
- Consistently use ES6+ features, such as arrow functions, destructuring, and template literals
- Avoid using deprecated JavaScript/TypeScript features or patterns
- Prefer modern `#private` over legacy `private` keyword on private fields

## Import Conventions

Follow these guidelines for importing code and types:

- Import actual code before types
- Separate import groups with a blank line
- Keep type imports separate from actual imports
  - ❌ Avoid `import { useState, type FC } from 'react';`
- Prefer named imports
  - Avoid default imports and namespace imports unless necessary
    - ❌ Avoid `import React from 'react';`
    - ❌ Avoid `import * as React from 'react';`
- Follow this import order:
  1. Building modules (prefixed with `node:`)
  2. Libraries
  3. Project modules
     a. Root shortcut prefixed with `#` (subpath imports defined in package.json)
     b. Relative path imports (farthest to closest: `../../*`, `../*`, `./*`)
- Use the same import order for types as for actual code
- **IMPORTANT**: Always use subpath imports when available. If package.json contains `"#*": "./source/*.ts"` in the imports field, use `import { emit } from '#emit';` instead of `import { emit } from '../source/emit.js';`

~ ✅ EXAMPLE ~

```typescript
/* code import */

// built-in modules
import { log } from 'node:console';
import { readFile } from 'node:fs/promises';

// third-party libraries
import { LibComponent } from 'some-library';
import { useState, useEffect } from 'react';
import axios from 'axios';

// project modules
import { FeatureComponent } from '#components/FeatureComponent';
import { useFeature } from '#hooks/useFeature';
import { featureFunction } from '#utils/featureUtils';
import { parentFunction } from '../helpers';
import { SiblingComponent } from './SiblingComponent';

/* type imports */

// built-in modules
import type { Console } from 'node:console';

// third-party libraries
import type { AxiosResponse } from 'axios';
import type { FC, ReactNode } from 'react';

// project modules
import type { FeatureProps } from '#types/feature';
// ...
```

## Naming

- `camelCase` vars/funcs · `PascalCase` types/classes · `UPPER_SNAKE` consts (file-scoped: `camelCase`)
- Prefer full descriptive names (✅ `userId`, `image` · ❌ `userID`, `img`)
- Well-known acronyms acceptable (✅ `id`, `url` · ❌ `identity`, `uniformResourceLocator`)
- Booleans: `is<Adj>` (state) · `has<Noun>` (event/milestone)
- Composite IDs: lower‑kebab with dots (`job.posting-new-job`)
- Data functions: `get<Entity>`, `set<Entity>`, `drop<Entity>`, `list<Entity>`, `search<Entity>`

### Acronyms

> **Always in UPPER cases**
> 
> Acronyms (like HTML, URL, API) are typically kept **fully UPPER case** in camelCase or PascalCase names. This improves clarity and aligns with many style guides, including Google's and TypeScript's.
> 
> - ✅ **getHTMLParser**
> - ❌ **getHtmlParser**

## Object key groups & order

- Use `has<Noun>` for possession/association (e.g., `hasAttachment`)
- Use `has<Something>` for milestones/events (e.g., `hasCompletedOnboarding`)
- Use `is<Adjective>` for current states (e.g., `isActive`, `isVisible`)
- Keep identical logical groups across objects and alphabetise inside each group

```ts
{
  // index //
  id: '…',

  // display //
  email: '…',
  name: '…',

  // auth //
  lastLogin: '…',
  passwordHash: '…',

  // permissions //
  isActive: true,
  roles: ['admin'],
}
```

--- END ---
