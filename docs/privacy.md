# Privacy & Compliance Documentation

## Data Minimization

### What Is Collected
- ✓ Mouse movement statistics (entropy, velocity, acceleration)
- ✓ Keyboard dynamics (timing, rhythm, error rate)
- ✓ Device fingerprint (resolution, color depth, timezone)
- ✓ Network conditions (connection type, RTT)
- ✓ Event sequences (order, timing, NOT raw content)

### What Is NOT Collected
- ✗ Any personally identifiable information (PII)
- ✗ Aadhaar numbers, names, email addresses
- ✗ Biometric templates
- ✗ Actual text typed or passwords
- ✗ Raw mouse/keyboard paths
- ✗ Browser history or cookies

## Retention Policy

| Data Type | Retention Period | Purpose |
|-----------|------------------|---------|
| Raw Telemetry | 4 hours | Real-time inference |
| Feature Summaries | 24 hours | Quality monitoring |
| Model Predictions | 7 days | Drift detection |
| Training Labels | 30 days | Model retraining |
| Audit Logs | 90 days | Compliance |

## Anonymization

- Session IDs are one-way hashed with session-specific salt
- Behavioral data converted to statistical summaries
- Training data batch-aggregated (impossible to reverse)
- No cross-session linking

## UIDAI Compliance

- ✓ Full alignment with Aadhaar privacy guidelines
- ✓ On-premise processing (no third-party sharing)
- ✓ Regular security audits
- ✓ User appeal mechanism
- ✓ Transparency reports