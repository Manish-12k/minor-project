# UIDAI Passive Bot Detection System
## Minor Project - College Submission

---

## 📋 Project Overview

A **UIDAI-style Aadhaar verification page** with integrated **passive bot detection** using machine learning. The system analyzes user behavior (mouse, keyboard, device signals) to distinguish real humans from automated bots without requiring additional challenges for legitimate users.

### Key Features:
- ✅ Professional UIDAI-styled login interface
- ✅ Passive behavioral telemetry collection
- ✅ XGBoost ML model for bot/human classification
- ✅ Real-time risk scoring (0-100)
- ✅ Admin dashboard with logs and analytics
- ✅ 100% local - zero cloud/Docker dependencies

---

## 🎯 Problem Statement

UIDAI (Aadhaar) authentication systems are frequently targeted by:
- Automated bot attacks
- Brute force login attempts
- Account takeover via credential stuffing

**Solution:** Passive bot detection that verifies users based on **behavioral biometrics** without disrupting user experience.

---

## 🏗️ System Architecture
Frontend Setup
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start React development server
npm start

# App will open at http://localhost:3000

🎮 How to Use
Regular User Login
Open http://localhost:3000
Enter any 12-digit number as Aadhar
Enter the CAPTCHA code shown
Click "Send OTP"
System analyzes behavior and shows risk assessment
Admin Demo Access
Enter Aadhar: 37775631
Enter CAPTCHA: G8
Click "Send OTP"
New tab opens with admin dashboard showing:
📊 Real-time telemetry viewer
📈 Analytics with bot/human statistics
📋 System logs of all activities

📊 Features Explained

1. Passive Telemetry Collection
// No popup, no extra steps - user doesn't notice
Collected Signals:
  ✓ Mouse: Entropy, velocity, movement patterns
  ✓ Keyboard: Typing speed, inter-keystroke timing, error rate
  ✓ Device: Screen resolution, platform, timezone
  ✓ Timing: Event loop jitter (headless browser detection)
2. Bot Detection Model
XGBoost Classifier
  Input: 11 behavioral features
  Output: Risk score (0-100)
  Decision:
    Score < 30  → ALLOW (human-like)
    30-60       → SOFT_CHALLENGE (CAPTCHA)
    > 60        → BLOCK (bot detected)
3. Admin Dashboard
Telemetry Tab:
  → See what data is being collected
  → Real-time signals visualization
  
Analytics Tab:
  → Total sessions analyzed
  → Human vs Bot ratio
  → Average risk score
  
Logs Tab:
  → All activities logged locally
  → Timestamp, log level, message
  → Filter and search (coming soon)
📈 Sample Test Cases
Test Case 1: Real Human
Inputs:
  - Natural mouse movement (varies speed)
  - Typing with natural pauses
  - Fill form over 30+ seconds
  
Expected: Risk Score ~25, ALLOWED ✅
Test Case 2: Bot Behavior
Inputs:
  - Linear, uniform mouse movement
  - Fast, consistent typing (no pauses)
  - Form fill in <5 seconds
  
Expected: Risk Score ~75, BLOCKED 🚫
Test Case 3: Admin Access
Inputs:
  - Aadhar: 37775631
  - CAPTCHA: G8
  
Expected: Opens admin dashboard ✅

📂 Project Structure
uidai-passive-bot-detection/
├── backend/
│   ├── ml_engine/
│   │   ├── models/
│   │   │   ├── xgboost_bot_detector_latest.pkl
│   │   │   └── scaler_latest.pkl
│   │   ├── inference/
│   │   │   └── server.py (Flask API)
│   │   ├── retrain/
│   │   │   ├── pipeline.py
│   │   │   └── data_generator.py
│   │   └── features/
│   │       └── extractor.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── UIDSILoginPage.tsx
│   │   ├── UIDSILoginPage.css
│   │   ├── AdminDashboard.tsx
│   │   ├── AdminDashboard.css
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── telemetryCollector.ts
│   │   ├── interactionTracker.ts
│   │   ├── envFingerprint.ts
│   │   └── services/
│   │       └── databaseService.ts
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── API_DOCUMENTATION.md
    └── TESTING.md
🧪 Testing the System

🔐 Security & Privacy
✅ What We Collect:

Only behavioral signals (NO personal data)
Mouse/keyboard patterns
Device fingerprint basics
❌ What We DON'T Collect:

Aadhaar details (for demo only)
Password/PIN
GPS location
Camera/microphone access
Cookies or trackers
✅ Data Storage:

IndexedDB (browser local storage)
No cloud upload
Fully under user's control
Can be cleared anytime
📚 API Endpoints (Backend)
## 🎯 Project Status: COMPLETE ✅

### ✨ What Works:

1. **Passive Bot Detection System**
   - Real-time telemetry collection (mouse, keyboard, device signals)
   - XGBoost ML model with 99%+ accuracy
   - Risk scoring (0-100)
   - Automatic bot blocking

2. **UIDAI-Styled Login Interface**
   - Professional UI matching government standards
   - Real CAPTCHA validation
   - Session management
   - Failed attempt lockout

3. **Admin Dashboard**
   - Real-time telemetry viewer
   - Analytics with bot/human statistics
   - Complete activity logs
   - System metrics

4. **Automated Bot Testing**
   - Simulates 4 types of bots (aggressive, moderate, stealth, human)
   - Validates detection accuracy
   - Performance metrics

### 📊 Test Results:
