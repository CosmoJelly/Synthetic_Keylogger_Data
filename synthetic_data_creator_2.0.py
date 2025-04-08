import random
import time
import csv

def generate_keystroke_data(text, condition, wpm, session_length=None, simulate_real_time=False):
    typing_conditions = {
        "normal": {"base_noise": 0.07},
        "high_load": {"base_noise": 0.16},
        "fatigue": {"base_noise": 0.34}
    }

    if condition not in typing_conditions:
        raise ValueError("Invalid condition. Choose from: normal, high_load, fatigue")

    base_cpm = wpm * 5  # 1 word = ~5 characters
    base_delay = 60 / base_cpm  # seconds per character

    keystroke_data = []
    start_time = time.time()
    session_length = session_length or len(text)

    caps_lock_active = False
    current_time = 0
    i = 0

    while i < session_length:
        char = text[i % len(text)]

        # Detect uppercase sequence
        if char.isupper():
            seq_start = i
            seq_len = 0
            while (seq_start + seq_len < len(text)) and text[seq_start + seq_len].isupper():
                seq_len += 1

            if seq_len >= 2 and not caps_lock_active:
                keystroke_data.append(["CAPS_LOCK_ON", current_time, 0.05, 0.05, 0.05])
                caps_lock_active = True

            elif seq_len < 2 and not caps_lock_active:
                keystroke_data.append(["SHIFT_DOWN", current_time, 0.01, 0.01, 0.02])

        elif caps_lock_active and not char.isupper():
            keystroke_data.append(["CAPS_LOCK_OFF", current_time, 0.05, 0.05, 0.05])
            caps_lock_active = False

        # Simulate key timings
        key_down_time = max(0.005, random.uniform(0.01, 0.03))
        key_hold_time = random.uniform(0.08, 0.2)
        key_up_time = max(0.005, random.uniform(0.01, 0.03))
        noise = random.gauss(0, typing_conditions[condition]["base_noise"])
        delay = max(0.01, base_delay + noise)

        keystroke_data.append([char, current_time, key_down_time, key_hold_time, key_up_time])

        # Random backspace
        if random.random() < 0.05:
            keystroke_data.append(["BACKSPACE", current_time + 0.01, 0.02, 0.05, 0.01])

        if char.isupper() and seq_len < 2 and not caps_lock_active:
            keystroke_data.append(["SHIFT_UP", current_time + 0.02, 0.01, 0.01, 0.01])

        # Advance simulated time
        current_time += delay

        if simulate_real_time:
            time.sleep(delay)

        i += 1

    if caps_lock_active:
        keystroke_data.append(["CAPS_LOCK_OFF", current_time, 0.05, 0.05, 0.05])

    return keystroke_data

# User input
text_to_type = input("Enter the text to simulate typing: ")
typing_condition = input("Enter typing condition (normal, high_load, fatigue): ")
wpm_input = input("Enter desired WPM (Words Per Minute): ")

try:
    wpm = float(wpm_input)
except ValueError:
    print("Invalid WPM entered. Using default of 50.")
    wpm = 50.0

# Noise addition to create remove artifical feeling from values
def add_jitter_and_format(val):
    if isinstance(val, (float, int)):
        jitter = random.uniform(-0.003, 0.003)
        jittered = val + jitter

        # Prevent unrealistic small or negative values
        jittered = max(jittered, 0.001)
        return f"{jittered:.4f}"
    return val

# Fast simulation (change to True for real-time delays)
simulate_real_time = False

# Generate and save
data = generate_keystroke_data(text_to_type, typing_condition, wpm, simulate_real_time=simulate_real_time)

csv_file = "synthetic_keystroke_data.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Key", "Timestamp (s)", "Key_Down_Time", "Key_Hold_Time", "Key_Up_Time"])

    for row in data:
        formatted_row = [add_jitter_and_format(val) if i > 0 else val for i, val in enumerate(row)]
        writer.writerow(formatted_row)

print(f"Synthetic keystroke data saved to {csv_file}")