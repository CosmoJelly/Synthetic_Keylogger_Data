# test_model.py

import pandas as pd
import joblib

# Load model
model = joblib.load("keystroke_rf_model.joblib")

# Define test cases
test_profiles = {
    "perfect_normal": {
        'avg_hold_time': 0.11,
        'std_hold_time': 0.015,
        'keystroke_count': 95,
        'backspace_count': 1,
        'error_rate': 1.05,
        'inter_key_latency_mean': 0.14,
        'inter_key_latency_std': 0.05,
        'wpm_estimate': 52.3
    },
    "mild_fatigue": {
        'avg_hold_time': 0.185,
        'std_hold_time': 0.03,
        'keystroke_count': 83,
        'backspace_count': 12,
        'error_rate': 17.4,
        'inter_key_latency_mean': 0.28,
        'inter_key_latency_std': 0.08,
        'wpm_estimate': 26.5
    },
    "extreme_fatigue": {
        'avg_hold_time': 0.26,
        'std_hold_time': 0.06,
        'keystroke_count': 65,
        'backspace_count': 35,
        'error_rate': 117.2,  # More backspaces than actual typing
        'inter_key_latency_mean': 0.43,
        'inter_key_latency_std': 0.14,
        'wpm_estimate': 9.1
    },
    "high_load_bursting": {
        'avg_hold_time': 0.13,
        'std_hold_time': 0.025,
        'keystroke_count': 97,
        'backspace_count': 7,
        'error_rate': 7.8,
        'inter_key_latency_mean': 0.17,
        'inter_key_latency_std': 0.12,
        'wpm_estimate': 54.8
    },
    "normal_typo_heavy": {
        'avg_hold_time': 0.12,
        'std_hold_time': 0.022,
        'keystroke_count': 91,
        'backspace_count': 20,
        'error_rate': 28.2,
        'inter_key_latency_mean': 0.16,
        'inter_key_latency_std': 0.06,
        'wpm_estimate': 47.1
    },
    "ambiguous_edge_case": {
        'avg_hold_time': 0.16,
        'std_hold_time': 0.04,
        'keystroke_count': 87,
        'backspace_count': 16,
        'error_rate': 22.5,
        'inter_key_latency_mean': 0.3,
        'inter_key_latency_std': 0.07,
        'wpm_estimate': 23.9
    }
}

# Run each profile
for name, features in test_profiles.items():
    print(f"\n🔍 Testing Profile: {name}")
    df = pd.DataFrame([features])
    prediction = model.predict(df)[0]
    proba = model.predict_proba(df)[0]

    print(f"🧠 Prediction: {prediction}")
    print("📊 Probabilities:")
    for cls, p in zip(model.classes_, proba):
        print(f"  - {cls.capitalize():<8}: {p*100:.2f}%")

    print("📈 Features:")
    for k, v in features.items():
        print(f"  {k}: {v}")