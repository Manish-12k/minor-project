"""
UIDAI Bot Detection - Backend API Server
Flask REST API for passive bot detection with XGBoost model
"""

import os
import sys
import json
import pickle
import logging
import traceback
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Resolve backend/build for serving React
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
REACT_BUILD_DIR = os.path.join(BACKEND_DIR, 'build')

# Initialize Flask (optionally serves React build)
app = Flask(__name__, static_folder=REACT_BUILD_DIR, static_url_path='')
CORS(app)

# Global model and scaler
model = None
scaler = None

# Global config
config = None

def load_config():
    """Load configuration from config.json"""
    global config
    config_path = os.path.join(BACKEND_DIR, 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"✅ Config loaded from {config_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading config: {e}")
        # Default config
        config = {
            "botDetectionThreshold": 60,
            "softChallengeThreshold": 30,
            "maxLoginAttempts": 3,
            "modelUpdateInterval": 24
        }
        return False

def load_model_and_scaler():
    """Load the trained XGBoost model and scaler"""
    global model, scaler

    logger.info("=" * 70)
    logger.info("Loading ML Model and Scaler...")
    logger.info("=" * 70)

    try:
        # Get absolute path to models directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        models_dir = os.path.join(project_root, 'backend', 'ml_engine', 'models')

        model_path = os.path.join(models_dir, 'xgboost_bot_detector_latest.pkl')
        scaler_path = os.path.join(models_dir, 'scaler_latest.pkl')

        logger.info(f"Model path: {model_path}")
        logger.info(f"Scaler path: {scaler_path}")

        # Load model
        if not os.path.exists(model_path):
            logger.error(f"❌ Model file not found: {model_path}")
            return False

        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✅ Model loaded successfully: {type(model).__name__}")

        # Load scaler
        if not os.path.exists(scaler_path):
            logger.error(f"❌ Scaler file not found: {scaler_path}")
            return False

        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        logger.info(f"✅ Scaler loaded successfully: {type(scaler).__name__}")

        logger.info("=" * 70)
        logger.info("✅ Models loaded successfully!")
        logger.info("=" * 70)

        # Load config
        load_config()

        return True

    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        logger.error(traceback.format_exc())
        return False

def predict_risk(telemetry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict bot risk from telemetry data

    Returns risk score (0-100) and recommended action
    """
    global model, scaler

    try:
        # Extract telemetry data
        mouse_data = telemetry.get('mouse', {}) or {}
        keyboard_data = telemetry.get('keyboard', {}) or {}
        timing_data = telemetry.get('timing', {}) or {}
        device_data = telemetry.get('device', {}) or {}

        headless_info = timing_data.get('headless_indicators') or {}
        headless_detected = 1.0 if headless_info.get('isHeadless') else 0.0

        interaction_ms = timing_data.get('total_interaction_time_ms')
        if interaction_ms is None:
            interaction_ms = device_data.get('total_interaction_time_ms', 0)
        interaction_ms = float(interaction_ms or 0)

        # Build feature vector (11 features) — order must match ml_engine/retrain/pipeline.py
        features = np.array([[
            mouse_data.get('movementEntropy', 0),                           # 0
            mouse_data.get('velocityStats', {}).get('mean', 0),             # 1
            mouse_data.get('velocityStats', {}).get('stddev', 0),           # 2
            mouse_data.get('velocityStats', {}).get('max', 0),              # 3
            mouse_data.get('totalMovements', 0),                            # 4
            keyboard_data.get('typingSpeed', 0),                            # 5
            keyboard_data.get('keystrokeEntropy', 0),                       # 6
            keyboard_data.get('errorRate', 0),                              # 7
            timing_data.get('event_loop_jitter', 0),                        # 8
            headless_detected,                                              # 9
            interaction_ms                                                  # 10
        ]])

        logger.info(f"Features extracted: {features}")

        # Check if model is loaded
        if model is None or scaler is None:
            logger.warning("⚠️ Model or scaler not loaded - returning default")
            return {
                'risk_score': 30,
                'bot_probability': 0.30,
                'recommended_action': 'SOFT_CHALLENGE',
                'reasoning': 'Model not loaded'
            }

        # Scale features
        features_scaled = scaler.transform(features)
        logger.info(f"Features scaled: {features_scaled}")

        # Get prediction
        bot_probability = float(model.predict_proba(features_scaled)[0][1])
        risk_score = int(bot_probability * 100)

        # Use live config thresholds
        if config is None:
            load_config()

        bot_threshold = int(config.get('botDetectionThreshold', 60))
        soft_threshold = int(config.get('softChallengeThreshold', 30))

        # Ensure thresholds are valid and ordered
        bot_threshold = max(0, min(100, bot_threshold))
        soft_threshold = max(0, min(bot_threshold, soft_threshold))

        if risk_score >= bot_threshold:
            action = 'BLOCK'
            reasoning = f'High risk (>= {bot_threshold}) - bot behavior detected'
        elif risk_score >= soft_threshold:
            action = 'SOFT_CHALLENGE'
            reasoning = f'Medium risk (>= {soft_threshold}) - CAPTCHA challenge recommended'
        else:
            action = 'ALLOW'
            reasoning = f'Low risk (< {soft_threshold}) - human-like behavior detected'

        logger.info(f"Prediction: risk={risk_score}, action={action}, bot_threshold={bot_threshold}, soft_threshold={soft_threshold}")

        return {
            'risk_score': risk_score,
            'bot_probability': bot_probability,
            'recommended_action': action,
            'reasoning': reasoning
        }

    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        logger.error(traceback.format_exc())
        return {
            'risk_score': 30,
            'bot_probability': 0.30,
            'recommended_action': 'SOFT_CHALLENGE',
            'reasoning': f'Error: {str(e)}'
        }

# ===== ROUTES =====

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'message': 'Bot Detection API is running',
        'status': 'ok',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/predict', methods=['POST'])
def predict():
    """Bot detection prediction endpoint"""
    try:
        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        telemetry = data.get('telemetry', {})
        session_id = data.get('session_id', 'unknown')

        logger.info(f"\n{'='*70}")
        logger.info(f"Prediction Request - Session: {session_id}")
        logger.info(f"{'='*70}")

        # Predict
        import time
        start_time = time.time()
        load_config()
        result = predict_risk(telemetry)
        latency_ms = (time.time() - start_time) * 1000

        result['latency_ms'] = latency_ms

        logger.info(f"Response: {json.dumps(result, indent=2)}")
        logger.info(f"{'='*70}\n")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug information endpoint"""
    return jsonify({
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'working_directory': os.getcwd(),
        'python_version': sys.version
    }), 200

@app.route('/api/simple-test', methods=['POST'])
def simple_test():
    """Simple test endpoint to verify bot test infrastructure"""
    logger.info("Simple test endpoint called")
    return jsonify({
        'success': True,
        'message': 'Simple test passed',
        'backend_path': os.path.abspath(__file__),
        'backend_dir': os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    }), 200

@app.route('/api/run-bot-tests', methods=['POST'])
def run_bot_tests():
    """Run bot detection tests using simple telemetry patterns"""
    logger.info("=" * 70)
    logger.info("BOT TEST ENDPOINT CALLED")
    logger.info("=" * 70)

    try:
        import time
        import requests
        
        logger.info("Starting simple bot tests...")
        
        # Define test cases with different telemetry patterns
        test_cases = [
            {
                'name': '🚫 AGGRESSIVE BOT',
                'telemetry': {
                    'mouse': {'movementEntropy': 0.2, 'velocityStats': {'mean': 500, 'stddev': 0.1, 'max': 600}, 'totalMovements': 5},
                    'keyboard': {'typingSpeed': 500, 'keystrokeEntropy': 0.1, 'errorRate': 0.0},
                    'timing': {'event_loop_jitter': 0.0}
                }
            },
            {
                'name': '⚠️ MODERATE BOT',
                'telemetry': {
                    'mouse': {'movementEntropy': 1.5, 'velocityStats': {'mean': 150, 'stddev': 20, 'max': 250}, 'totalMovements': 30},
                    'keyboard': {'typingSpeed': 150, 'keystrokeEntropy': 0.8, 'errorRate': 0.0},
                    'timing': {'event_loop_jitter': 0.5}
                }
            },
            {
                'name': '⚠️ STEALTH BOT',
                'telemetry': {
                    'mouse': {'movementEntropy': 2.8, 'velocityStats': {'mean': 25, 'stddev': 8, 'max': 80}, 'totalMovements': 80},
                    'keyboard': {'typingSpeed': 65, 'keystrokeEntropy': 1.5, 'errorRate': 0.01},
                    'timing': {'event_loop_jitter': 2.0}
                }
            },
            {
                'name': '✅ REAL HUMAN',
                'telemetry': {
                    'mouse': {'movementEntropy': 4.2, 'velocityStats': {'mean': 12.5, 'stddev': 3.2, 'max': 45}, 'totalMovements': 150},
                    'keyboard': {'typingSpeed': 45, 'keystrokeEntropy': 3.5, 'errorRate': 0.02},
                    'timing': {'event_loop_jitter': 3.2}
                }
            }
        ]
        
        results = []
        output_lines = []
        
        output_lines.append("=" * 60)
        output_lines.append("🤖 BOT DETECTION SYSTEM TESTER")
        output_lines.append("=" * 60)
        output_lines.append("")
        
        # Run tests
        for test_case in test_cases:
            output_lines.append(f"\n{'=' * 60}")
            output_lines.append(f"🤖 Testing: {test_case['name']}")
            output_lines.append(f"{'=' * 60}")
            
            try:
                # Prepare payload
                payload = {
                    'telemetry': {
                        'device': {
                            'screenResolution': {'width': 1920, 'height': 1080},
                            'colorDepth': 24,
                            'timezone': 'UTC',
                            'platform': 'Linux'
                        },
                        **test_case['telemetry']
                    },
                    'session_id': f"test-{test_case['name']}-{int(time.time())}"
                }
                
                # Make prediction request
                response = requests.post(
                    f"{request.host_url.rstrip('/')}/api/predict",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    risk_score = result.get('risk_score', 0)
                    action = result.get('recommended_action', 'UNKNOWN')
                    latency = result.get('latency_ms', 0)
                    
                    output_lines.append(f"✅ Response received in {latency:.1f}ms")
                    output_lines.append(f"\n📊 RESULTS:")
                    output_lines.append(f"   Risk Score: {risk_score}/100")
                    output_lines.append(f"   Bot Probability: {result.get('bot_probability', 0) * 100:.1f}%")
                    output_lines.append(f"   Recommended Action: {action}")
                    output_lines.append(f"   Reasoning: {result.get('reasoning', 'N/A')}")
                    
                    # Verdict
                    if risk_score < 30:
                        output_lines.append(f"\n✅ VERDICT: HUMAN - Allowed to proceed")
                    elif risk_score < 60:
                        output_lines.append(f"\n⚠️ VERDICT: SUSPICIOUS - Soft challenge (CAPTCHA)")
                    else:
                        output_lines.append(f"\n🚫 VERDICT: BOT DETECTED - Blocked")
                    
                    results.append({
                        'name': test_case['name'],
                        'risk_score': risk_score,
                        'action': action,
                        'passed': True
                    })
                else:
                    output_lines.append(f"❌ API returned {response.status_code}: {response.text}")
                    results.append({'name': test_case['name'], 'passed': False})
                    
            except Exception as e:
                output_lines.append(f"❌ Error: {e}")
                results.append({'name': test_case['name'], 'passed': False})
            
            time.sleep(0.5)
        
        # Summary
        output_lines.append("\n" + "=" * 60)
        output_lines.append("📋 TEST SUMMARY")
        output_lines.append("=" * 60)
        
        for result in results:
            status = "✅ PASS" if result.get('passed') else "❌ FAIL"
            name = result.get('name', 'Unknown')
            risk = result.get('risk_score', 'N/A')
            action = result.get('action', 'N/A')
            output_lines.append(f"{status} | {name:20} | Risk: {str(risk):3}/100 | Action: {action}")
        
        output_lines.append("=" * 60)
        output_lines.append("\n✨ Testing complete!")
        
        output = "\n".join(output_lines)
        logger.info(output)
        logger.info("=" * 70)
        
        return jsonify({
            'success': True,
            'message': 'Bot tests completed successfully',
            'output': output,
            'error': ''
        }), 200

    except Exception as e:
        logger.error(f"❌ Error running bot tests: {e}")
        logger.error(traceback.format_exc())
        logger.info("=" * 70)
        return jsonify({
            'success': False,
            'message': f'Error running bot tests: {str(e)}',
            'error': traceback.format_exc()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    global config
    if config is None:
        load_config()
    response = jsonify(config)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response, 200

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global config
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Validate required fields
        required_fields = ['botDetectionThreshold', 'softChallengeThreshold', 'maxLoginAttempts', 'modelUpdateInterval']
        for field in required_fields:
            if field not in new_config:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate threshold order and ranges
        bot_threshold = int(new_config.get('botDetectionThreshold', 60))
        soft_threshold = int(new_config.get('softChallengeThreshold', 30))
        max_login_attempts = int(new_config.get('maxLoginAttempts', 3))
        model_update_interval = int(new_config.get('modelUpdateInterval', 24))

        if not (0 <= soft_threshold <= bot_threshold <= 100):
            return jsonify({'error': 'softChallengeThreshold must be <= botDetectionThreshold and both must be between 0 and 100'}), 400
        if max_login_attempts < 1 or max_login_attempts > 100:
            return jsonify({'error': 'maxLoginAttempts must be between 1 and 100'}), 400
        if model_update_interval < 1 or model_update_interval > 168:
            return jsonify({'error': 'modelUpdateInterval must be between 1 and 168 hours'}), 400

        new_config['botDetectionThreshold'] = bot_threshold
        new_config['softChallengeThreshold'] = soft_threshold
        new_config['maxLoginAttempts'] = max_login_attempts
        new_config['modelUpdateInterval'] = model_update_interval

        # Update global config
        config = new_config

        # Save to file
        config_path = os.path.join(BACKEND_DIR, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"✅ Config updated: {config}")
        return jsonify({'message': 'Configuration updated successfully', 'config': config}), 200

    except Exception as e:
        logger.error(f"❌ Error updating config: {e}")
        return jsonify({'error': str(e)}), 500

# ===== STARTUP =====

def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("UIDAI BOT DETECTION - Backend API Server")
    print("=" * 70)

    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")

    # Load models
    if not load_model_and_scaler():
        logger.error("\n❌ Failed to load models!")
        logger.error("Run: python ml_engine/retrain/pipeline.py")
        sys.exit(1)

    # Load config (already loaded in load_model_and_scaler, but ensure it's loaded)
    load_config()

    port = int(os.environ.get('PORT', os.environ.get('FLASK_PORT', '8000')))

    logger.info("\nStarting Flask server...")
    logger.info(f"Health check: GET http://localhost:{port}/health")
    logger.info(f"Predict API: POST http://localhost:{port}/api/predict")
    print("=" * 70 + "\n")

    # Start server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
else:
    # When run under a WSGI server (e.g., gunicorn), ensure the model is loaded
    # during worker startup. If loading fails, fail fast so deployment doesn't
    # look "healthy" while returning default scores.
    if not load_model_and_scaler():
        raise RuntimeError("Failed to load ML model/scaler on startup")


# ===== REACT STATIC SERVING (optional) =====

@app.route('/', methods=['GET'])
def serve_react_index():
    """
    Serve React index.html if build exists; otherwise provide a helpful message.
    """
    index_path = os.path.join(app.static_folder or '', 'index.html')
    if app.static_folder and os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')

    return jsonify({
        'message': 'Backend is running. React build not found.',
        'expected_react_build_dir': app.static_folder,
        'hint': 'Run `npm run build` in frontend and move/copy the build folder to backend/build/.'
    }), 200


@app.route('/<path:path>', methods=['GET'])
def serve_react_static_or_fallback(path: str):
    """
    Serve static files from React build. If the file doesn't exist, fall back to
    index.html so React Router (SPA) routes work.
    """
    if not app.static_folder:
        return jsonify({'error': 'React build directory not configured'}), 404

    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)

    # SPA fallback
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')

    return jsonify({
        'error': 'React build not found',
        'expected_react_build_dir': app.static_folder
    }), 404