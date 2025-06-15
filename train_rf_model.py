# train_rf_model.py

import os
import pandas as pd
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib

def extract_features_from_csv(file_path, label):
    try:
        df = pd.read_csv(file_path)
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
            'wpm_estimate': (correct_keystrokes / 5) / (len(df_sorted) / 60),
            'label': label
        }
        return features
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return None

def get_label_from_folder(folder_name):
    parts = folder_name.split("_")
    return parts[-1].lower() if len(parts) >= 3 else None

def load_all_datasets(root_dir):
    all_features = []
    for user in os.listdir(root_dir):
        user_path = os.path.join(root_dir, user)
        if not os.path.isdir(user_path):
            continue
        for session_folder in os.listdir(user_path):
            session_path = os.path.join(user_path, session_folder)
            if not os.path.isdir(session_path):
                continue
            label = get_label_from_folder(session_folder)
            if label:
                csv_path = os.path.join(session_path, "keystroke_data.csv")
                if os.path.exists(csv_path):
                    features = extract_features_from_csv(csv_path, label)
                    if features:
                        all_features.append(features)
    return pd.DataFrame(all_features)

# === Main ===
if __name__ == "__main__":
    root_data_dir = "Data"
    print(f"📁 Scanning '{root_data_dir}' for labeled keystroke data...")

    df = load_all_datasets(root_data_dir)
    if df.empty:
        print("❌ No data found.")
        exit()

    print(f"✅ Loaded {len(df)} labeled sessions.")

    X = df.drop(columns=['label'])
    y = df['label']

    print("\n🔁 Running Stratified 5-Fold Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)

    scores = cross_val_score(model, X, y, cv=skf)
    print(f"\n✅ Cross-Validation Accuracy (5 folds): {scores.mean():.4f} ± {scores.std():.4f}")

    # Train/test split for final evaluation + model saving
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, stratify=y, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n📊 Final Test Set Evaluation:\n")
    print(classification_report(y_test, y_pred))

    print("\n📈 Confusion Matrix (Test Set):")
    disp = ConfusionMatrixDisplay.from_predictions(y_test, y_pred, cmap="Blues")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.show()

    # Save final model
    joblib.dump(model, "keystroke_rf_model.joblib")
    print("\n✅ Model saved to keystroke_rf_model.joblib")