import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';
import App from './App';
import { db, LogEntry, Config } from './services/databaseService';

const AdminDashboard: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('telemetry');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [config, setConfig] = useState<Config>({
    botDetectionThreshold: 60,
    softChallengeThreshold: 30,
    maxLoginAttempts: 3,
    modelUpdateInterval: 24
  });
  const [logsLoading, setLogsLoading] = useState(false);
  const [configSaved, setConfigSaved] = useState(false);

  // Initialize database and load data
  useEffect(() => {
    const initDB = async () => {
      await db.init();

      // Load initial logs
      const initialLogs = await db.getLogs(50);
      setLogs(initialLogs);

      // Load config
      const savedConfig = await db.getConfig();
      setConfig(savedConfig);

      // Log that admin accessed dashboard
      await db.logInfo('Admin dashboard accessed');
    };

    initDB();
  }, []);

  // Refresh logs when tab changes to logs
  useEffect(() => {
    if (currentTab === 'logs') {
      refreshLogs();
    }
  }, [currentTab]);

  const refreshLogs = async () => {
    setLogsLoading(true);
    try {
      const updatedLogs = await db.getLogs(50);
      setLogs(updatedLogs);
    } catch (error) {
      console.error('Error loading logs:', error);
    } finally {
      setLogsLoading(false);
    }
  };

  const handleConfigChange = (field: keyof Config, value: number) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveConfig = async () => {
    try {
      await db.saveConfig(config);
      setConfigSaved(true);
      await db.logInfo(`Configuration updated: Bot threshold=${config.botDetectionThreshold}, Max attempts=${config.maxLoginAttempts}`);
      setTimeout(() => setConfigSaved(false), 3000);
    } catch (error) {
      console.error('Error saving config:', error);
    }
  };

  const clearLogs = async () => {
    if (window.confirm('Are you sure you want to delete all logs?')) {
      try {
        await db.clearLogs();
        setLogs([]);
        console.log('Logs cleared');
      } catch (error) {
        console.error('Error clearing logs:', error);
      }
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>🛡️ Admin Dashboard - Bot Detection System</h1>
        <button className="logout-btn" onClick={() => window.close()}>
          Logout
        </button>
      </header>

      <main className="admin-main">
        <div className="admin-sidebar">
          <nav className="admin-nav">
            <button
              className={`nav-btn ${currentTab === 'telemetry' ? 'active' : ''}`}
              onClick={() => setCurrentTab('telemetry')}
            >
              📊 Telemetry Viewer
            </button>
            <button
              className={`nav-btn ${currentTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setCurrentTab('analytics')}
            >
              📈 Analytics
            </button>
            <button
              className={`nav-btn ${currentTab === 'config' ? 'active' : ''}`}
              onClick={() => setCurrentTab('config')}
            >
              ⚙️ Configuration
            </button>
            <button
              className={`nav-btn ${currentTab === 'logs' ? 'active' : ''}`}
              onClick={() => setCurrentTab('logs')}
            >
              🔍 System Logs
            </button>
          </nav>
        </div>

        <div className="admin-content">
          {/* Telemetry Viewer Tab */}
          {currentTab === 'telemetry' && (
            <div className="admin-section">
              <h2>📊 Current Telemetry Viewer</h2>
              <p className="section-desc">View real-time behavioral signals and bot detection analysis</p>

              <div className="telemetry-viewer">
                <App />
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {currentTab === 'analytics' && (
            <div className="admin-section">
              <h2>📈 Analytics Dashboard</h2>
              <p className="section-desc">View bot detection statistics and trends</p>

              <div className="analytics-content">
                <div className="stat-card">
                  <h3>Total Sessions</h3>
                  <p className="stat-number">{logs.length}</p>
                  <p className="stat-change">↑ Real-time data</p>
                </div>

                <div className="stat-card">
                  <h3>Humans Detected</h3>
                  <p className="stat-number">
                    {logs.filter(l => l.level === 'SUCCESS').length}
                  </p>
                  <p className="stat-change">
                    {logs.length > 0
                      ? ((logs.filter(l => l.level === 'SUCCESS').length / logs.length) * 100).toFixed(1)
                      : 0}%
                  </p>
                </div>

                <div className="stat-card">
                  <h3>Bots Blocked</h3>
                  <p className="stat-number">
                    {logs.filter(l => l.level === 'WARNING').length}
                  </p>
                  <p className="stat-change">
                    {logs.length > 0
                      ? ((logs.filter(l => l.level === 'WARNING').length / logs.length) * 100).toFixed(1)
                      : 0}%
                  </p>
                </div>

                <div className="stat-card">
                  <h3>Avg Risk Score</h3>
                  <p className="stat-number">
                    {logs.length > 0
                      ? (logs.reduce((sum, l) => sum + (l.riskScore || 0), 0) / logs.length).toFixed(0)
                      : 0}
                  </p>
                  <p className="stat-change">✅ Low Risk</p>
                </div>
              </div>

              <div className="chart-placeholder">
                <p>📊 Risk Score Distribution</p>
                <div className="chart-bar">
                  <div className="bar low" style={{
                    height: logs.length > 0
                      ? ((logs.filter(l => l.level === 'SUCCESS').length / logs.length) * 100) + '%'
                      : '0%'
                  }}></div>
                  <div className="bar medium" style={{height: '20%'}}></div>
                  <div className="bar high" style={{
                    height: logs.length > 0
                      ? ((logs.filter(l => l.level === 'WARNING').length / logs.length) * 100) + '%'
                      : '0%'
                  }}></div>
                </div>
              </div>
            </div>
          )}

          {/* Configuration Tab */}
          {currentTab === 'config' && (
            <div className="admin-section">
              <h2>⚙️ Configuration Settings</h2>
              <p className="section-desc">Manage system configuration and thresholds</p>

              {configSaved && (
                <div className="alert alert-success">
                  ✅ Configuration saved successfully!
                </div>
              )}

              <div className="config-form">
                <div className="config-group">
                  <label>Bot Detection Threshold (Risk Score): {config.botDetectionThreshold}</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.botDetectionThreshold}
                    onChange={(e) => handleConfigChange('botDetectionThreshold', parseInt(e.target.value))}
                    className="slider"
                  />
                  <p className="config-hint">Scores above {config.botDetectionThreshold} are flagged as bots</p>
                </div>

                <div className="config-group">
                  <label>Soft Challenge Threshold: {config.softChallengeThreshold}</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.softChallengeThreshold}
                    onChange={(e) => handleConfigChange('softChallengeThreshold', parseInt(e.target.value))}
                    className="slider"
                  />
                  <p className="config-hint">Scores between {config.softChallengeThreshold}-{config.botDetectionThreshold} trigger CAPTCHA</p>
                </div>

                <div className="config-group">
                  <label>Max Login Attempts: {config.maxLoginAttempts}</label>
                  <input
                    type="number"
                    value={config.maxLoginAttempts}
                    onChange={(e) => handleConfigChange('maxLoginAttempts', parseInt(e.target.value))}
                    min="1"
                    max="10"
                    className="config-input"
                  />
                  <p className="config-hint">Failed attempts before account lockout</p>
                </div>

                <div className="config-group">
                  <label>Model Update Interval (hours): {config.modelUpdateInterval}</label>
                  <input
                    type="number"
                    value={config.modelUpdateInterval}
                    onChange={(e) => handleConfigChange('modelUpdateInterval', parseInt(e.target.value))}
                    min="1"
                    max="168"
                    className="config-input"
                  />
                  <p className="config-hint">How often the ML model is retrained</p>
                </div>

                <div className="config-buttons">
                  <button className="save-config-btn" onClick={saveConfig}>
                    💾 Save Configuration
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* System Logs Tab */}
          {currentTab === 'logs' && (
            <div className="admin-section">
              <h2>🔍 System Logs</h2>
              <p className="section-desc">View all system events and activities</p>

              <div className="logs-header">
                <button className="refresh-btn" onClick={refreshLogs} disabled={logsLoading}>
                  {logsLoading ? '⏳ Refreshing...' : '🔄 Refresh'}
                </button>
                <button className="clear-logs-btn" onClick={clearLogs}>
                  🗑️ Clear All Logs
                </button>
                <span className="log-count">Total: {logs.length} entries</span>
              </div>

              <div className="logs-container">
                {logs.length === 0 ? (
                  <p className="no-logs">No logs available. Activity will appear here.</p>
                ) : (
                  logs.map((log) => (
                    <div key={log.id} className={`log-entry log-${log.level.toLowerCase()}`}>
                      <span className="log-time">{log.time}</span>
                      <span className="log-level">{log.level}</span>
                      <span className="log-message">{log.message}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;