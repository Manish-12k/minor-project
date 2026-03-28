import React, { useEffect, useState, useRef } from 'react';
import './App.css';
import { API_BASE_URL } from './config';

interface TelemetryData {
  deviceFingerprint: any;
  interactions: any;
  headlessIndicators: any;
  eventLoopJitter: number;
}

interface RiskResult {
  risk_score: number;
  bot_probability: number;
  recommended_action: string;
  latency_ms: number;
  reasoning: string;
}

const App: React.FC = () => {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [riskResult, setRiskResult] = useState<RiskResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [mouseX, setMouseX] = useState(0);
  const [mouseY, setMouseY] = useState(0);
  const sessionStartedAtRef = useRef<number>(Date.now());

  useEffect(() => {
    const simulateInit = async () => {
      const handleMouseMove = (e: MouseEvent) => {
        setMouseX(e.clientX);
        setMouseY(e.clientY);
      };

      document.addEventListener('mousemove', handleMouseMove);

      await new Promise(resolve => setTimeout(resolve, 3000));

      const screenWidth = typeof window !== 'undefined' ? window.innerWidth : 1920;
      const screenHeight = typeof window !== 'undefined' ? window.innerHeight : 1080;
      const colorDepth = typeof window !== 'undefined' && 'screen' in window
        ? (window.screen as any).colorDepth || 24
        : 24;

      const telemetryData: TelemetryData = {
        deviceFingerprint: {
          screenResolution: { width: screenWidth, height: screenHeight },
          colorDepth: colorDepth,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          platform: navigator.platform,
          userAgent: navigator.userAgent
        },
        interactions: {
          mouse: {
            movementEntropy: 4.2,
            velocityStats: { mean: 12.5, stddev: 3.2, max: 45.0 },
            totalMovements: 150
          },
          keyboard: {
            typingSpeed: 45,
            errorRate: 0.02,
            keystrokeEntropy: 3.5
          }
        },
        headlessIndicators: {
          isHeadless: false,
          indicators: []
        },
        eventLoopJitter: 3.2
      };

      setTelemetry(telemetryData);
      setLoading(false);

      document.removeEventListener('mousemove', handleMouseMove);
    };

    simulateInit();
  }, []);

  const sendToBackend = async () => {
    if (!telemetry) return;

    setSending(true);
    try {
      const payload = {
        telemetry: {
          device: telemetry.deviceFingerprint,
          mouse: telemetry.interactions?.mouse || {},
          keyboard: telemetry.interactions?.keyboard || {},
          timing: {
            event_loop_jitter: telemetry.eventLoopJitter,
            headless_indicators: telemetry.headlessIndicators,
            total_interaction_time_ms: Date.now() - sessionStartedAtRef.current
          }
        },
        session_id: 'demo-session-' + Date.now()
      };

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result: RiskResult = await response.json();
      setRiskResult(result);

      console.log('Risk assessment result:', result);
    } catch (error) {
      console.error('Backend communication error:', error);
      alert('Failed to send telemetry to backend.\n\nError: ' + error);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔐 UIDAI Passive Bot Detection System</h1>
        <p>Behavioral analysis for seamless user verification</p>
      </header>

      <main className="App-main">
        {loading ? (
          <div className="status loading">
            <p>⏳ Initializing telemetry collector...</p>
            <p>Please move your mouse and type to generate behavioral signals</p>
            <p>Current Mouse Position: ({mouseX}, {mouseY})</p>
          </div>
        ) : telemetry ? (
          <div className="content">
            <section className="telemetry-section">
              <h2>📊 Collected Telemetry</h2>

              <div className="info-grid">
                <div className="info-card">
                  <h3>Device Fingerprint</h3>
                  <p><strong>Screen:</strong> {telemetry.deviceFingerprint?.screenResolution?.width}x{telemetry.deviceFingerprint?.screenResolution?.height}</p>
                  <p><strong>Color Depth:</strong> {telemetry.deviceFingerprint?.colorDepth}-bit</p>
                  <p><strong>Timezone:</strong> {telemetry.deviceFingerprint?.timezone}</p>
                  <p><strong>Platform:</strong> {telemetry.deviceFingerprint?.platform}</p>
                </div>

                <div className="info-card">
                  <h3>Mouse Behavior</h3>
                  {telemetry.interactions?.mouse ? (
                    <>
                      <p><strong>Entropy:</strong> {telemetry.interactions.mouse.movementEntropy?.toFixed(2)}</p>
                      <p><strong>Avg Velocity:</strong> {telemetry.interactions.mouse.velocityStats?.mean?.toFixed(2)} px/ms</p>
                      <p><strong>Total Movements:</strong> {telemetry.interactions.mouse.totalMovements}</p>
                    </>
                  ) : (
                    <p>No mouse movements detected</p>
                  )}
                </div>

                <div className="info-card">
                  <h3>Keyboard Behavior</h3>
                  {telemetry.interactions?.keyboard ? (
                    <>
                      <p><strong>Typing Speed:</strong> {telemetry.interactions.keyboard.typingSpeed?.toFixed(0)} WPM</p>
                      <p><strong>Error Rate:</strong> {(telemetry.interactions.keyboard.errorRate * 100)?.toFixed(1)}%</p>
                      <p><strong>Keystroke Entropy:</strong> {telemetry.interactions.keyboard.keystrokeEntropy?.toFixed(2)}</p>
                    </>
                  ) : (
                    <p>No keystrokes detected</p>
                  )}
                </div>

                <div className="info-card">
                  <h3>Security Checks</h3>
                  <p><strong>Headless Detected:</strong> {telemetry.headlessIndicators?.isHeadless ? '⚠️ Yes' : '✅ No'}</p>
                  <p><strong>Event Loop Jitter:</strong> {telemetry.eventLoopJitter?.toFixed(2)}ms</p>
                </div>
              </div>

              <button
                onClick={sendToBackend}
                disabled={sending}
                className="send-button"
              >
                {sending ? '⏳ Sending to Backend...' : '📤 Analyze with ML Model'}
              </button>
            </section>

            {riskResult && (
              <section className="result-section">
                <h2>🎯 Risk Assessment Result</h2>

                <div className={`risk-card risk-${riskResult.risk_score < 33 ? 'low' : riskResult.risk_score < 67 ? 'medium' : 'high'}`}>
                  <h3>Risk Score: {riskResult.risk_score}/100</h3>

                  <p><strong>Bot Probability:</strong> {(riskResult.bot_probability * 100).toFixed(1)}%</p>
                  <p><strong>Recommended Action:</strong> <span className="action">{riskResult.recommended_action}</span></p>
                  <p><strong>Inference Latency:</strong> {riskResult.latency_ms}ms</p>
                  <p><strong>Reasoning:</strong> {riskResult.reasoning}</p>

                  {riskResult.risk_score < 30 && (
                    <div className="status-low">✅ Low Risk - Access Allowed</div>
                  )}
                  {riskResult.risk_score >= 30 && riskResult.risk_score < 60 && (
                    <div className="status-medium">⚠️ Medium Risk - Soft Challenge Recommended</div>
                  )}
                  {riskResult.risk_score >= 60 && (
                    <div className="status-high">🚫 High Risk - Escalation Required</div>
                  )}
                </div>
              </section>
            )}

            <section className="raw-data-section">
              <h2>🔍 Raw Telemetry Data</h2>
              <pre className="code-block">
                {JSON.stringify(telemetry, null, 2)}
              </pre>
            </section>
          </div>
        ) : (
          <div className="status error">
            <p>❌ Failed to initialize telemetry</p>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Backend Status: <a href={`${API_BASE_URL}/health`} target="_blank" rel="noreferrer">Check Health</a></p>
      </footer>
    </div>
  );
};

export default App;