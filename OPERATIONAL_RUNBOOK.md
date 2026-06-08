# CreditSentinel Operational Runbook

## If Memo Hallucination Alert Fires

1. Record application ID
2. Review memo content
3. Verify unsupported facts
4. Review prompt version
5. Decide:
   - Isolated issue → Monitor
   - Systematic issue → Rollback prompt
6. Post findings in #blockers

## If Risk Score Latency Alert Fires

1. Check CPU usage
2. Check memory usage
3. Check database performance
4. Check API latency
5. Investigate bottleneck
6. Escalate if unresolved

## If Red Flag False Positive Rate High

1. Review recent flagged applications
2. Verify correctness
3. Identify over-triggering rules
4. Adjust thresholds if required
5. Re-test on sample data

## If Success Rate Drops Below 99%

1. Review API logs
2. Check database connection
3. Check Render status
4. Investigate failures
5. Escalate if issue persists

## Daily Health Check

1. Review previous day's metrics
2. Check overnight alerts
3. Review #blockers channel
4. Confirm system status
5. Resolve open issues
