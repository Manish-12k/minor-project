# API Contracts & Payload Specifications

## Telemetry Submission Endpoint

**POST** `/api/telemetry/submit`

### Request Payload

```json
{
  "payload": {
    "v": 1,
    "device": {
      "screenResolution": [1920, 1080],
      "colorDepth": 24,
      "timezone": "Asia/Kolkata"
    },
    "mouse": {
      "velocity_mean": 12.5,
      "velocity_stddev": 3.2,
      "movement_entropy": 4.8
    },
    "keyboard": {
      "typing_speed": 45,
      "keystroke_entropy": 3.5
    },
    "timing": {
      "event_loop_jitter": 3.2
    }
  },
  "signature": "hmac-sha256-signature",
  "nonce": "random-32-byte-hex",
  "timestamp": 1707122400000,
  "session_id": "session-hash"
}
```

### Response

```json
{
  "risk_score": 35,
  "friction_level": "SOFT",
  "recommended_action": "SOFT_CHALLENGE",
  "challenge": {
    "type": "SLIDER",
    "description": "Slide to verify"
  }
}
```

## Inference Endpoint

**POST** `/api/predict`

### Request

```json
{
  "telemetry": { /* full telemetry object */ },
  "session_id": "session-id"
}
```

### Response

```json
{
  "risk_score": 45,
  "bot_probability": 0.35,
  "confidence": 0.82,
  "latency_ms": 47.3,
  "recommended_action": "SOFT_CHALLENGE"
}
```

## Challenge Validation Endpoint

**POST** `/api/challenge/validate`

### Request

```json
{
  "session_id": "session-id",
  "challenge_type": "SLIDER",
  "response": {
    "value": 100
  }
}
```

### Response

```json
{
  "valid": true,
  "message": "Challenge passed",
  "session_token": "new-session-token"
}
```