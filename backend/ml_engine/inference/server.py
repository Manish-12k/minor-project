# ML Model serving and inference API - FIXED IMPORTS

import asyncio
import time
import json
import logging
import os
import sys

# Add parent directories to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Now try to import the ensemble model
try:
    from ml_engine.models.ensemble_detector import BotDetectionEnsemble
except ImportError:
    try:
        from models.ensemble_detector import BotDetectionEnsemble
    except ImportError:
        logger.warning("Could not import BotDetectionEnsemble - using stub")
        BotDetectionEnsemble = None

from typing import Dict, Optional


class BotDetectionInference:
    def __init__(self, model_path: str = '/models/'):
        try:
            if BotDetectionEnsemble:
                self.ensemble = BotDetectionEnsemble(model_path)
            else:
                self.ensemble = None
                logger.warning("Using stub model - no real ML predictions")
        except Exception as e:
            logger.warning(f"Ensemble model init warning: {e}")
            self.ensemble = None

        self.session_cache = {}
        self.cache_ttl = 3600

    async def predict(self, telemetry: Dict, session_id: str) -> Dict:
        """Real-time inference with <100ms latency target"""
        start_time = time.time()

        try:
            features = self._extract_features(telemetry)
            session_context = self.session_cache.get(session_id, {})

            if self.ensemble:
                prediction = self.ensemble.predict_ensemble(features)
            else:
                # Stub prediction when model not loaded
                prediction = {
                    'bot_probability': 0.3,  # Low risk by default
                    'risk_score': 30,
                    'model_votes': {
                        'xgboost': 0.3,
                        'lstm': 0.25,
                        'gcn': 0.35,
                        'anomaly': 0.0
                    },
                    'confidence': 0.5,
                    'reasoning': 'Stub model (no trained weights loaded)'
                }

            risk_score = self._calculate_risk_score(prediction, session_context)

            self.session_cache[session_id] = {
                **session_context,
                'last_prediction': prediction,
                'last_timestamp': time.time(),
                'prediction_count': session_context.get('prediction_count', 0) + 1
            }

            latency = (time.time() - start_time) * 1000

            if latency > 100:
                logger.warning(f"Inference latency exceeded SLA: {latency:.2f}ms")

            return {
                'risk_score': risk_score,
                'bot_probability': float(prediction.get('bot_probability', 0.5)),
                'model_votes': prediction.get('model_votes', {}),
                'confidence': float(prediction.get('confidence', 0)),
                'latency_ms': round(latency, 2),
                'recommended_action': self._action_from_risk(risk_score),
                'reasoning': prediction.get('reasoning', '')
            }

        except Exception as e:
            logger.error(f"Inference error: {e}", exc_info=True)
            return {
                'risk_score': 50,
                'fallback': True,
                'error': str(e)
            }

    def _extract_features(self, telemetry: Dict) -> Dict:
        """Extract ML features from raw telemetry"""
        try:
            return {
                'mouse': telemetry.get('mouse', {}),
                'keyboard': telemetry.get('keyboard', {}),
                'device': telemetry.get('device', {}),
                'timing': telemetry.get('timing', {}),
                'touch': telemetry.get('touch', {}),
                'event_sequence': telemetry.get('event_sequence', [])
            }
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return {}

    def _calculate_risk_score(self, prediction: Dict, session_context: Dict) -> int:
        """Convert ML score to risk (0-100)"""
        try:
            base_score = int(prediction.get('bot_probability', 0.5) * 100)
            previous_scores = session_context.get('scores_history', [])
            if previous_scores:
                avg_previous = sum(previous_scores) / len(previous_scores)
                if abs(base_score - avg_previous) < 10:
                    base_score = int(base_score * 1.2)
            return min(100, max(0, base_score))
        except:
            return 50

    def _action_from_risk(self, risk_score: int) -> str:
        """Determine action based on risk"""
        if risk_score < 30:
            return 'ACCEPT'
        elif risk_score < 60:
            return 'SOFT_CHALLENGE'
        else:
            return 'ESCALATE'


# Flask app for serving
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

inference = BotDetectionInference()


@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Predict bot probability from telemetry"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        telemetry = data.get('telemetry', {})
        session_id = data.get('session_id', 'default-session')

        # Run async prediction in sync context
        import asyncio
        result = asyncio.run(inference.predict(telemetry, session_id))

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Bot Detection API is running'}), 200


@app.route('/api/risk-score', methods=['POST'])
def risk_score():
    """Calculate risk score from ML prediction"""
    try:
        data = request.get_json()
        prediction = data.get('prediction', {})
        session_context = data.get('session_context', {})

        score = inference._calculate_risk_score(prediction, session_context)

        return jsonify({
            'risk_score': score,
            'action': inference._action_from_risk(score)
        }), 200
    except Exception as e:
        logger.error(f"Risk score API error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("UIDAI BOT DETECTION - Backend API Server")
    print("=" * 70)
    print(f"Starting Flask server on http://localhost:8000")
    print(f"Health check: http://localhost:8000/health")
    print(f"Predict API: POST http://localhost:8000/api/predict")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 70)

    try:
        app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("\nMake sure these packages are installed:")
        print("  pip install flask flask-cors xgboost tensorflow scikit-learn")