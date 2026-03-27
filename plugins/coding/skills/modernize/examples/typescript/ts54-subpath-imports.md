---
since: "TS 5.4"
min-es-target: "any"
module: "nodenext or bundler"
---

## Detection

`from "\.\./\.\./` or `from "\.\./\.\./\.\./` -- deeply nested relative import paths

## Before

```typescript
// src/features/auth/handlers/login.ts
import { hashPassword } from "../../../utils/crypto.js";
import { validateEmail } from "../../../utils/validation.js";
import { UserRepository } from "../../../repositories/user.js";
import { createToken } from "../../../services/auth/token.js";
import type { AppConfig } from "../../../config/types.js";
```

## After

```jsonc
// package.json
{
  "imports": {
    "#utils/*": "./src/utils/*",
    "#repositories/*": "./src/repositories/*",
    "#services/*": "./src/services/*",
    "#config/*": "./src/config/*"
  }
}
```

```typescript
// src/features/auth/handlers/login.ts
import { hashPassword } from "#utils/crypto.js";
import { validateEmail } from "#utils/validation.js";
import { UserRepository } from "#repositories/user.js";
import { createToken } from "#services/auth/token.js";
import type { AppConfig } from "#config/types.js";
```

## Conditions

- Requires `--moduleResolution nodenext` or `bundler` in tsconfig
- The `#` prefix is mandatory per the Node.js subpath imports specification
- Subpath imports are resolved from the closest parent `package.json`
- Works with both ESM and CJS when using `nodenext` resolution
- Can include conditional exports for different environments (e.g., `"node"` vs `"default"`)
- TS 5.4 added full support for wildcard patterns in subpath imports
