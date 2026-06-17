import json
import statistics

def analyze_logs(logfile='model_predictions.log'):
    """Analyze model performance during load test"""
    
    latencies = []
    errors = 0
    success = 0
    scores = []
    
    with open(logfile, 'r') as f:
        for line in f:
            entry = json.loads(line)
            
            if entry['status'] == 'success':
                success += 1
                latencies.append(entry['latency_ms'])
                scores.append(entry['risk_score'])
            else:
                errors += 1
    
    # Calculate statistics
    latencies.sort()
    total = success + errors
    
    print(f"Total Requests: {total}")
    print(f"Success: {success} ({success/total*100:.1f}%)")
    print(f"Errors: {errors} ({errors/total*100:.1f}%)")
    print(f"")
    print(f"Latency (ms):")
    print(f"  Min: {min(latencies):.2f}")
    print(f"  Max: {max(latencies):.2f}")
    print(f"  Mean: {statistics.mean(latencies):.2f}")
    print(f"  Median: {statistics.median(latencies):.2f}")
    print(f"  p95: {latencies[int(0.95*len(latencies))]:.2f}")
    print(f"  p99: {latencies[int(0.99*len(latencies))]:.2f}")
    print(f"")
    print(f"Score Distribution:")
    print(f"  Min: {min(scores):.1f}")
    print(f"  Max: {max(scores):.1f}")
    print(f"  Mean: {statistics.mean(scores):.1f}")

if __name__ == '__main__':
    analyze_logs()
