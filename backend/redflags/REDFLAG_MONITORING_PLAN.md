# Red Flag Detection Monitoring Plan

## Daily Metrics

### Detection Performance

* Total applications processed
* Average detection latency
* Success rate
* Error count

### Quality Metrics

* Flags generated (count and rate)
* False positive count (estimated)
* False negative count (estimated)
* Evidence quality average

### Alert Thresholds

* Alert if p99 latency > 500ms
* Alert if false positive rate > 2%
* Alert if false negative rate > 5%
* Alert if error rate > 0.1%

## Weekly Review

Every Monday:

* Audit 30-application sample
* Manual verification of flags
* False positive/negative analysis
* Rule threshold adjustment if needed

## Escalation

### Performance Alerts

Post in #blockers within 2 hours

### Accuracy Issues

Post in #blockers within 4 hours

## Success Criteria

* Maintain precision > 95%
* Maintain recall > 90%
* Maintain evidence quality > 4.5/5
* Maintain system uptime > 99.9%

