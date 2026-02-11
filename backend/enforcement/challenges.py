# Adaptive friction and challenge mechanisms

import random
import string
from typing import Dict, Optional


class AdaptiveFriction:
    """Minimal friction mechanisms"""

    def __init__(self):
        self.challenge_types = [
            'INVISIBLE_CLICK',
            'SLIDER',
            'TOUCH_TAP',
            'MATH'
        ]

    def apply_friction(self, friction_level: str, user_context: Dict) -> Dict:
        """
        Assign appropriate challenge
        """
        if friction_level == 'NONE':
            return {'challenge': None, 'allow': True, 'timeout': 0}

        elif friction_level == 'SOFT':
            device_type = user_context.get('device_type', 'desktop')
            attempts = user_context.get('challenge_attempts', 0)

            if device_type == 'mobile':
                challenge = self._touch_challenge()
            else:
                challenge = self._click_challenge() if attempts == 0 else self._slider_challenge()

            return {
                'challenge': challenge,
                'timeout': 60,
                'allow': False
            }

        else:  # ESCALATED
            return {
                'challenge': self._cognitive_challenge(),
                'timeout': 120,
                'allow': False
            }

    def _click_challenge(self) -> Dict:
        """Invisible element click"""
        return {
            'type': 'INVISIBLE_CLICK',
            'description': 'Click to continue',
            'element_position': (random.randint(0, 100), random.randint(0, 100)),
            'element_size': (50, 50),
            'timeout': 30
        }

    def _touch_challenge(self) -> Dict:
        """Mobile tap challenge"""
        return {
            'type': 'VISUAL_TAP',
            'description': 'Tap the button',
            'button_label': 'Tap Here',
            'timeout': 30
        }

    def _slider_challenge(self) -> Dict:
        """Slider verification"""
        return {
            'type': 'SLIDER',
            'description': 'Slide to verify',
            'min': 0,
            'max': 100,
            'required_position': 100,
            'timeout': 60
        }

    def _cognitive_challenge(self) -> Dict:
        """Simple math challenge"""
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        correct = a + b

        # Generate wrong answers
        options = [correct]
        while len(options) < 4:
            wrong = random.randint(1, 20)
            if wrong != correct and wrong not in options:
                options.append(wrong)

        random.shuffle(options)

        return {
            'type': 'MATH',
            'question': f'{a} + {b} = ?',
            'options': options,
            'correct': correct,
            'timeout': 120
        }

    def validate_challenge_response(self, challenge: Dict, response: Dict) -> bool:
        """Verify challenge response"""
        try:
            if challenge['type'] == 'INVISIBLE_CLICK':
                click_x, click_y = response['position']
                target_x, target_y = challenge['element_position']
                size_w, size_h = challenge['element_size']

                return (
                        target_x <= click_x <= target_x + size_w and
                        target_y <= click_y <= target_y + size_h
                )

            elif challenge['type'] == 'SLIDER':
                return response['value'] >= challenge['required_position']

            elif challenge['type'] == 'MATH':
                return response['answer'] == challenge['correct']

            elif challenge['type'] == 'VISUAL_TAP':
                return response.get('tapped', False)

            return False
        except Exception as e:
            print(f"Challenge validation error: {e}")
            return False