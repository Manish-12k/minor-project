import React, { useEffect, useState, useRef } from 'react';
import { API_BASE_URL } from './config';
import './UIDSILoginPage.css';
import { TelemetryCollector } from './telemetryCollector';
import { InteractionTracker } from './interactionTracker';
import { EnvironmentFingerprint } from './envFingerprint';

interface BotDetectionResult {
  risk_score: number;
  is_bot: boolean;
  recommended_action: string;
}

const UIDSILoginPage: React.FC = () => {
  const [aadharInput, setAadharInput] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaText, setCaptchaText] = useState('bbfd68');
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [isLocked, setIsLocked] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const sessionStartedAtRef = useRef<number>(Date.now());

  // Generate random CAPTCHA
  const generateCaptcha = () => {
    const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789';
    let captcha = '';
    for (let i = 0; i < 6; i++) {
      captcha += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setCaptchaText(captcha);
  };

  // Verify CAPTCHA
  const verifyCaptcha = () => {
    return captchaInput.toLowerCase() === captchaText.toLowerCase();
  };

  // Check for bot using our ML model
  const checkIfBot = async (): Promise<BotDetectionResult> => {
    setIsChecking(true);
    try {
      const telemetryCollector = new TelemetryCollector();
      const interactionTracker = new InteractionTracker();

      const deviceFp = telemetryCollector.captureDeviceFingerprint();
      const interactions = interactionTracker.getAllSignals();
      const headlessSignals = EnvironmentFingerprint.detectHeadlessIndicators();
      const jitter = await EnvironmentFingerprint.measureEventLoopJitter();

      const payload = {
        telemetry: {
          device: deviceFp,
          mouse: interactions?.mouse || {},
          keyboard: interactions?.keyboard || {},
          timing: {
            event_loop_jitter: jitter,
            headless_indicators: headlessSignals,
            total_interaction_time_ms: Date.now() - sessionStartedAtRef.current
          }
        },
        session_id: 'uidai-' + Date.now()
      };

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Bot detection API failed');
      }

      const result = await response.json();

      const botResult: BotDetectionResult = {
        risk_score: result.risk_score,
        is_bot: result.risk_score > 60,
        recommended_action: result.recommended_action
      };

      return botResult;
    } catch (error) {
      console.error('Bot detection error:', error);
      return {
        risk_score: 50,
        is_bot: false,
        recommended_action: 'SOFT_CHALLENGE'
      };
    } finally {
      setIsChecking(false);
    }
  };

  // Handle login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    // Check if locked
    if (isLocked) {
      setErrorMessage('Too many attempts. Please try again later.');
      return;
    }

    // Check admin credentials FIRST
    if (aadharInput === '37775631' && captchaInput === 'G8') {
      setSuccessMessage('✅ Admin access granted! Opening dashboard...');
      setTimeout(() => {
        window.open('/admin-dashboard', '_blank', 'width=1400,height=900');
      }, 500);
      setAadharInput('');
      setCaptchaInput('');
      generateCaptcha();
      return;
    }

    // Validate Aadhar
    if (!aadharInput || aadharInput.length !== 12) {
      setErrorMessage('Please enter a valid 12-digit Aadhar number');
      return;
    }

    // Verify CAPTCHA first
    if (!verifyCaptcha()) {
      setErrorMessage('❌ Incorrect CAPTCHA. Please try again.');
      setLoginAttempts(prev => prev + 1);
      generateCaptcha();
      setCaptchaInput('');
      if (loginAttempts >= 2) {
        setIsLocked(true);
      }
      return;
    }

    // Check for bot
    const botResult = await checkIfBot();

    if (botResult.is_bot) {
      setErrorMessage('🚫 Bot detected! Please try again with natural interactions.');
      setLoginAttempts(prev => prev + 1);
      if (loginAttempts >= 2) {
        setIsLocked(true);
      }
      return;
    }

    // Success
    setSuccessMessage('✅ Verification successful! Sending OTP...');
    setTimeout(() => {
      setAadharInput('');
      setCaptchaInput('');
      generateCaptcha();
    }, 1500);
  };

  // Handle refresh CAPTCHA
  const handleRefreshCaptcha = () => {
    generateCaptcha();
    setCaptchaInput('');
  };

  // Initialize on mount
  useEffect(() => {
    generateCaptcha();
  }, []);

  return (
    <div className="uidai-page">
      {/* Header */}
      <header className="uidai-header">
        <div className="header-top">
          <div className="logo-india">🇮🇳</div>
          <h1 className="header-title">Unique Identification Authority of India</h1>
          <div className="logo-aadhaar">🔴</div>
        </div>
        <nav className="header-nav">
          <div className="nav-wrapper">
            <span className="nav-icon">☰</span>
            <span className="nav-brand">myAadhaar</span>
            <div className="nav-right">
              <span className="language">🌐 English ▼</span>
            </div>
          </div>
        </nav>
        <div className="nav-breadcrumb">
          <span>Dashboard</span>
          <span> › </span>
          <span className="breadcrumb-active">eAadhaar Download</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="uidai-main">
        <div className="container">
          {/* Left Column - Form */}
          <div className="form-section">
            <div className="form-card">
              <h2 className="form-title">eAadhaar Download / Verification</h2>
              <p className="form-subtitle">Select 12 digit Aadhar Number</p>

              {errorMessage && (
                <div className="alert alert-error">
                  {errorMessage}
                </div>
              )}

              {successMessage && (
                <div className="alert alert-success">
                  {successMessage}
                </div>
              )}

              <form onSubmit={handleLogin} className="login-form">
                {/* Aadhar Input */}
                <div className="form-group">
                  <label className="form-label">Enter Aadhar Number</label>
                  <input
                    type="text"
                    placeholder="Enter Aadhar Number"
                    value={aadharInput}
                    onChange={(e) => setAadharInput(e.target.value.replace(/\D/g, '').slice(0, 12))}
                    maxLength={12}
                    disabled={isLocked}
                    className="form-input"
                  />
                </div>

                {/* CAPTCHA */}
                <div className="form-group">
                  <label className="form-label">Enter Captcha</label>
                  <div className="captcha-wrapper">
                    <div className="captcha-box">
                      <span className="captcha-text">{captchaText}</span>
                    </div>
                    <button
                      type="button"
                      className="captcha-btn"
                      onClick={handleRefreshCaptcha}
                      title="Refresh"
                    >
                      🔄
                    </button>
                  </div>
                  <input
                    type="text"
                    placeholder="Enter Captcha"
                    value={captchaInput}
                    onChange={(e) => setCaptchaInput(e.target.value)}
                    disabled={isLocked}
                    className="form-input"
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  className={`submit-btn ${isLocked ? 'disabled' : ''}`}
                  disabled={isLocked || isChecking}
                >
                  {isChecking ? '⏳ Checking...' : '📬 Send OTP'}
                </button>

                {isLocked && (
                  <p className="locked-msg">🔒 Account locked. Too many attempts.</p>
                )}

                {loginAttempts > 0 && loginAttempts < 3 && (
                  <p className="attempts-msg">⚠️ Attempts: {3 - loginAttempts} remaining</p>
                )}
              </form>

              {/* FAQ */}
              <div className="faq-section">
                <h3 className="faq-title">❓ Frequently Asked Questions</h3>
                <details className="faq-item">
                  <summary>What is e-Aadhar?</summary>
                  <p>e-Aadhar is an electronic version of your Aadhar document.</p>
                </details>
                <details className="faq-item">
                  <summary>What is this Passive Bot Detection?</summary>
                  <p>Our system analyzes your behavior to verify you're human, not a bot.</p>
                </details>
                <details className="faq-item">
                  <summary>Is my data safe?</summary>
                  <p>Yes! We follow strict privacy protocols and don't store personal data.</p>
                </details>
              </div>
            </div>
          </div>

          {/* Right Column - Info */}
          <div className="info-section">
            <div className="info-card">
              <h3 className="info-title">🛡️ Passive Bot Detection Active</h3>
              <p className="info-status">✅ Telemetry Collected</p>
              <p className="info-text">
                Moving your mouse and typing naturally helps us verify you're human.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="uidai-footer">
        <p>© 2026 Unique Identification Authority of India. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default UIDSILoginPage;