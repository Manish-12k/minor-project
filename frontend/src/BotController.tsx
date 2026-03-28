import React, { useState } from 'react';
import './BotController.css';

interface BotControllerProps {
  visible?: boolean;
}

const BotController: React.FC<BotControllerProps> = ({ visible = true }) => {
  const [botRunning, setBotRunning] = useState(false);
  const [botType, setBotType] = useState('aggressive');
  const [logs, setLogs] = useState<string[]>([]);

  const runBot = (type: string) => {
    if (botRunning) return;

    setBotType(type);
    setBotRunning(true);
    setLogs([`🤖 Starting ${type} bot...`]);

    // Call bot from window
    (window as any).runBot?.(type);

    // Stop after expected time
    const times: { [key: string]: number } = {
      aggressive: 2000,
      moderate: 4000,
      stealth: 10000,
      human: 18000
    };

    setTimeout(() => {
      setBotRunning(false);
    }, times[type] || 5000);
  };

  if (!visible) return null;

  return (
    <div className="bot-controller">
      <div className="bot-panel">
        <h3>🤖 Bot Controller (Testing Only)</h3>

        <div className="bot-buttons">
          <button
            className="bot-btn aggressive"
            onClick={() => runBot('aggressive')}
            disabled={botRunning}
            title="Fast bot - 1 second (85% chance of being blocked)"
          >
            ⚡ Aggressive Bot
          </button>

          <button
            className="bot-btn moderate"
            onClick={() => runBot('moderate')}
            disabled={botRunning}
            title="Medium speed - 3 seconds (will be challenged)"
          >
            ⚠️ Moderate Bot
          </button>

          <button
            className="bot-btn stealth"
            onClick={() => runBot('stealth')}
            disabled={botRunning}
            title="Slow bot - 8 seconds (tries to mimic human)"
          >
            👻 Stealth Bot
          </button>

          <button
            className="bot-btn human"
            onClick={() => runBot('human')}
            disabled={botRunning}
            title="Human-like - 15 seconds"
          >
            👤 Human Mimic
          </button>
        </div>

        <div className="bot-status">
          {botRunning && (
            <>
              <div className="status-indicator">
                <span className="dot"></span>
                <span>Bot running: {botType}</span>
              </div>
              <p className="instructions">
                Watch the form being filled automatically. Our passive detection system will analyze the behavior.
              </p>
            </>
          )}
          {!botRunning && (
            <p className="info">Click a button above to run a bot. The form will auto-fill with bot behavior patterns.</p>
          )}
        </div>

        <p className="disclaimer">
          ℹ️ For testing only. The passive bot detection system analyzes typing speed, mouse movement, and interaction timing to determine if a user is human or bot.
        </p>
      </div>
    </div>
  );
};

export default BotController;