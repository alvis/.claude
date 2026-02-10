# TYP-IMPT-01: Import Category Ordering

## Intent

Import order is strict: built-in (`node:`), third-party, project modules (alias/subpath/relative), then type-only imports, with blank-line separation between categories. Never mix runtime and `type` imports in a single statement.

## Fix

```typescript
import { readFile } from "node:fs/promises";

import { useState } from "react";
import axios from "axios";

import { DatabaseClient } from "#database/client";
import { logger } from "#utilities/logger";

import type { Request, Response } from "express";

import type { User } from "#types/user";
```

### Strict Import Order

**STRICT order** (blank lines separate each category):

1. **Built-in modules** (`node:`)
2. **Third-party libraries**
3. **Project modules** (subpath `#*`, path alias `@*`, or relative `../`)
4. **Type imports** (repeat same order as above)

```typescript
import { readFile } from 'node:fs/promises';

import { useState } from 'react';
import axios from 'axios';

import { FeatureComponent } from '@/components/FeatureComponent';
import { featureFunction } from '#utilities/feature';
import { parentFunction } from '../helpers';

import type { FC } from 'react';

import type { User } from '#types/user';
```

### Import Style Rules

```typescript
// ✅ DO: clean, separated imports
import { useState, useEffect } from 'react';

import type { FC } from 'react';

// ❌ DON'T: mixed imports
import React, { useState, type FC } from 'react';

// ❌ DON'T: namespace imports
import * as React from 'react';

// ❌ DON'T: default imports when named available
import React from 'react';
```

### Subpath Import Rules

Check `package.json` for subpath mappings under `exports` or `imports`:

**RULE 1: Use shortest subpath** for cross-module imports:

```typescript
// ✅ DO: use subpaths for cross-module imports
import { handler } from '#request';
import { helper } from '#utilities/validator';

// ❌ DON'T: use relative paths when subpath exists
import { handler } from './fastify/request';
import { helper } from '../utilities/validator';
```

**RULE 2: Use relative** for same-subpath imports:

```typescript
// File: src/fastify/request.ts (part of #fastify/*)

// ✅ DO: relative imports within same subpath
import { formatResponse } from './response';

// ❌ DON'T: subpath imports within same subpath
import { formatResponse } from '#fastify/response';
```

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `import x from "#a"; import fs from "fs"` (wrong order), refactor before adding new behavior.
- Type-only imports repeat the same category order (builtin types, third-party types, project types) within their section.

## Related

TYP-IMPT-02, TYP-IMPT-03, TYP-IMPT-04
