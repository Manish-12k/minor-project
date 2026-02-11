# Risk scoring and threshold calibration

import numpy as np
from typing import Dict
from datetime import datetime
import math


class RiskScoring:
    def __init__(self):
        self.thresholds = {
            'uidai_authentication': {'low': 30, 'medium': 60, 'high': 80},
            'uidai_dashboard': {'low': 25, 'medium': 55, 'high': 75},
            'uidai_download': {'low': 40, 'medium': 65, 'high': 85}
        }

        self.toa_multipliers = {
            '00-06': 1.1,
            '06-12': 1.0,
            '12-18': 0.95,
            '18-24': 1.05
        }

    def calculate_risk(
            self,
            ml_score: float,
            session_context: Dict,
            request_context: Dict,
            portal_type: str
    ) -> Dict:
        """
        Multi-factor risk assessment
        """
        try:
            # Base score from ML
            base_score = ml_score * 100

            # Factor 1: Session consistency
            consistency_penalty = self._consistency_penalty(session_context)

            # Factor 2: Time-of-day adjustment
            toa_multiplier = self._time_of_day_multiplier(request_context.get('timestamp'))

            # Combine (weighted)
            final_score = (
                                  base_score * 0.5 +
                                  consistency_penalty * 0.3 +
                                  0 * 0.2  # Geo penalty placeholder
                          ) * toa_multiplier

            final_score = min(100, max(0, final_score))

            friction_level = self._friction_from_score(final_score, portal_type)

            return {
                'risk_score': int(final_score),
                'risk_level': self._risk_level(final_score),
                'friction_level': friction_level,
                'factors': {
                    'ml_score': base_score,
                    'consistency_penalty': consistency_penalty,
                    'toa_multiplier': toa_multiplier
                },
                'reasoning': self._explain_risk(final_score, portal_type)
            }
        except Exception as e:
            return {
                'risk_score': 50,
                'risk_level': 'MEDIUM',
                'friction_level': 'SOFT',
                'error': str(e)
            }

    def _consistency_penalty(self, session_context: Dict) -> float:
        """Check if behavior is consistent"""
        history = session_context.get('ml_scores_history', [])

        if len(history) < 2:
            return 0

        variance = np.var(history)

        if variance < 0.05:
            avg_score = np.mean(history)
            return 70 if avg_score > 0.6 else 0
        else:
            return 20

    def _time_of_day_multiplier(self, timestamp: int = None) -> float:
        """TOD risk adjustment"""
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())

        hour = (timestamp // 3600) % 24

        if 0 <= hour < 6:
            return 1.1
        elif 6 <= hour < 12:
            return 1.0
        elif 12 <= hour < 18:
            return 0.95
        else:
            return 1.05

    def _friction_from_score(self, score: int, portal_type: str) -> str:
        """Map risk to friction level"""
        thresholds = self.thresholds.get(portal_type, self.thresholds['uidai_authentication'])

        if score < thresholds['low']:
            return 'NONE'
        elif score < thresholds['medium']:
            return 'SOFT'
        else:
            return 'ESCALATED'

    def _risk_level(self, score: int) -> str:
        """Convert score to risk level"""
        if score < 33:
            return 'LOW'
        elif score < 67:
            return 'MEDIUM'
        else:
            return 'HIGH'

    def _explain_risk(self, score: int, portal_type: str) -> str:
        """Explain risk score"""
        if score < 30:
            return "Low risk - seamless access"
        elif score < 60:
            return "Medium risk - soft challenge recommended"
        else:
            return "High risk - escalation recommended"