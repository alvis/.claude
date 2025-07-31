# Security Audit Checklist

*Comprehensive security checklist for application security audits and assessments*

## How to Use This Checklist

1. **Regular Audits**: Run through this checklist quarterly
2. **Before Release**: Complete all critical items before production
3. **After Incidents**: Review relevant sections after security events
4. **Continuous**: Some items require ongoing monitoring

### Priority Levels
- 🔴 **Critical**: Must be implemented before production
- 🟡 **Important**: Should be implemented for security maturity
- 🟢 **Recommended**: Enhances security posture

## Authentication & Session Management

### 🔴 Critical Items
- [ ] Passwords hashed with bcrypt (min 12 rounds) or Argon2
- [ ] No plaintext passwords in database or logs
- [ ] Session tokens generated with cryptographic randomness
- [ ] Session invalidation implemented on logout
- [ ] Authentication required for all protected resources

### 🟡 Important Items
- [ ] JWT tokens expire within 24 hours (access) / 7 days (refresh)
- [ ] Refresh tokens rotated on use
- [ ] Account lockout after 5 failed attempts
- [ ] Password complexity requirements enforced
- [ ] Session timeout after inactivity (30 minutes)

### 🟢 Recommended Items
- [ ] Multi-factor authentication (MFA) available
- [ ] Passwordless authentication options
- [ ] Biometric authentication for mobile
- [ ] Risk-based authentication
- [ ] Device fingerprinting

### Verification Steps
```bash
# Check password hashing
grep -r "bcrypt\|argon2\|scrypt" --include="*.ts" --include="*.js"

# Verify JWT expiration
grep -r "expiresIn\|exp" --include="*.ts" --include="*.js"

# Check for hardcoded passwords
grep -r "password\s*=\s*[\"'][^\"']+[\"']" --include="*.ts" --include="*.js"
```

## Authorization & Access Control

### 🔴 Critical Items
- [ ] Authorization checks on every API endpoint
- [ ] Role-based access control (RBAC) implemented
- [ ] Default deny for unauthorized requests
- [ ] Resource ownership verification
- [ ] No authorization logic in client code

### 🟡 Important Items
- [ ] Principle of least privilege enforced
- [ ] API scopes properly defined and validated
- [ ] Admin actions require re-authentication
- [ ] Indirect object reference protection (use UUIDs)
- [ ] Function-level access control

### 🟢 Recommended Items
- [ ] Attribute-based access control (ABAC)
- [ ] Dynamic permission evaluation
- [ ] Delegation mechanisms
- [ ] Time-based access restrictions
- [ ] Geographic access restrictions

### Verification Steps
```typescript
// Example authorization middleware check
describe('Authorization', () => {
  it('should require authentication for protected routes', async () => {
    const response = await request(app)
      .get('/api/users/profile')
      .expect(401);
  });

  it('should enforce role-based access', async () => {
    const userToken = await getUserToken();
    const response = await request(app)
      .get('/api/admin/users')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(403);
  });
});
```

## Input Validation & Sanitization

### 🔴 Critical Items
- [ ] All user inputs validated server-side
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] Command injection prevention
- [ ] Path traversal prevention

### 🟡 Important Items
- [ ] Input length restrictions
- [ ] Data type validation
- [ ] Regular expression validation for formats
- [ ] File upload restrictions (type, size, content)
- [ ] XML external entity (XXE) prevention

### 🟢 Recommended Items
- [ ] Input normalization (Unicode, etc.)
- [ ] Business logic validation
- [ ] Contextual validation based on user role
- [ ] Rate limiting on input processing
- [ ] Input history tracking

### Common Vulnerabilities to Check
```typescript
// SQL Injection - Check for parameterized queries
const query = 'SELECT * FROM users WHERE id = $1'; // ✅ Good
const query = `SELECT * FROM users WHERE id = ${userId}`; // ❌ Bad

// XSS - Check for proper encoding
response.send(`<div>${escapeHtml(userInput)}</div>`); // ✅ Good
response.send(`<div>${userInput}</div>`); // ❌ Bad

// Path Traversal - Check for path validation
const safePath = path.join(baseDir, path.normalize(userPath).replace(/^(\.\.[\/\\])+/, '')); // ✅ Good
const unsafePath = baseDir + userPath; // ❌ Bad
```

## Data Protection & Cryptography

### 🔴 Critical Items
- [ ] TLS 1.2+ enforced for all connections
- [ ] Sensitive data encrypted at rest (AES-256)
- [ ] No custom cryptography implementations
- [ ] Secure random number generation
- [ ] No sensitive data in URLs

### 🟡 Important Items
- [ ] Strong cipher suites only
- [ ] Perfect forward secrecy enabled
- [ ] Encryption keys rotated regularly
- [ ] Key derivation functions used properly
- [ ] Secure key storage (HSM/KMS)

### 🟢 Recommended Items
- [ ] Field-level encryption for PII
- [ ] Encrypted backups
- [ ] Certificate pinning
- [ ] Quantum-resistant algorithms considered
- [ ] Homomorphic encryption for analytics

### Verification Commands
```bash
# Check TLS configuration
nmap --script ssl-enum-ciphers -p 443 example.com

# Verify encryption in code
grep -r "createCipher\|crypto\|encrypt" --include="*.ts"

# Check for hardcoded keys
grep -r "key\s*=\s*[\"'][0-9a-fA-F]+[\"']" --include="*.ts"
```

## API & Web Security

### 🔴 Critical Items
- [ ] CORS configured with specific origins
- [ ] CSRF protection for state-changing requests
- [ ] Rate limiting implemented
- [ ] Content-Type validation
- [ ] API authentication required

### 🟡 Important Items
- [ ] API versioning implemented
- [ ] Request size limits
- [ ] Response size limits
- [ ] Timeout configurations
- [ ] Error handling doesn't leak info

### 🟢 Recommended Items
- [ ] GraphQL query complexity limits
- [ ] WebSocket authentication
- [ ] API documentation security reviewed
- [ ] Request signing for critical operations
- [ ] Idempotency keys for payments

### Security Headers Checklist
```typescript
const requiredHeaders = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Content-Security-Policy': "default-src 'self'",
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
};
```

## Infrastructure & Configuration

### 🔴 Critical Items
- [ ] No secrets in code repository
- [ ] Environment-specific configurations
- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Unnecessary services disabled

### 🟡 Important Items
- [ ] Security patches up to date
- [ ] Dependency vulnerabilities scanned
- [ ] Container images scanned
- [ ] Network segmentation implemented
- [ ] Firewall rules configured

### 🟢 Recommended Items
- [ ] Infrastructure as Code (IaC) security
- [ ] Immutable infrastructure
- [ ] Blue-green deployments
- [ ] Chaos engineering practices
- [ ] Security automation

### Configuration Audit
```bash
# Check for exposed environment variables
env | grep -i "key\|secret\|password"

# Scan for vulnerabilities
npm audit
yarn audit --groups dependencies

# Check Docker images
docker scout cves <image-name>
```

## Logging & Monitoring

### 🔴 Critical Items
- [ ] Security events logged
- [ ] No sensitive data in logs
- [ ] Log injection prevention
- [ ] Logs stored securely
- [ ] Log retention policy defined

### 🟡 Important Items
- [ ] Centralized logging system
- [ ] Real-time alerting configured
- [ ] Anomaly detection active
- [ ] Failed authentication tracked
- [ ] Privilege escalation monitored

### 🟢 Recommended Items
- [ ] Log correlation implemented
- [ ] SIEM integration
- [ ] Threat intelligence feeds
- [ ] Automated response playbooks
- [ ] Regular log analysis

### Log Security Patterns
```typescript
// Sanitize before logging
logger.info('User login attempt', {
  email: user.email,
  ip: req.ip,
  password: '[REDACTED]', // Never log passwords
  sessionId: hashSessionId(session.id) // Hash sensitive identifiers
});

// Structured logging for security events
logger.security({
  event: 'AUTH_FAILURE',
  severity: 'warning',
  user: user.email,
  ip: req.ip,
  reason: 'invalid_password',
  timestamp: new Date().toISOString()
});
```

## Third-Party Security

### 🔴 Critical Items
- [ ] Dependencies vulnerability scanned
- [ ] License compliance verified
- [ ] API keys securely stored
- [ ] Webhook signatures validated
- [ ] Third-party services assessed

### 🟡 Important Items
- [ ] Supply chain security reviewed
- [ ] Dependency update process
- [ ] Vendor security assessments
- [ ] SLA security requirements
- [ ] Data processing agreements

### 🟢 Recommended Items
- [ ] Software bill of materials (SBOM)
- [ ] Dependency pinning
- [ ] Private package registry
- [ ] Vendor diversity strategy
- [ ] Exit strategies defined

## Compliance & Privacy

### 🔴 Critical Items
- [ ] Data classification implemented
- [ ] Privacy policy accurate
- [ ] Consent mechanisms working
- [ ] Data retention enforced
- [ ] Right to deletion implemented

### 🟡 Important Items
- [ ] GDPR compliance (EU users)
- [ ] CCPA compliance (California users)
- [ ] PCI DSS (payment cards)
- [ ] HIPAA (health data)
- [ ] SOC 2 controls

### 🟢 Recommended Items
- [ ] Privacy by design
- [ ] Data minimization
- [ ] Purpose limitation
- [ ] Privacy impact assessments
- [ ] Cross-border data transfer compliance

## Incident Response

### 🔴 Critical Items
- [ ] Incident response plan documented
- [ ] Security contact defined
- [ ] Backup systems tested
- [ ] Recovery procedures documented
- [ ] Communication plan ready

### 🟡 Important Items
- [ ] Incident classification defined
- [ ] Escalation procedures clear
- [ ] Legal counsel identified
- [ ] PR strategy prepared
- [ ] Customer notification templates

### 🟢 Recommended Items
- [ ] Tabletop exercises conducted
- [ ] Red team exercises
- [ ] Purple team collaboration
- [ ] Lessons learned process
- [ ] Continuous improvement cycle

## Security Testing Schedule

### Monthly
- [ ] Dependency vulnerability scan
- [ ] Security patch review
- [ ] Access control audit
- [ ] Log analysis review

### Quarterly
- [ ] Full security checklist review
- [ ] Penetration testing
- [ ] Security training update
- [ ] Incident response drill

### Annually
- [ ] Third-party security audit
- [ ] Compliance assessment
- [ ] Architecture security review
- [ ] Disaster recovery test

## Automation Scripts

```bash
#!/bin/bash
# Security audit automation script

echo "🔒 Starting Security Audit..."

# Check for secrets in code
echo "Checking for hardcoded secrets..."
grep -r "password\|secret\|key\|token" --include="*.ts" --include="*.js" \
  --exclude-dir=node_modules --exclude-dir=.git

# Run dependency audit
echo "Running dependency audit..."
npm audit

# Check security headers
echo "Testing security headers..."
curl -I https://your-app.com | grep -E "Strict-Transport-Security|X-Frame-Options|Content-Security-Policy"

# Run OWASP ZAP scan
echo "Running OWASP ZAP scan..."
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://your-app.com

echo "✅ Security audit complete!"
```

## References

- [OWASP Top 10](https://owasp.org/Top10/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)