# Authentication Standards

_Standards for secure authentication, session management, and password handling_

## Core Authentication Principles

### MUST Follow Rules

- **MUST use secure token storage** - Never store tokens in localStorage for sensitive apps
- **MUST hash passwords** - Use bcrypt with minimum 12 salt rounds
- **MUST implement token expiration** - Maximum 24 hours for access tokens
- **MUST validate all authentication inputs** - Prevent injection attacks
- **MUST use HTTPS** - All authentication endpoints require TLS

### SHOULD Follow Guidelines

- **SHOULD implement refresh tokens** - For better UX with short-lived access tokens
- **SHOULD use secure session configuration** - HttpOnly, Secure, SameSite cookies
- **SHOULD implement rate limiting** - Prevent brute force attacks
- **SHOULD log authentication events** - For security monitoring

## JWT Token Implementation

### Token Structure

```typescript
interface JWTPayload {
  userId: string;
  email: string;
  roles: string[];
  exp: number;
  iat: number;
}

interface RefreshTokenPayload {
  userId: string;
  tokenFamily: string;
  exp: number;
  iat: number;
}
```

### Token Generation

```typescript
class AuthService {
  private readonly JWT_SECRET = process.env.JWT_SECRET!;
  private readonly REFRESH_SECRET = process.env.REFRESH_SECRET!;
  private readonly ACCESS_TOKEN_EXPIRY = "15m";
  private readonly REFRESH_TOKEN_EXPIRY = "7d";

  generateTokens(user: User): AuthTokens {
    const accessToken = this.generateAccessToken(user);
    const refreshToken = this.generateRefreshToken(user);

    return { accessToken, refreshToken };
  }

  private generateAccessToken(user: User): string {
    const payload: JWTPayload = {
      userId: user.id,
      email: user.email,
      roles: user.roles,
      exp: Math.floor(Date.now() / 1000) + 15 * 60, // 15 minutes
      iat: Math.floor(Date.now() / 1000),
    };

    return jwt.sign(payload, this.JWT_SECRET, {
      algorithm: "HS256",
      expiresIn: this.ACCESS_TOKEN_EXPIRY,
    });
  }
}
```

### Token Verification

```typescript
async verifyToken(token: string): Promise<JWTPayload> {
  try {
    const payload = jwt.verify(token, this.JWT_SECRET) as JWTPayload;

    // Additional expiration check
    if (Date.now() >= payload.exp * 1000) {
      throw new AuthenticationError('Token expired');
    }

    // Check if user still exists and is active
    const user = await this.userRepository.findById(payload.userId);
    if (!user || !user.isActive) {
      throw new AuthenticationError('User not found or inactive');
    }

    return payload;
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      throw new AuthenticationError('Invalid token');
    }
    throw error;
  }
}
```

## Password Security

### Password Requirements

```typescript
const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  maxLength: 128,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  preventCommon: true,
  preventUserInfo: true,
};
```

### Password Hashing

```typescript
import bcrypt from "bcrypt";

class PasswordService {
  private readonly SALT_ROUNDS = 12;

  async hashPassword(password: string): Promise<string> {
    this.validatePassword(password);
    return bcrypt.hash(password, this.SALT_ROUNDS);
  }

  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  private validatePassword(password: string): void {
    // Length check
    if (password.length < PASSWORD_REQUIREMENTS.minLength) {
      throw new ValidationError(
        `Password must be at least ${PASSWORD_REQUIREMENTS.minLength} characters`,
      );
    }

    // Complexity check
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!hasUppercase || !hasLowercase || !hasNumbers || !hasSpecialChars) {
      throw new ValidationError(
        "Password must contain uppercase, lowercase, numbers, and special characters",
      );
    }

    // Common password check
    if (this.isCommonPassword(password)) {
      throw new ValidationError("Password is too common");
    }
  }
}
```

## Session Management

### Session Configuration

```typescript
const sessionConfig: SessionOptions = {
  secret: process.env.SESSION_SECRET!,
  name: "sessionId",
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  },
  store: new RedisStore({
    client: redisClient,
    prefix: "session:",
    ttl: 86400, // 24 hours
  }),
};
```

### Session Security

```typescript
class SessionManager {
  async createSession(
    userId: string,
    metadata: SessionMetadata,
  ): Promise<string> {
    const sessionId = crypto.randomBytes(32).toString("hex");
    const sessionData = {
      userId,
      createdAt: Date.now(),
      lastActivity: Date.now(),
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
    };

    await this.sessionStore.set(sessionId, sessionData, "EX", 86400);
    return sessionId;
  }

  async validateSession(sessionId: string): Promise<SessionData | null> {
    const session = await this.sessionStore.get(sessionId);
    if (!session) return null;

    // Check session expiry
    if (Date.now() - session.lastActivity > SESSION_TIMEOUT) {
      await this.sessionStore.del(sessionId);
      return null;
    }

    // Update last activity
    session.lastActivity = Date.now();
    await this.sessionStore.set(sessionId, session, "EX", 86400);

    return session;
  }
}
```

## Multi-Factor Authentication (MFA)

### TOTP Implementation

```typescript
import speakeasy from "speakeasy";

class MFAService {
  generateSecret(user: User): MFASecret {
    const secret = speakeasy.generateSecret({
      length: 32,
      name: `YourApp (${user.email})`,
      issuer: "YourApp",
    });

    return {
      secret: secret.base32,
      qrCode: secret.otpauth_url!,
    };
  }

  verifyToken(secret: string, token: string): boolean {
    return speakeasy.totp.verify({
      secret,
      encoding: "base32",
      token,
      window: 2, // Allow 2 time steps for clock drift
    });
  }
}
```

## Security Headers for Authentication

```typescript
const authSecurityHeaders = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "Cache-Control": "no-store, no-cache, must-revalidate",
  Pragma: "no-cache",
};
```

## Anti-Patterns to Avoid

### ❌ Insecure Token Storage

```typescript
// Bad: Storing sensitive tokens in localStorage
localStorage.setItem("accessToken", token);

// Bad: Storing tokens in cookies without security flags
document.cookie = `token=${token}`;
```

### ❌ Weak Password Hashing

```typescript
// Bad: Using MD5 or SHA for passwords
const hash = crypto.createHash("md5").update(password).digest("hex");

// Bad: Low salt rounds
bcrypt.hash(password, 4); // Too few rounds
```

### ❌ Missing Authentication Checks

```typescript
// Bad: Not verifying token on each request
app.get("/api/user", (req, res) => {
  // Missing authentication check
  res.json(userData);
});
```

## Testing Authentication

```typescript
describe("Authentication", () => {
  it("should hash passwords securely", async () => {
    const password = "SecurePass123!";
    const hash = await passwordService.hashPassword(password);

    expect(hash).not.toBe(password);
    expect(hash.length).toBeGreaterThan(50);
    expect(await passwordService.verifyPassword(password, hash)).toBe(true);
  });

  it("should generate valid JWT tokens", () => {
    const user = { id: "123", email: "test@example.com", roles: ["user"] };
    const token = authService.generateAccessToken(user);

    const decoded = jwt.decode(token) as JWTPayload;
    expect(decoded.userId).toBe(user.id);
    expect(decoded.exp).toBeGreaterThan(Date.now() / 1000);
  });
});
```

## References

- [Password Hashing](../code/security-patterns.md#password-hashing)
- [Session Management](./session-management.md)
- [API Security](./api-design.md#security)
