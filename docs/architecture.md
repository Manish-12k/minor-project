# UIDAI Passive Bot Detection System - Architecture

## Overview

This document provides a comprehensive technical overview of the passive bot-detection system designed to replace CAPTCHA for UIDAI portals.

## System Components

### 1. Frontend Telemetry Collector
- **Purpose:** Silently collect behavioral and environmental signals
- **Technologies:** React/TypeScript, Flutter
- **Key Features:**
  - Non-invasive signal collection
  - Headless browser detection
  - Anti-tamper mechanisms
  - Optimized payload compression

### 2. Backend ML Engine
- **Purpose:** Real-time classification of sessions as human or bot
- **Architecture:** Ensemble of XGBoost, LSTM, Anomaly Detection
- **Latency Target:** <100ms

### 3. Risk Scoring Engine
- **Purpose:** Map ML predictions to actionable risk levels
- **Features:** Multi-factor assessment, temporal adjustments

### 4. Enforcement Layer
- **Purpose:** Apply adaptive friction based on risk
- **Mechanisms:** Invisible challenges, sliders, cognitive tasks

## Data Flow

```
User Portal
    ↓
Telemetry Collector (silent)
    ↓
API Gateway (validation, anti-replay)
    ↓
ML Inference Engine
    ↓
Risk Scoring
    ↓
Decision: Allow / Challenge / Block
```

## Deployment Architecture

- **Multi-region Kubernetes clusters**
- **Horizontal autoscaling based on RPS**
- **Stateless ML serving**
- **Redis session cache**

## Security Features

- Signature-verified payloads (HMAC-SHA256)
- Session-based replay protection
- Headless browser detection
- Runtime integrity checks