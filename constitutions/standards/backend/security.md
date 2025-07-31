# Security Standards - Overview

*This file has been reorganized into focused, domain-specific security standards for better maintainability.*

## 📁 Security Standards Have Moved

The comprehensive security standards have been split into specialized files for easier navigation and maintenance:

### Core Security Standards

| Standard | Purpose | Location |
|----------|---------|----------|
| **Authentication** | JWT, passwords, sessions, MFA | [→ security/authentication.md](../security/authentication.md) |
| **Data Protection** | Input validation, encryption, sanitization | [→ security/data-protection.md](../security/data-protection.md) |
| **Infrastructure** | Headers, rate limiting, CORS, DDoS | [→ security/infrastructure.md](../security/infrastructure.md) |
| **Monitoring** | Logging, alerting, incident response | [→ security/monitoring.md](../security/monitoring.md) |
| **Checklist** | Comprehensive security audit guide | [→ security/checklist.md](../security/checklist.md) |

## Quick Navigation

### By Security Domain

- 🔐 **Authentication & Authorization** → [authentication.md](../security/authentication.md)
- 🛡️ **Data Security** → [data-protection.md](../security/data-protection.md)
- 🌐 **Network & Infrastructure** → [infrastructure.md](../security/infrastructure.md)
- 📊 **Monitoring & Incident Response** → [monitoring.md](../security/monitoring.md)
- ✅ **Security Audit** → [checklist.md](../security/checklist.md)

### By Implementation Phase

1. **Foundation** → Start with [Authentication](../security/authentication.md)
2. **Data Layer** → Implement [Data Protection](../security/data-protection.md)
3. **Infrastructure** → Configure [Infrastructure Security](../security/infrastructure.md)
4. **Operations** → Set up [Monitoring](../security/monitoring.md)
5. **Validation** → Use the [Security Checklist](../security/checklist.md)

## Security First Principles (Summary)

### Core Rules (See detailed standards for implementation)
- **NEVER commit secrets** → See [Authentication](../security/authentication.md#secret-management)
- **NEVER trust user input** → See [Data Protection](../security/data-protection.md#input-validation)
- **ALWAYS use HTTPS** → See [Infrastructure](../security/infrastructure.md#tls-configuration)
- **ALWAYS hash passwords** → See [Authentication](../security/authentication.md#password-security)
- **ALWAYS log security events** → See [Monitoring](../security/monitoring.md#security-event-logging)

## Implementation Priority

### Phase 1: Critical Security (Week 1)
- [ ] Implement authentication standards
- [ ] Set up password hashing and JWT
- [ ] Configure security headers
- [ ] Enable HTTPS

### Phase 2: Data Protection (Week 2)
- [ ] Add input validation
- [ ] Implement data encryption
- [ ] Set up SQL injection prevention
- [ ] Configure XSS protection

### Phase 3: Infrastructure (Week 3)
- [ ] Implement rate limiting
- [ ] Configure CORS properly
- [ ] Set up DDoS protection
- [ ] Add security monitoring

### Phase 4: Continuous Security (Ongoing)
- [ ] Regular security audits using checklist
- [ ] Monitor security events
- [ ] Update dependencies
- [ ] Security training

## Migration Notice

If you're looking for specific content from the old monolithic security.md file:

- **Secret Management** → [authentication.md](../security/authentication.md#secret-management)
- **JWT Implementation** → [authentication.md](../security/authentication.md#jwt-token-implementation)
- **Input Validation** → [data-protection.md](../security/data-protection.md#input-validation)
- **SQL Injection Prevention** → [data-protection.md](../security/data-protection.md#sql-injection-prevention)
- **Security Headers** → [infrastructure.md](../security/infrastructure.md#security-headers)
- **Rate Limiting** → [infrastructure.md](../security/infrastructure.md#rate-limiting)
- **Security Logging** → [monitoring.md](../security/monitoring.md#security-event-logging)
- **Audit Checklist** → [checklist.md](../security/checklist.md)

## See Also

- [API Design Standards](./api-design.md) - Secure API patterns
- [Data Operations Standards](./data-operations.md) - Secure data handling
- [Error Handling Standards](./error-handling.md) - Security-aware error handling

---

**Note**: This file now serves as a navigation guide. All detailed security implementations have been moved to the specialized files in the [security/](../security/) directory for better organization and maintainability.