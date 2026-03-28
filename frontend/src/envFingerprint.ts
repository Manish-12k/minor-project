/**
 * Environment Fingerprint
 * Detects headless browsers and bot-like behaviors
 */

export class EnvironmentFingerprint {
  static detectHeadlessIndicators() {
    const indicators: string[] = [];

    // Check for headless browser indicators
    if ((navigator as any).webdriver) {
      indicators.push('webdriver_property');
    }

    if (!window.chrome && !window.safari) {
      indicators.push('missing_chrome_safari');
    }

    if ((navigator as any).permissions?.query) {
      (navigator as any).permissions
        .query({ name: 'notifications' })
        .then((result: any) => {
          if (Notification.permission === 'denied' && result.state === 'prompt') {
            indicators.push('permissions_mismatch');
          }
        })
        .catch(() => {});
    }

    if (
      !('ontouchstart' in window) &&
      !('onmousedown' in window) &&
      navigator.maxTouchPoints === 0
    ) {
      indicators.push('no_touch_support');
    }

    // Check for phantom.js
    if ((window as any).callPhantom || (window as any)._phantom) {
      indicators.push('phantomjs_detected');
    }

    // Check for headless Chrome
    if (/HeadlessChrome/.test(navigator.userAgent)) {
      indicators.push('headless_chrome');
    }

    return {
      isHeadless: indicators.length > 0,
      indicators,
      timestamp: new Date().toISOString(),
    };
  }

  static measureEventLoopJitter(): Promise<number> {
    return new Promise((resolve) => {
      const measurements: number[] = [];
      let count = 0;

      const measure = () => {
        const start = performance.now();

        setTimeout(() => {
          const latency = performance.now() - start;
          measurements.push(latency);
          count++;

          if (count < 10) {
            measure();
          } else {
            // Calculate jitter (standard deviation)
            const mean =
              measurements.reduce((a, b) => a + b, 0) / measurements.length;
            const variance =
              measurements.reduce((a, b) => a + (b - mean) ** 2, 0) /
              measurements.length;
            const jitter = Math.sqrt(variance);

            resolve(jitter);
          }
        }, 0);
      };

      measure();
    });
  }

  static checkForFrameworkDetection() {
    const detections: string[] = [];

    // Check for Selenium
    if ((window as any).document.$cdc_asdjflasutopfhvcn5345a ||
        (window as any).__webdriverResource ||
        (window as any).__nightmare) {
      detections.push('selenium_detected');
    }

    // Check for Protractor
    if ((window as any).angular) {
      detections.push('protractor_detected');
    }

    return detections;
  }

  static getFullFingerprint() {
    return {
      headlessIndicators: this.detectHeadlessIndicators(),
      frameworkDetections: this.checkForFrameworkDetection(),
      userAgent: navigator.userAgent,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      timestamp: Date.now(),
    };
  }
}

// Augment window type
declare global {
  interface Window {
    chrome?: any;
    safari?: any;
    callPhantom?: any;
    _phantom?: any;
  }
}