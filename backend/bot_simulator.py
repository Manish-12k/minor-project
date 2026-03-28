"""
Bot Simulator - Tests passive bot detection system
Simulates various bot behaviors and sends requests to the detection API
"""

import requests
import json
import time
import random
from typing import Dict, Any


class BotSimulator:
    """Simulates different types of bots trying to bypass detection"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session_counter = 0

    def get_session_id(self) -> str:
        """Generate unique session ID"""
        self.session_counter += 1
        return f"bot-session-{self.session_counter}"

    # ===== BOT BEHAVIOR TYPES =====

    def aggressive_bot_telemetry(self) -> Dict[str, Any]:
        """
        Aggressive bot behavior:
        - Fast, linear mouse movement
        - Extremely fast typing
        - Very low entropy
        - Minimal interaction time
        """
        return {
            "device": {
                "screenResolution": {"width": 1920, "height": 1080},
                "colorDepth": 24,
                "timezone": "UTC",
                "platform": "Linux",
                "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "language": "en-US",
                "hardwareConcurrency": 4,
                "deviceMemory": "unknown",
                "maxTouchPoints": 0
            },
            "mouse": {
                "movementEntropy": 0.2,  # Very low entropy = bot-like
                "velocityStats": {
                    "mean": 500,  # Insanely fast
                    "stddev": 0.1,  # No variation = bot
                    "max": 600
                },
                "totalMovements": 5  # Very few movements
            },
            "keyboard": {
                "typingSpeed": 500,  # Inhuman speed (500 WPM!)
                "keystrokeEntropy": 0.1,  # No variation
                "errorRate": 0.0  # Perfect accuracy = bot
            },
            "timing": {
                "event_loop_jitter": 0.0  # No jitter = headless
            }
        }

    def moderate_bot_telemetry(self) -> Dict[str, Any]:
        """
        Moderate bot behavior:
        - Slightly varied mouse movement
        - Fast but not inhuman typing
        - Low-medium entropy
        - Quick interaction time
        """
        return {
            "device": {
                "screenResolution": {"width": 1366, "height": 768},
                "colorDepth": 24,
                "timezone": "Asia/Kolkata",
                "platform": "Win32",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "language": "en-US",
                "hardwareConcurrency": 8,
                "deviceMemory": "unknown",
                "maxTouchPoints": 0
            },
            "mouse": {
                "movementEntropy": 1.5,  # Low entropy
                "velocityStats": {
                    "mean": 150,  # Fast but possible
                    "stddev": 20,  # Some variation
                    "max": 250
                },
                "totalMovements": 30  # Fewer than human
            },
            "keyboard": {
                "typingSpeed": 150,  # Very fast (150 WPM)
                "keystrokeEntropy": 0.8,  # Low variation
                "errorRate": 0.0  # No errors
            },
            "timing": {
                "event_loop_jitter": 0.5  # Minimal jitter
            }
        }

    def stealth_bot_telemetry(self) -> Dict[str, Any]:
        """
        Stealth bot behavior:
        - Tries to mimic human patterns
        - Medium entropy
        - Medium typing speed
        - But still shows subtle bot signs
        """
        return {
            "device": {
                "screenResolution": {"width": 1920, "height": 1080},
                "colorDepth": 32,
                "timezone": "Asia/Kolkata",
                "platform": "Win32",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
                "language": "en-IN",
                "hardwareConcurrency": 16,
                "deviceMemory": "8",
                "maxTouchPoints": 0
            },
            "mouse": {
                "movementEntropy": 2.8,  # Medium entropy (trying to mimic human)
                "velocityStats": {
                    "mean": 25,  # Reasonable speed
                    "stddev": 8,  # Some variation (trying to be human)
                    "max": 80
                },
                "totalMovements": 80  # Decent amount of movement
            },
            "keyboard": {
                "typingSpeed": 65,  # Reasonable speed
                "keystrokeEntropy": 1.5,  # Some variation
                "errorRate": 0.01  # Few errors (trying to be human)
            },
            "timing": {
                "event_loop_jitter": 2.0  # Some jitter
            }
        }

    def human_telemetry(self) -> Dict[str, Any]:
        """
        Real human behavior:
        - Varied mouse movement
        - Natural typing speed
        - High entropy
        - Longer interaction time
        """
        return {
            "device": {
                "screenResolution": {"width": 1920, "height": 1080},
                "colorDepth": 32,
                "timezone": "Asia/Kolkata",
                "platform": "Win32",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
                "language": "en-IN",
                "hardwareConcurrency": 8,
                "deviceMemory": "8",
                "maxTouchPoints": 10  # Touch-enabled device
            },
            "mouse": {
                "movementEntropy": 4.2,  # High entropy = human
                "velocityStats": {
                    "mean": 12.5,  # Natural speed
                    "stddev": 3.2,  # Good variation
                    "max": 45
                },
                "totalMovements": 150  # Lots of movement
            },
            "keyboard": {
                "typingSpeed": 45,  # Normal typing speed
                "keystrokeEntropy": 3.5,  # Good variation in timing
                "errorRate": 0.02  # Few typos
            },
            "timing": {
                "event_loop_jitter": 3.2  # Natural jitter
            }
        }

    # ===== TEST METHODS =====

    def check_api_health(self) -> bool:
        """Check if backend API is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend API is running!")
                return True
            else:
                print(f"❌ Backend API returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {self.api_url}")
            print("   Make sure Flask server is running: python -m ml_engine.inference.server")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_bot(self, bot_type: str, name: str) -> Dict[str, Any]:
        """
        Test a specific bot type

        Args:
            bot_type: 'aggressive', 'moderate', 'stealth', 'human'
            name: Display name for the test

        Returns:
            API response with risk assessment
        """
        print(f"\n{'=' * 60}")
        print(f"🤖 Testing: {name}")
        print(f"{'=' * 60}")

        # Select telemetry based on bot type
        if bot_type == 'aggressive':
            telemetry = self.aggressive_bot_telemetry()
        elif bot_type == 'moderate':
            telemetry = self.moderate_bot_telemetry()
        elif bot_type == 'stealth':
            telemetry = self.stealth_bot_telemetry()
        elif bot_type == 'human':
            telemetry = self.human_telemetry()
        else:
            print(f"Unknown bot type: {bot_type}")
            return {}

        # Prepare payload
        payload = {
            "telemetry": telemetry,
            "session_id": self.get_session_id()
        }

        # Send request
        try:
            print(f"📤 Sending telemetry to {self.api_url}/api/predict...")
            start_time = time.time()

            response = requests.post(
                f"{self.api_url}/api/predict",
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )

            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response received in {latency:.1f}ms")

                # Display results
                risk_score = result.get('risk_score', 0)
                bot_prob = result.get('bot_probability', 0)
                action = result.get('recommended_action', 'UNKNOWN')

                print(f"\n📊 RESULTS:")
                print(f"   Risk Score: {risk_score}/100")
                print(f"   Bot Probability: {bot_prob * 100:.1f}%")
                print(f"   Recommended Action: {action}")

                # Verdict
                if risk_score < 30:
                    print(f"\n✅ VERDICT: HUMAN - Allowed to proceed")
                elif risk_score < 60:
                    print(f"\n⚠️  VERDICT: SUSPICIOUS - Soft challenge (CAPTCHA)")
                else:
                    print(f"\n🚫 VERDICT: BOT DETECTED - Blocked")

                return result
            else:
                print(f"❌ API returned {response.status_code}: {response.text}")
                return {}

        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - API is not responding")
            return {}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def run_all_tests(self):
        """Run all bot detection tests"""
        print("\n" + "=" * 60)
        print("🤖 BOT DETECTION SYSTEM TESTER")
        print("=" * 60)

        # Check API
        if not self.check_api_health():
            print("\n❌ Cannot proceed - backend API is not running")
            print("\nTo start the backend, run in another terminal:")
            print("   cd backend")
            print("   python -m ml_engine.inference.server")
            return

        # Run tests
        results = []

        # Test 1: Aggressive Bot
        result = self.test_bot('aggressive', '🚫 AGGRESSIVE BOT (should be BLOCKED)')
        results.append(('Aggressive Bot', result))
        time.sleep(1)

        # Test 2: Moderate Bot
        result = self.test_bot('moderate', '⚠️  MODERATE BOT (should be CHALLENGED)')
        results.append(('Moderate Bot', result))
        time.sleep(1)

        # Test 3: Stealth Bot
        result = self.test_bot('stealth', '⚠️  STEALTH BOT (might be allowed or challenged)')
        results.append(('Stealth Bot', result))
        time.sleep(1)

        # Test 4: Real Human
        result = self.test_bot('human', '✅ REAL HUMAN (should be ALLOWED)')
        results.append(('Real Human', result))

        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)

        for name, result in results:
            if result:
                risk = result.get('risk_score', 0)
                action = result.get('recommended_action', 'UNKNOWN')
                status = "✅ PASS" if self.is_correct_verdict(name, risk) else "❌ FAIL"
                print(f"{status} | {name:20} | Risk: {risk:3}/100 | Action: {action}")
            else:
                print(f"❌ FAIL | {name:20} | No response")

        print("=" * 60)
        print("\n✨ Testing complete!")

    def is_correct_verdict(self, bot_type: str, risk_score: int) -> bool:
        """Check if verdict matches expected behavior"""
        if 'Aggressive' in bot_type:
            return risk_score > 60  # Should be blocked
        elif 'Moderate' in bot_type:
            return 30 <= risk_score <= 70  # Should be challenged
        elif 'Stealth' in bot_type:
            return risk_score > 40  # Should be at least challenged
        elif 'Real Human' in bot_type:
            return risk_score < 40  # Should be allowed
        return False


def main():
    """Main entry point"""
    simulator = BotSimulator()

    # Run all tests
    simulator.run_all_tests()

    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("=" * 60)
    print("1. Check frontend at http://localhost:3000")
    print("2. Try logging in as real user (should pass)")
    print("3. Try admin access with Aadhar: 37775631, CAPTCHA: G8")
    print("4. View logs in admin dashboard to see bot detection results")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()