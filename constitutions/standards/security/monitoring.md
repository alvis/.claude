# Security Monitoring Standards

_Standards for security event logging, alerting, and incident response_

## Core Monitoring Principles

### MUST Follow Rules

- **MUST log all security events** - Authentication, authorization, and suspicious activities
- **MUST protect log integrity** - Logs must be tamper-proof
- **MUST monitor in real-time** - Critical events need immediate attention
- **MUST retain logs securely** - Follow compliance requirements
- **MUST sanitize log data** - Never log passwords or sensitive data

### SHOULD Follow Guidelines

- **SHOULD aggregate logs centrally** - Single source of truth
- **SHOULD implement alerting rules** - Automated incident detection
- **SHOULD track metrics** - Security KPIs and trends
- **SHOULD automate responses** - For common attack patterns

## Security Event Types

### Event Classification

```typescript
enum SecurityEventType {
  // Authentication Events
  AUTH_SUCCESS = "auth_success",
  AUTH_FAILURE = "auth_failure",
  AUTH_LOCKOUT = "auth_lockout",
  PASSWORD_RESET = "password_reset",
  MFA_CHALLENGE = "mfa_challenge",

  // Authorization Events
  AUTHZ_FAILURE = "authz_failure",
  PRIVILEGE_ESCALATION = "privilege_escalation",
  ROLE_CHANGE = "role_change",

  // Security Violations
  RATE_LIMIT_EXCEEDED = "rate_limit_exceeded",
  INVALID_TOKEN = "invalid_token",
  SUSPICIOUS_ACTIVITY = "suspicious_activity",
  SQL_INJECTION_ATTEMPT = "sql_injection_attempt",
  XSS_ATTEMPT = "xss_attempt",

  // Data Events
  DATA_ACCESS = "data_access",
  DATA_MODIFICATION = "data_modification",
  DATA_EXPORT = "data_export",

  // System Events
  CONFIG_CHANGE = "config_change",
  SERVICE_START = "service_start",
  SERVICE_STOP = "service_stop",
}

interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  severity: "info" | "warning" | "error" | "critical";
  timestamp: string;
  source: {
    ip: string;
    userAgent?: string;
    geo?: GeoLocation;
  };
  user?: {
    id: string;
    email?: string;
    roles?: string[];
  };
  resource?: {
    type: string;
    id: string;
    action?: string;
  };
  details: Record<string, unknown>;
  metadata?: {
    sessionId?: string;
    requestId?: string;
    correlationId?: string;
  };
}
```

## Security Logger Implementation

### Core Logger

```typescript
import winston from "winston";
import { ElasticsearchTransport } from "winston-elasticsearch";

class SecurityLogger {
  private logger: winston.Logger;
  private alertManager: AlertManager;

  constructor() {
    this.logger = winston.createLogger({
      level: "info",
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
      ),
      defaultMeta: { service: "security" },
      transports: [
        // File transport for audit trail
        new winston.transports.File({
          filename: "security.log",
          level: "info",
          maxsize: 10485760, // 10MB
          maxFiles: 30,
          tailable: true,
        }),

        // Elasticsearch for analysis
        new ElasticsearchTransport({
          level: "info",
          clientOpts: {
            node: process.env.ELASTICSEARCH_URL,
            auth: {
              username: process.env.ELASTICSEARCH_USER,
              password: process.env.ELASTICSEARCH_PASS,
            },
          },
          index: "security-logs",
          dataStream: true,
        }),

        // Console for development
        ...(process.env.NODE_ENV !== "production"
          ? [
              new winston.transports.Console({
                format: winston.format.simple(),
              }),
            ]
          : []),
      ],
    });

    this.alertManager = new AlertManager();
  }

  async logSecurityEvent(event: Partial<SecurityEvent>): Promise<void> {
    const fullEvent: SecurityEvent = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      severity: "info",
      ...event,
      type: event.type!,
      source: event.source!,
      details: event.details || {},
    };

    // Log the event
    this.logger.log({
      level: this.mapSeverityToLevel(fullEvent.severity),
      message: `Security Event: ${fullEvent.type}`,
      ...fullEvent,
    });

    // Check if alerting is needed
    await this.checkAlertConditions(fullEvent);

    // Send to SIEM if configured
    if (process.env.SIEM_ENDPOINT) {
      await this.sendToSIEM(fullEvent);
    }
  }

  private mapSeverityToLevel(severity: string): string {
    const mapping: Record<string, string> = {
      info: "info",
      warning: "warn",
      error: "error",
      critical: "error",
    };
    return mapping[severity] || "info";
  }

  private async checkAlertConditions(event: SecurityEvent): Promise<void> {
    // Critical events always alert
    if (event.severity === "critical") {
      await this.alertManager.sendAlert({
        type: "immediate",
        event,
        channel: ["email", "slack", "pagerduty"],
      });
    }

    // Check for patterns
    await this.detectPatterns(event);
  }

  private async detectPatterns(event: SecurityEvent): Promise<void> {
    // Detect brute force attempts
    if (event.type === SecurityEventType.AUTH_FAILURE) {
      const recentFailures = await this.getRecentEvents({
        type: SecurityEventType.AUTH_FAILURE,
        "source.ip": event.source.ip,
        since: new Date(Date.now() - 15 * 60 * 1000), // Last 15 minutes
      });

      if (recentFailures.length >= 5) {
        await this.logSecurityEvent({
          type: SecurityEventType.SUSPICIOUS_ACTIVITY,
          severity: "warning",
          source: event.source,
          details: {
            pattern: "brute_force_attempt",
            failureCount: recentFailures.length,
            timeWindow: "15m",
          },
        });
      }
    }

    // Detect privilege escalation attempts
    if (event.type === SecurityEventType.AUTHZ_FAILURE) {
      const recentAuthzFailures = await this.getRecentEvents({
        type: SecurityEventType.AUTHZ_FAILURE,
        "user.id": event.user?.id,
        since: new Date(Date.now() - 5 * 60 * 1000), // Last 5 minutes
      });

      if (recentAuthzFailures.length >= 3) {
        await this.logSecurityEvent({
          type: SecurityEventType.SUSPICIOUS_ACTIVITY,
          severity: "error",
          source: event.source,
          user: event.user,
          details: {
            pattern: "privilege_escalation_attempt",
            failureCount: recentAuthzFailures.length,
          },
        });
      }
    }
  }

  private async sendToSIEM(event: SecurityEvent): Promise<void> {
    try {
      await fetch(process.env.SIEM_ENDPOINT!, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.SIEM_TOKEN}`,
        },
        body: JSON.stringify(event),
      });
    } catch (error) {
      this.logger.error("Failed to send event to SIEM", { error, event });
    }
  }
}
```

## Alert Management

### Alert Configuration

```typescript
interface AlertRule {
  id: string;
  name: string;
  condition: AlertCondition;
  actions: AlertAction[];
  cooldown?: number; // Minutes before re-alerting
  enabled: boolean;
}

interface AlertCondition {
  eventType?: SecurityEventType[];
  severity?: string[];
  threshold?: {
    count: number;
    window: number; // Minutes
  };
  pattern?: string;
  customQuery?: string;
}

interface AlertAction {
  type: "email" | "slack" | "webhook" | "pagerduty";
  config: Record<string, unknown>;
  template?: string;
}

class AlertManager {
  private rules: AlertRule[] = [
    {
      id: "brute-force",
      name: "Brute Force Attack Detection",
      condition: {
        eventType: [SecurityEventType.AUTH_FAILURE],
        threshold: { count: 5, window: 15 },
      },
      actions: [
        {
          type: "slack",
          config: { channel: "#security-alerts" },
          template: "Brute force attack detected from {{source.ip}}",
        },
        {
          type: "email",
          config: { to: "security@example.com" },
        },
      ],
      cooldown: 30,
      enabled: true,
    },
    {
      id: "critical-security",
      name: "Critical Security Event",
      condition: {
        severity: ["critical"],
      },
      actions: [
        {
          type: "pagerduty",
          config: { serviceKey: process.env.PAGERDUTY_KEY },
        },
      ],
      enabled: true,
    },
  ];

  async sendAlert(alert: {
    type: string;
    event: SecurityEvent;
    channel: string[];
  }): Promise<void> {
    for (const channelType of alert.channel) {
      switch (channelType) {
        case "email":
          await this.sendEmailAlert(alert.event);
          break;
        case "slack":
          await this.sendSlackAlert(alert.event);
          break;
        case "pagerduty":
          await this.sendPagerDutyAlert(alert.event);
          break;
      }
    }
  }

  private async sendSlackAlert(event: SecurityEvent): Promise<void> {
    const webhook = process.env.SLACK_WEBHOOK_URL;

    await fetch(webhook!, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: `Security Alert: ${event.type}`,
        attachments: [
          {
            color: this.getSeverityColor(event.severity),
            fields: [
              { title: "Type", value: event.type, short: true },
              { title: "Severity", value: event.severity, short: true },
              { title: "Source IP", value: event.source.ip, short: true },
              { title: "User", value: event.user?.email || "N/A", short: true },
              { title: "Details", value: JSON.stringify(event.details) },
            ],
            timestamp: Math.floor(Date.now() / 1000),
          },
        ],
      }),
    });
  }

  private getSeverityColor(severity: string): string {
    const colors: Record<string, string> = {
      info: "#36a64f",
      warning: "#ff9900",
      error: "#ff0000",
      critical: "#ff0000",
    };
    return colors[severity] || "#808080";
  }
}
```

## Security Metrics

### Metrics Collection

```typescript
interface SecurityMetrics {
  authenticationMetrics: {
    successfulLogins: number;
    failedLogins: number;
    averageLoginTime: number;
    uniqueUsers: number;
  };
  authorizationMetrics: {
    deniedRequests: number;
    privilegedAccess: number;
    roleChanges: number;
  };
  securityViolations: {
    rateLimitViolations: number;
    injectionAttempts: number;
    suspiciousActivities: number;
  };
  systemHealth: {
    activeUsers: number;
    activeSessions: number;
    apiLatency: number;
  };
}

class SecurityMetricsCollector {
  private metrics = new Map<string, number>();

  increment(metric: string, value: number = 1): void {
    const current = this.metrics.get(metric) || 0;
    this.metrics.set(metric, current + value);
  }

  gauge(metric: string, value: number): void {
    this.metrics.set(metric, value);
  }

  async collectMetrics(): Promise<SecurityMetrics> {
    return {
      authenticationMetrics: {
        successfulLogins: this.metrics.get("auth.success") || 0,
        failedLogins: this.metrics.get("auth.failure") || 0,
        averageLoginTime: this.metrics.get("auth.duration.avg") || 0,
        uniqueUsers: await this.getUniqueUsers(),
      },
      authorizationMetrics: {
        deniedRequests: this.metrics.get("authz.denied") || 0,
        privilegedAccess: this.metrics.get("authz.privileged") || 0,
        roleChanges: this.metrics.get("authz.role_changes") || 0,
      },
      securityViolations: {
        rateLimitViolations: this.metrics.get("security.rate_limit") || 0,
        injectionAttempts: this.metrics.get("security.injection") || 0,
        suspiciousActivities: this.metrics.get("security.suspicious") || 0,
      },
      systemHealth: {
        activeUsers: await this.getActiveUsers(),
        activeSessions: await this.getActiveSessions(),
        apiLatency: this.metrics.get("api.latency.p95") || 0,
      },
    };
  }

  private async getUniqueUsers(): Promise<number> {
    // Implementation to count unique users
    return 0;
  }

  private async getActiveUsers(): Promise<number> {
    // Implementation to count active users
    return 0;
  }

  private async getActiveSessions(): Promise<number> {
    // Implementation to count active sessions
    return 0;
  }
}
```

## Incident Response

### Automated Responses

```typescript
interface IncidentResponse {
  trigger: SecurityEventType;
  condition: (event: SecurityEvent) => boolean;
  action: (event: SecurityEvent) => Promise<void>;
}

class IncidentResponseManager {
  private responses: IncidentResponse[] = [
    {
      trigger: SecurityEventType.SUSPICIOUS_ACTIVITY,
      condition: (event) => event.details.pattern === "brute_force_attempt",
      action: async (event) => {
        // Block IP address
        await this.blockIP(event.source.ip, 3600); // 1 hour

        // Invalidate all sessions from this IP
        await this.invalidateSessionsByIP(event.source.ip);

        // Log the action
        await securityLogger.logSecurityEvent({
          type: SecurityEventType.SUSPICIOUS_ACTIVITY,
          severity: "warning",
          source: event.source,
          details: {
            action: "ip_blocked",
            duration: 3600,
            reason: "brute_force_attempt",
          },
        });
      },
    },
    {
      trigger: SecurityEventType.SQL_INJECTION_ATTEMPT,
      condition: () => true,
      action: async (event) => {
        // Block request immediately
        await this.blockIP(event.source.ip, 86400); // 24 hours

        // Alert security team
        await this.alertSecurityTeam({
          priority: "high",
          event,
          message: "SQL injection attempt detected",
        });
      },
    },
  ];

  async handleIncident(event: SecurityEvent): Promise<void> {
    for (const response of this.responses) {
      if (response.trigger === event.type && response.condition(event)) {
        await response.action(event);
      }
    }
  }

  private async blockIP(ip: string, duration: number): Promise<void> {
    // Add IP to blocklist
    await redis.setex(`blocked_ip:${ip}`, duration, "1");
  }

  private async invalidateSessionsByIP(ip: string): Promise<void> {
    // Find and invalidate all sessions from this IP
    const sessions = await this.findSessionsByIP(ip);
    for (const sessionId of sessions) {
      await redis.del(`session:${sessionId}`);
    }
  }
}
```

## Log Retention and Compliance

### Retention Policy

```typescript
interface LogRetentionPolicy {
  security: number; // Days
  audit: number;
  compliance: number;
  operational: number;
}

const retentionPolicy: LogRetentionPolicy = {
  security: 365, // 1 year
  audit: 2555, // 7 years
  compliance: 1825, // 5 years
  operational: 90, // 3 months
};

// Implement log rotation
class LogRotationService {
  async rotateLogs(): Promise<void> {
    const cutoffDates = {
      security: new Date(
        Date.now() - retentionPolicy.security * 24 * 60 * 60 * 1000,
      ),
      audit: new Date(Date.now() - retentionPolicy.audit * 24 * 60 * 60 * 1000),
      compliance: new Date(
        Date.now() - retentionPolicy.compliance * 24 * 60 * 60 * 1000,
      ),
      operational: new Date(
        Date.now() - retentionPolicy.operational * 24 * 60 * 60 * 1000,
      ),
    };

    // Archive old logs
    for (const [logType, cutoffDate] of Object.entries(cutoffDates)) {
      await this.archiveLogs(logType, cutoffDate);
    }
  }

  private async archiveLogs(logType: string, cutoffDate: Date): Promise<void> {
    // Implementation to move logs to cold storage
  }
}
```

## Testing Security Monitoring

```typescript
describe("Security Monitoring", () => {
  let logger: SecurityLogger;
  let alertManager: AlertManager;

  describe("Event Logging", () => {
    it("should log authentication failures", async () => {
      const event: Partial<SecurityEvent> = {
        type: SecurityEventType.AUTH_FAILURE,
        source: { ip: "192.168.1.1" },
        user: { email: "test@example.com" },
      };

      await logger.logSecurityEvent(event);

      const logs = await getRecentLogs();
      expect(logs).toContainEqual(
        expect.objectContaining({ type: SecurityEventType.AUTH_FAILURE }),
      );
    });

    it("should sanitize sensitive data", async () => {
      const event: Partial<SecurityEvent> = {
        type: SecurityEventType.AUTH_SUCCESS,
        details: {
          password: "secret123",
          token: "jwt-token",
        },
      };

      await logger.logSecurityEvent(event);

      const logs = await getRecentLogs();
      expect(logs[0].details.password).toBe("[REDACTED]");
      expect(logs[0].details.token).toBe("[REDACTED]");
    });
  });

  describe("Alert Detection", () => {
    it("should detect brute force attempts", async () => {
      // Simulate multiple failed logins
      for (let i = 0; i < 6; i++) {
        await logger.logSecurityEvent({
          type: SecurityEventType.AUTH_FAILURE,
          source: { ip: "10.0.0.1" },
        });
      }

      const alerts = await getRecentAlerts();
      expect(alerts).toContainEqual(
        expect.objectContaining({
          pattern: "brute_force_attempt",
        }),
      );
    });
  });
});
```

## References

- [Logging Standards](../code/logging.md)
- [Alert Configuration](./alerting.md)
- [SIEM Integration](./siem-integration.md)
