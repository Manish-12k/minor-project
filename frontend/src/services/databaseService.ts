/**
 * Database Service - Manages logs and configuration
 * Uses IndexedDB for client-side storage (no server needed for demo)
 */

export interface LogEntry {
  id?: number;
  timestamp: string;
  time: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG' | 'SUCCESS';
  message: string;
  sessionId?: string;
  riskScore?: number;
  userId?: string;
}

export interface Config {
  botDetectionThreshold: number;
  softChallengeThreshold: number;
  maxLoginAttempts: number;
  modelUpdateInterval: number;
}

const DB_NAME = 'UIDaiBotDetection';
const LOGS_STORE = 'logs';
const CONFIG_STORE = 'config';

export class DatabaseService {
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        console.log('Database initialized');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create logs store
        if (!db.objectStoreNames.contains(LOGS_STORE)) {
          const logsStore = db.createObjectStore(LOGS_STORE, {
            keyPath: 'id',
            autoIncrement: true
          });
          logsStore.createIndex('timestamp', 'timestamp', { unique: false });
          logsStore.createIndex('level', 'level', { unique: false });
          logsStore.createIndex('sessionId', 'sessionId', { unique: false });
        }

        // Create config store
        if (!db.objectStoreNames.contains(CONFIG_STORE)) {
          db.createObjectStore(CONFIG_STORE, { keyPath: 'id' });
        }
      };
    });
  }

  async addLog(logEntry: Omit<LogEntry, 'id'>): Promise<number> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([LOGS_STORE], 'readwrite');
      const store = transaction.objectStore(LOGS_STORE);
      const request = store.add(logEntry);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        console.log('Log added:', logEntry);
        resolve(request.result as number);
      };
    });
  }

  async getLogs(limit: number = 50): Promise<LogEntry[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([LOGS_STORE], 'readonly');
      const store = transaction.objectStore(LOGS_STORE);
      const index = store.index('timestamp');
      const request = index.openCursor(null, 'prev');

      const logs: LogEntry[] = [];
      let count = 0;

      request.onerror = () => reject(request.error);
      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;

        if (cursor && count < limit) {
          logs.push(cursor.value);
          count++;
          cursor.continue();
        } else {
          resolve(logs);
        }
      };
    });
  }

  async getLogsByLevel(level: string): Promise<LogEntry[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([LOGS_STORE], 'readonly');
      const store = transaction.objectStore(LOGS_STORE);
      const index = store.index('level');
      const request = index.getAll(level);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const allLogs = request.result as LogEntry[];
        resolve(allLogs.reverse().slice(0, 50));
      };
    });
  }

  async clearLogs(): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([LOGS_STORE], 'readwrite');
      const store = transaction.objectStore(LOGS_STORE);
      const request = store.clear();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        console.log('All logs cleared');
        resolve();
      };
    });
  }

  async saveConfig(config: Config): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([CONFIG_STORE], 'readwrite');
      const store = transaction.objectStore(CONFIG_STORE);
      const request = store.put({ id: 'main', ...config });

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        console.log('Configuration saved:', config);
        resolve();
      };
    });
  }

  async getConfig(): Promise<Config> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([CONFIG_STORE], 'readonly');
      const store = transaction.objectStore(CONFIG_STORE);
      const request = store.get('main');

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const result = request.result;
        if (result) {
          resolve({
            botDetectionThreshold: result.botDetectionThreshold,
            softChallengeThreshold: result.softChallengeThreshold,
            maxLoginAttempts: result.maxLoginAttempts,
            modelUpdateInterval: result.modelUpdateInterval
          });
        } else {
          // Default config
          const defaultConfig: Config = {
            botDetectionThreshold: 60,
            softChallengeThreshold: 30,
            maxLoginAttempts: 3,
            modelUpdateInterval: 24
          };
          resolve(defaultConfig);
        }
      };
    });
  }

  async logBotDetection(
    userId: string,
    riskScore: number,
    isBot: boolean,
    timestamp?: string
  ): Promise<void> {
    const now = new Date();
    const logEntry: Omit<LogEntry, 'id'> = {
      timestamp: timestamp || now.toISOString(),
      time: now.toLocaleTimeString(),
      level: isBot ? 'WARNING' : 'SUCCESS',
      message: isBot
        ? `Bot detected from user ${userId} (Risk: ${riskScore}/100)`
        : `User ${userId} passed bot detection (Risk: ${riskScore}/100)`,
      userId,
      riskScore
    };

    await this.addLog(logEntry);
  }

  async logError(message: string): Promise<void> {
    const now = new Date();
    const logEntry: Omit<LogEntry, 'id'> = {
      timestamp: now.toISOString(),
      time: now.toLocaleTimeString(),
      level: 'ERROR',
      message
    };

    await this.addLog(logEntry);
  }

  async logInfo(message: string): Promise<void> {
    const now = new Date();
    const logEntry: Omit<LogEntry, 'id'> = {
      timestamp: now.toISOString(),
      time: now.toLocaleTimeString(),
      level: 'INFO',
      message
    };

    await this.addLog(logEntry);
  }
}

export const db = new DatabaseService();