# INCIDENT_PLAYBOOK

## Purpose

Provide operational response procedures for production incidents.

---

# Incident Severity Levels

## Critical

Examples:

* Service unavailable
* Error rate >5%
* Database outage

Response Time:
Immediate

---

## Warning

Examples:

* Latency >2 seconds
* Elevated false positives
* Degraded performance

Response Time:
Within 2 hours

---

# Scenario 1 — Error Rate Above 5%

## Detection

Monitoring alert triggered.

Threshold:

```text
Error Rate > 5%
```

## Response Steps

1. Review application logs
2. Identify affected endpoints
3. Verify database connectivity
4. Verify Render service health
5. Determine root cause

### Escalation

Post in #blockers immediately.

### Resolution

* Fix issue
* Validate endpoints
* Confirm error rate returns to normal

---

# Scenario 2 — Latency Above 2 Seconds

## Detection

Monitoring alert triggered.

Threshold:

```text
p95 Latency > 2000ms
```

## Diagnosis Steps

1. Check Render CPU usage
2. Check memory utilization
3. Review database performance
4. Review API response times
5. Identify bottleneck

### Common Causes

* Infrastructure saturation
* Slow database queries
* External API latency

### Resolution

* Scale resources
* Optimize queries
* Apply caching

---

# Scenario 3 — False Positives Increase

## Detection

Audit or monitoring identifies increase.

Threshold:

```text
False Positive Rate > 3%
```

## Investigation

1. Review recent flagged applications
2. Compare with expected outcomes
3. Identify problematic rules
4. Review threshold configuration

## Resolution

1. Roll back recent rule changes
2. Re-test sample applications
3. Validate corrected behavior

---

# Contact Escalation List

## Level 1

Operational Monitoring Owner

Responsibilities:

* Initial investigation
* Alert acknowledgement
* Incident logging

---

## Level 2

Backend Lead

Responsibilities:

* API investigation
* Database investigation
* Deployment rollback

---

## Level 3

Project Lead

Responsibilities:

* Major incident coordination
* Deployment decisions
* Stakeholder communication

---

# Health Check Procedure

## Daily

1. Review dashboard metrics
2. Check error rates
3. Review latency metrics
4. Review overnight alerts
5. Confirm services operational

---

## Weekly

1. Review application logs
2. Review alert history
3. Review incident reports
4. Validate monitoring thresholds

---

## Monthly

1. Audit sample decisions
2. Review false positives
3. Review memo quality
4. Validate operational procedures
5. Update runbook if needed

---

# Incident Closure Checklist

Before closing incident:

* Root cause identified
* Fix implemented
* Monitoring confirms recovery
* No recurring alerts observed
* Incident documented

Status: APPROVED

