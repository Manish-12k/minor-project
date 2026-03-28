"""
ML Training Pipeline - FIXED VERSION
Corrects the bot/human labeling
"""

import os
import sys
import json
import pickle
import logging
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
MODELS_DIR = os.path.join(BACKEND_DIR, 'ml_engine', 'models')

os.makedirs(MODELS_DIR, exist_ok=True)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from xgboost import XGBClassifier

def generate_synthetic_data(n_samples=5000):
    """Generate synthetic bot and human behavior data with CORRECT labels"""
    logger.info("=" * 70)
    logger.info("Generating synthetic training data...")
    logger.info("=" * 70)

    X = []
    y = []

    # ===== HUMAN SAMPLES (label = 0) =====
    logger.info(f"Generating {n_samples} human behavior samples (label=0)...")
    for _ in range(n_samples):
        # Humans have HIGH entropy, natural speeds, good variation
        sample = [
            np.random.normal(4.0, 0.5),       # mouse_entropy: HIGH (4.0) = human
            np.random.normal(12.5, 3.0),      # mouse_velocity_mean: normal
            np.random.normal(3.2, 1.0),       # mouse_velocity_stddev: good variation
            np.random.normal(45, 10),         # mouse_max_velocity: reasonable
            np.random.normal(150, 30),        # total_mouse_movements: lots
            np.random.normal(45, 15),         # typing_speed: 45 WPM (normal)
            np.random.normal(3.5, 0.8),       # keystroke_entropy: HIGH (3.5) = human
            np.random.normal(0.02, 0.01),     # keystroke_error_rate: few typos
            np.random.normal(3.2, 1.0),       # event_loop_jitter: natural
            0,                                # headless: false
            np.random.normal(35000, 5000)     # interaction_time: 30+ seconds
        ]
        X.append(sample)
        y.append(0)  # Label 0 = HUMAN

    # ===== BOT SAMPLES (label = 1) =====
    logger.info(f"Generating {n_samples} bot behavior samples (label=1)...")
    for _ in range(n_samples):
        # Bots have LOW entropy, uniform speeds, minimal variation
        sample = [
            np.random.normal(0.5, 0.3),       # mouse_entropy: LOW (0.5) = bot
            np.random.normal(200, 50),        # mouse_velocity_mean: very fast
            np.random.normal(5, 5),           # mouse_velocity_stddev: minimal variation
            np.random.normal(400, 50),        # mouse_max_velocity: very high
            np.random.normal(20, 10),         # total_mouse_movements: few
            np.random.normal(300, 50),        # typing_speed: 300 WPM (inhuman)
            np.random.normal(0.3, 0.2),       # keystroke_entropy: LOW (0.3) = bot
            np.random.normal(0.0, 0.005),     # keystroke_error_rate: perfect
            np.random.normal(0.1, 0.05),      # event_loop_jitter: none
            1,                                # headless: true
            np.random.normal(3000, 1000)      # interaction_time: <5 seconds
        ]
        X.append(sample)
        y.append(1)  # Label 1 = BOT

    X = np.array(X)
    y = np.array(y)

    logger.info(f"✅ Dataset created: {len(X)} samples")
    logger.info(f"   Humans (label=0): {np.sum(y == 0)}")
    logger.info(f"   Bots (label=1): {np.sum(y == 1)}")

    return X, y

def train_model(X, y):
    """Train XGBoost model"""
    logger.info("=" * 70)
    logger.info("Training XGBoost model...")
    logger.info("=" * 70)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.125, random_state=42, stratify=y_train)

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    logger.info(f"Train - Humans: {np.sum(y_train == 0)}, Bots: {np.sum(y_train == 1)}")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost
    model = XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )

    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_val_scaled, y_val)],
        early_stopping_rounds=20,
        verbose=False
    )

    logger.info("✅ XGBoost training completed")

    # Evaluate
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    cm = confusion_matrix(y_test, y_pred)

    logger.info("\n✅ XGBoost Results:")
    logger.info(f"  Accuracy:  {accuracy:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall:    {recall:.4f}")
    logger.info(f"  F1-Score:  {f1:.4f}")
    logger.info(f"  AUC:       {auc:.4f}")
    logger.info(f"  Confusion Matrix:\n{cm}")

    # Print what confusion matrix means
    tn, fp, fn, tp = cm.ravel()
    logger.info(f"\n  True Negatives (Humans correctly identified):  {tn}")
    logger.info(f"  False Positives (Humans marked as bots):     {fp}")
    logger.info(f"  False Negatives (Bots marked as humans):     {fn}")
    logger.info(f"  True Positives (Bots correctly identified):  {tp}")

    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'auc': float(auc)
    }

    return model, scaler, metrics

def save_artifacts(model, scaler, metrics):
    """Save trained model, scaler, and metrics"""

    logger.info("=" * 70)
    logger.info("Saving artifacts...")
    logger.info("=" * 70)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # Save model with timestamp
        model_path_ts = os.path.join(MODELS_DIR, f'xgboost_bot_detector_{timestamp}.pkl')
        with open(model_path_ts, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"✅ Model saved: {model_path_ts}")

        # Save model as latest
        model_path_latest = os.path.join(MODELS_DIR, 'xgboost_bot_detector_latest.pkl')
        with open(model_path_latest, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"✅ Latest model saved: {model_path_latest}")

        # Save scaler
        scaler_path = os.path.join(MODELS_DIR, 'scaler_latest.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"✅ Scaler saved: {scaler_path}")

        # Save metrics
        metrics_path = os.path.join(MODELS_DIR, 'training_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"✅ Metrics saved: {metrics_path}")

        # Verify
        logger.info("\n✅ Verification:")
        for file in [model_path_latest, scaler_path, metrics_path]:
            if os.path.exists(file):
                size = os.path.getsize(file)
                logger.info(f"  ✅ {os.path.basename(file)} ({size:,} bytes)")
            else:
                logger.error(f"  ❌ {os.path.basename(file)} NOT FOUND!")

    except Exception as e:
        logger.error(f"❌ Error saving artifacts: {e}")
        raise

def main():
    """Main entry point"""
    logger.info("\n" + "=" * 70)
    logger.info("🤖 UIDAI BOT DETECTION - ML TRAINING PIPELINE")
    logger.info("=" * 70)
    logger.info(f"Models directory: {MODELS_DIR}\n")

    try:
        # Generate data
        X, y = generate_synthetic_data(n_samples=5000)

        # Train model
        model, scaler, metrics = train_model(X, y)

        # Save artifacts
        save_artifacts(model, scaler, metrics)

        logger.info("\n" + "=" * 70)
        logger.info("✅ TRAINING COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info("\nNext steps:")
        logger.info("1. Restart backend: python -m ml_engine.inference.server")
        logger.info("2. Test bot detection: python bot_simulator.py")
        logger.info("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()