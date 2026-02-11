# ML Ensemble detector for bot classification

import numpy as np
import xgboost as xgb
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from typing import Dict, Tuple


class BotDetectionEnsemble:
    def __init__(self, model_path: str = '/models/'):
        self.model_path = model_path

        # Load or initialize models
        try:
            self.xgb_model = xgb.XGBClassifier(
                n_estimators=500,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=1.0,
                reg_lambda=2.0,
                random_state=42
            )
        except Exception as e:
            print(f"Warning: XGBoost model loading failed: {e}")

        try:
            self.lstm_model = tf.keras.Sequential([
                tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(None, 10)),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.LSTM(64),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
        except Exception as e:
            print(f"Warning: LSTM model initialization failed: {e}")

        try:
            self.anomaly_detector = IsolationForest(
                contamination=0.05,
                n_estimators=100,
                random_state=42
            )
        except Exception as e:
            print(f"Warning: Anomaly detector initialization failed: {e}")

    def predict_ensemble(self, features: Dict) -> Dict:
        """
        Predict bot probability using ensemble
        """
        try:
            # Extract features
            tabular_features = self._extract_tabular(features)
            sequence_features = self._extract_sequence(features)

            # Individual model predictions
            xgb_pred = 0.5  # Fallback
            lstm_pred = 0.5
            gcn_pred = 0.5
            anomaly_score = 0.0

            try:
                xgb_pred = self.xgb_model.predict_proba(tabular_features)[0, 1]
            except:
                pass

            try:
                lstm_pred = float(self.lstm_model.predict(sequence_features)[0, 0])
            except:
                pass

            try:
                anomaly_score = 1.0 if self.anomaly_detector.predict(tabular_features)[0] == -1 else 0.0
            except:
                pass

            # Ensemble combination
            ensemble_score = np.mean([xgb_pred, lstm_pred, gcn_pred])

            final_score = (ensemble_score * 0.7 + anomaly_score * 0.3)

            return {
                'bot_probability': float(final_score),
                'risk_score': int(final_score * 100),
                'model_votes': {
                    'xgboost': float(xgb_pred),
                    'lstm': float(lstm_pred),
                    'gcn': float(gcn_pred),
                    'anomaly': float(anomaly_score)
                },
                'confidence': float(np.max([xgb_pred, lstm_pred, gcn_pred])),
                'reasoning': self._explain_prediction(features, [xgb_pred, lstm_pred, gcn_pred])
            }
        except Exception as e:
            return {
                'bot_probability': 0.5,
                'risk_score': 50,
                'error': str(e),
                'fallback': True
            }

    def _extract_tabular(self, features: Dict) -> np.ndarray:
        """Extract environmental + statistical features"""
        try:
            return np.array([
                features.get('mouse', {}).get('velocity_mean', 0),
                features.get('mouse', {}).get('velocity_stddev', 0),
                features.get('mouse', {}).get('movement_entropy', 0),
                features.get('keyboard', {}).get('typing_speed', 0),
                features.get('keyboard', {}).get('keystroke_entropy', 0),
                features.get('device', {}).get('screen_resolution', [1920, 1080])[0] / 1920,
                features.get('device', {}).get('screen_resolution', [1920, 1080])[1] / 1080,
                features.get('timing', {}).get('event_loop_jitter', 0),
                features.get('timing', {}).get('inter_event_variance', 0),
                features.get('touch', {}).get('pressure_variance', 0) if 'touch' in features else 0,
            ]).reshape(1, -1)
        except:
            return np.zeros((1, 10))

    def _extract_sequence(self, features: Dict) -> np.ndarray:
        """Extract sequence features for LSTM"""
        try:
            event_seq = features.get('event_sequence', [])
            padded = np.zeros((1, 100, 10))

            for i, event in enumerate(event_seq[:100]):
                padded[0, i] = self._encode_event(event)

            return padded
        except:
            return np.zeros((1, 100, 10))

    def _encode_event(self, event: Dict) -> np.ndarray:
        """Encode single event"""
        event_type_map = {'click': 0, 'keydown': 1, 'mousemove': 2, 'scroll': 3, 'touch': 4}
        try:
            return np.array([
                event_type_map.get(event.get('type', 'unknown'), -1),
                event.get('x', 0) / 1000,
                event.get('y', 0) / 1000,
                event.get('timestamp', 0) / 10000,
                event.get('pressure', 1),
                0, 0, 0, 0, 0
            ])
        except:
            return np.zeros(10)

    def _explain_prediction(self, features: Dict, model_scores: list) -> str:
        """Human-readable explanation"""
        reasons = []

        if features.get('mouse', {}).get('movement_entropy', 10) < 2.0:
            reasons.append("Low mouse movement entropy")

        if features.get('keyboard', {}).get('keystroke_entropy', 5) > 4.5:
            reasons.append("Perfect keystroke timing")

        if features.get('timing', {}).get('event_loop_jitter', 5) < 1.0:
            reasons.append("Suspicious timing variance")

        if np.mean(model_scores) > 0.7:
            reasons.append("Converged bot signals")

        return " | ".join(reasons) if reasons else "No obvious bot signals"