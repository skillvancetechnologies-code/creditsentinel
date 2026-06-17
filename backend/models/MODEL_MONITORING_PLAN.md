# ML Model Monitoring Plan — Week 5

## During Load Test (Wednesday)

### Metrics to Track

1. Inference Latency
   - Per-request latency for /api/score
   - Target: p99 <100ms under 100 concurrent requests

2. Model Output Validity
   - Are all scores in 0-100 range?
   - Are risk tiers assigned correctly?
   - SHAP explanations present?

3. Error Rate
   - Failed requests percentage
   - Timeout count
   - Target: <0.1% error rate

4. System Resource Usage
   - Server CPU during test
   - Server memory during test
   - Database connection count

### Logging Setup

- Log every prediction with: timestamp, latency, score, error (if any)
- Use structured logging (JSON format)
- Save logs for post-test analysis

### Success Criteria

- p99 latency <100ms
- 100% valid scores (0-100 range)
- Error rate <0.1%
- CPU <80%, Memory <70%

### Failure Indicators

- p99 latency >200ms (degradation)
- Score out of range (logic error)
- Error rate >1% (system issues)
