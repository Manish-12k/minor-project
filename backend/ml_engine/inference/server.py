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

        # Determine action
        if risk_score < 30:
            action = 'ALLOW'
            reasoning = 'Low risk - human-like behavior detected'
        elif risk_score < 60:
            action = 'SOFT_CHALLENGE'
            reasoning = 'Medium risk - CAPTCHA challenge recommended'
        else:
            action = 'BLOCK'
            reasoning = 'High risk - bot behavior detected'

        logger.info(f"Prediction: risk={risk_score}, action={action}")

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

@app.route('/api/run-bot-tests', methods=['POST'])
def run_bot_tests():
    """Run bot detection tests using the bot simulator"""
    try:
        import sys
        import os
        from io import StringIO

        logger.info("Starting bot tests...")

        # Import the bot simulator module directly
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from bot_simulator import BotSimulator

        # Get the API URL for this server
        api_url = os.environ.get('API_URL') or 'https://minor-project-backend-zp8v.onrender.com'
        logger.info(f"Using API URL: {api_url}")

        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            # Create simulator and run tests
            simulator = BotSimulator(api_url)
            simulator.run_all_tests()

            # Get the captured output
            output = captured_output.getvalue()

        finally:
            # Restore stdout
            sys.stdout = old_stdout

        logger.info("Bot tests completed successfully")
        return jsonify({
            'success': True,
            'message': 'Bot tests completed successfully',
            'output': output,
            'error': ''
        }), 200

    except Exception as e:
        logger.error(f"Error running bot tests: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error running bot tests: {str(e)}',
            'error': traceback.format_exc()
        }), 500

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