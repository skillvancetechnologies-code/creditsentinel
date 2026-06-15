# CreditSentinel Operational Runbook

## If Memo Hallucination Alert Fires

1. Record application ID
2. Review memo content
3. Verify unsupported facts
4. Review prompt version used
5. Determine incident scope:
   - Isolated issue → Monitor
   - Systematic issue → Roll back prompt version
6. Post findings in #blockers
7. Document resolution

---

## If Risk Score Latency Alert Fires

1. Check CPU usage
2. Check memory usage
3. Check database performance
4. Check API latency metrics
5. Investigate bottleneck
6. Apply mitigation:
   - Upgrade infrastructure if required
   - Optimize queries if required
   - Review model performance
7. Escalate if unresolved within SLA

---

## If Red Flag False Positive Rate High

1. Review recent flagged applications
2. Verify correctness of flags
3. Identify over-triggering rules
4. Adjust thresholds if required
5. Re-test on sample data
6. Document rule changes
7. Post update in #blockers

---

## If Success Rate Drops Below 99%

1. Review API logs
2. Check database connection
3. Check Render status
4. Investigate failures
5. Apply corrective actions
6. Escalate if issue persists
7. Document root cause

---

## Daily Health Check

Every Morning:

1. Review previous day's metrics
2. Check overnight alerts
3. Review #blockers channel
4. Confirm system status
5. Resolve open issues
6. Verify monitoring dashboards
7. Record observations

---

## Lessons Learned From Incident Drills

### Incident Simulation 1 – Portfolio Summary Latency Spike

Findings:
- Alert thresholds successfully detected elevated latency.
- Escalation process worked as expected.
- Root cause identification process was clear.

Improvement:
- Add expected response timelines for each alert severity.

---

### Incident Simulation 2 – Red Flag False Positive Spike

Findings:
- False positive review process successfully identified problematic rules.
- Rollback process restored expected behavior.

Improvement:
- Explicitly document rollback ownership and approval process.

---

## Additional Runbook Improvements

1. Add escalation timeline expectations:
   - Critical alerts: Immediate response
   - Warning alerts: Within 2 hours

2. Assign investigation owner for every incident.

3. Document rollback procedures more explicitly.

4. Record incident closure process:
   - Root cause identified
   - Fix implemented
   - Validation completed
   - Incident closed

5. Require post-incident summary documentation.

---

## Incident Closure Checklist

Before closing any incident:

- Root cause identified
- Fix implemented
- Monitoring confirms recovery
- No recurring alerts observed
- Stakeholders informed
- Incident report completed

Status: Approved
