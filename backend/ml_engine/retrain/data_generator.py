# Generate synthetic training data for ML models

import numpy as np
import pandas as pd
from typing import Tuple
import json
from datetime import datetime


class TrainingDataGenerator:
    """Generate labeled training data for bot detection models"""

    def __init__(self, n_human_samples: int = 5000, n_bot_samples: int = 5000):
        self.n_human_samples = n_human_samples
        self.n_bot_samples = n_bot_samples

    def generate_human_behavior(self) -> dict:
        """Generate realistic human behavior signals"""

        # Mouse movement - natural entropy
        mouse_entropy = np.random.normal(4.5, 0.8)  # Mean 4.5, std 0.8
        velocity_mean = np.random.normal(15, 5)  # Natural movement
        velocity_stddev = np.random.normal(4, 1)  # Variability

        # Keyboard - human-like rhythm
        typing_speed = np.random.normal(50, 15)  # WPM
        keystroke_entropy = np.random.normal(3.8, 0.6)
        error_rate = np.random.uniform(0.01, 0.05)  # 1-5% errors

        # Device - diverse hardware
        screen_width = np.random.choice([1920, 2560, 1366, 1024, 768])
        screen_height = np.random.choice([1080, 1440, 768, 768, 1024])
        color_depth = np.random.choice([24, 32])

        # Timing - jittery (human-like)
        event_loop_jitter = np.random.uniform(2, 5)  # ms
        inter_event_variance = np.random.uniform(10, 50)

        return {
            'mouse_entropy': max(0, mouse_entropy),
            'mouse_velocity_mean': max(0, velocity_mean),
            'mouse_velocity_stddev': max(0, velocity_stddev),
            'keyboard_typing_speed': max(0, typing_speed),
            'keyboard_keystroke_entropy': max(0, keystroke_entropy),
            'keyboard_error_rate': error_rate,
            'screen_width': screen_width,
            'screen_height': screen_height,
            'color_depth': color_depth,
            'event_loop_jitter': event_loop_jitter,
            'inter_event_variance': inter_event_variance,
            'label': 0  # Human
        }

    def generate_bot_behavior(self) -> dict:
        """Generate bot-like behavior signals"""

        # Mouse - perfect regularity (bot signature)
        mouse_entropy = np.random.uniform(0.5, 1.5)  # Low entropy
        velocity_mean = np.random.uniform(10, 20)
        velocity_stddev = np.random.uniform(0.1, 0.5)  # Very uniform

        # Keyboard - perfect timing
        typing_speed = np.random.uniform(200, 500)  # Superhuman WPM
        keystroke_entropy = np.random.uniform(4.8, 5.5)  # Perfect regularity
        error_rate = np.random.uniform(0, 0.001)  # No errors

        # Device - standard hardware
        screen_width = 1920
        screen_height = 1080
        color_depth = 24

        # Timing - machine-like precision
        event_loop_jitter = np.random.uniform(0.1, 0.5)  # Very low
        inter_event_variance = np.random.uniform(0.5, 2)  # Consistent

        return {
            'mouse_entropy': max(0, mouse_entropy),
            'mouse_velocity_mean': max(0, velocity_mean),
            'mouse_velocity_stddev': max(0, velocity_stddev),
            'keyboard_typing_speed': max(0, typing_speed),
            'keyboard_keystroke_entropy': max(0, keystroke_entropy),
            'keyboard_error_rate': error_rate,
            'screen_width': screen_width,
            'screen_height': screen_height,
            'color_depth': color_depth,
            'event_loop_jitter': event_loop_jitter,
            'inter_event_variance': inter_event_variance,
            'label': 1  # Bot
        }

    def generate_dataset(self) -> pd.DataFrame:
        """Generate complete training dataset"""

        print("Generating synthetic training data...")

        data = []

        # Generate human samples
        print(f"Generating {self.n_human_samples} human behavior samples...")
        for _ in range(self.n_human_samples):
            data.append(self.generate_human_behavior())

        # Generate bot samples
        print(f"Generating {self.n_bot_samples} bot behavior samples...")
        for _ in range(self.n_bot_samples):
            data.append(self.generate_bot_behavior())

        # Create DataFrame
        df = pd.DataFrame(data)

        # Shuffle
        df = df.sample(frac=1).reset_index(drop=True)

        print(f"Dataset created with {len(df)} samples")
        print(f"Human samples: {(df['label'] == 0).sum()}")
        print(f"Bot samples: {(df['label'] == 1).sum()}")

        return df

    def save_dataset(self, df: pd.DataFrame, filepath: str = 'training_data.csv'):
        """Save dataset to CSV"""
        df.to_csv(filepath, index=False)
        print(f"Dataset saved to {filepath}")
        return filepath


# Usage
if __name__ == '__main__':
    generator = TrainingDataGenerator(n_human_samples=5000, n_bot_samples=5000)
    df = generator.generate_dataset()
    generator.save_dataset(df, 'training_data.csv')