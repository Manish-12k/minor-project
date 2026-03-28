/**
 * Telemetry Collector
 * Captures device fingerprint and environmental signals
 */

export class TelemetryCollector {
  captureDeviceFingerprint() {
    return {
      screenResolution: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
      colorDepth: typeof window !== 'undefined' && window.screen
        ? (window.screen as Screen).colorDepth || 24
        : 24,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      platform: navigator.platform,
      userAgent: navigator.userAgent,
      language: navigator.language,
      hardwareConcurrency: (navigator as any).hardwareConcurrency || 1,
      deviceMemory: (navigator as any).deviceMemory || 'unknown',
      maxTouchPoints: navigator.maxTouchPoints || 0,
    };
  }

  captureNetworkInfo() {
    const connection = (navigator as any).connection || (navigator as any).mozConnection;
    if (!connection) {
      return {
        effectiveType: 'unknown',
        downlink: 0,
        rtt: 0,
      };
    }

    return {
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
    };
  }

  captureBrowserInfo() {
    return {
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack,
      onLine: navigator.onLine,
      plugins: Array.from(navigator.plugins).map(p => p.name),
    };
  }
}