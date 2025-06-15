# keystroke_realtime_demo.py

import time
import threading
from pynput import keyboard
import pandas as pd
from collections import deque
import joblib
import os
from datetime import datetime

# === Load trained model ===
MODEL_PATH = "keystroke_rf_model.joblib"
LOG_PATH = "predictions_log.csv"

if not os.path.exists(MODEL_PATH):
    print(f"❌ Trained model not found at {MODEL_PATH}. Please run training first.")
    exit()

model = joblib.load(MODEL_PATH)

# === Globals ===
keystrokes = deque()
key_down_times = {}

# === Parameters ===
WINDOW_SIZE = 30
FEATURE_INTERVAL = 5

# === Setup CSV Log ===
log_columns = [
    "Timestamp", "Prediction", "avg_hold_time", "std_hold_time", "keystroke_count",
    "backspace_count", "error_rate", "inter_key_latency_mean",
    "inter_key_latency_std", "wpm_estimate"
]

if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=log_columns).to_csv(LOG_PATH, index=False)

# === Keyboard Callbacks ===
def on_press(key):
    try:
        k = key.char if hasattr(key, 'char') else str(key)
    except:
        k = str(key)
    key_down_times[k] = time.time()

def on_release(key):
    try:
        k = key.char if hasattr(key, 'char') else str(key)
    except:
        k = str(key)

    down_time = key_down_times.get(k)
    if down_time:
        up_time = time.time()
        hold_time = up_time - down_time
        keystrokes.append({
            'Key': k,
            'Timestamp': down_time,
            'Key_Down_Time': down_time,
            'Key_Hold_Time': hold_time,
            'Key_Up_Time': up_time
        })
        del key_down_times[k]

    if key == keyboard.Key.esc:
        return False

# === Feature Extraction ===
def prune_buffer():
    now = time.time()
    while keystrokes and (now - keystrokes[0]['Key_Down_Time']) > WINDOW_SIZE:
        keystrokes.popleft()

def extract_features():
    prune_buffer()
    if not keystrokes:
        return None

    df = pd.DataFrame(keystrokes)
    total_keystrokes = len(df)
    backspaces = df['Key'].str.contains('BACKSPACE', case=False).sum()
    correct_keystrokes = total_keystrokes - backspaces
    error_rate = (backspaces / correct_keystrokes) * 100 if correct_keystrokes > 0 else 0

    df_sorted = df.sort_values(by='Key_Down_Time')
    latencies = df_sorted['Key_Down_Time'].diff().dropna()

    features = {
        'avg_hold_time': df['Key_Hold_Time'].mean(),
        'std_hold_time': df['Key_Hold_Time'].std(),
        'keystroke_count': total_keystrokes,
        'backspace_count': backspaces,
        'error_rate': error_rate,
        'inter_key_latency_mean': latencies.mean(),
        'inter_key_latency_std': latencies.std(),
        'wpm_estimate': (correct_keystrokes / 5) / (WINDOW_SIZE / 60),
    }

    return features

# === Model Prediction ===
def predict_condition(features):
    if not features or any(pd.isna(val) for val in features.values()):
        return "Insufficient Data"

    df = pd.DataFrame([features])
    try:
        prediction = model.predict(df)[0]
        return prediction.capitalize()
    except Exception as e:
        return f"Prediction Error: {e}"

# === Periodic Inference Loop ===
def periodic_analysis():
    while True:
        time.sleep(FEATURE_INTERVAL)
        features = extract_features()
        prediction = predict_condition(features)

        # Print friendly console output
        now_str = datetime.now().strftime("%H:%M:%S")
        if features:
            print(f"\n[🧠 {now_str}] Prediction: {prediction}")
            print(f"Features: WPM={features['wpm_estimate']:.1f} | Error={features['error_rate']:.1f}% | Hold={features['avg_hold_time']:.3f}s")

        # Save to CSV log
        row = {
            "Timestamp": datetime.now().isoformat(),
            "Prediction": prediction
        }
        if features:
            row.update(features)
        pd.DataFrame([row]).to_csv(LOG_PATH, mode='a', header=False, index=False)

# === Main ===
if __name__ == "__main__":
    print("🔴 Real-time keystroke monitoring started. Press [ESC] to stop.")
    threading.Thread(target=periodic_analysis, daemon=True).start()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("\n🟢 Logging session ended.")
    print(f"📄 Full prediction log saved to: {LOG_PATH}")