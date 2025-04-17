import random
import time
import csv

def generate_keystroke_data(text, condition, wpm, session_length=None, simulate_real_time=False):
    typing_conditions = {
        "normal": {"base_noise": 0.24, "typo_rate": 0.05},
        "high_load": {"base_noise": 0.45, "typo_rate": 0.15},
        "fatigue": {"base_noise": 0.69, "typo_rate": 0.30}
    }

    if condition not in typing_conditions:
        raise ValueError("Invalid condition. Choose from: normal, high_load, fatigue")

    base_cpm = wpm * 5
    base_delay = 60 / base_cpm

    keystroke_data = []
    start_time = time.time()
    session_length = session_length or len(text)

    caps_lock_active = False
    current_time = 0
    i = 0
    typo_rate = typing_conditions[condition]["typo_rate"]

    while i < session_length:
        char = text[i % len(text)]
        is_upper = char.isupper()

        # Caps Lock logic
        if is_upper:
            seq_start = i
            seq_len = 0
            while (seq_start + seq_len < len(text)) and text[seq_start + seq_len].isupper():
                seq_len += 1
            if seq_len >= 2 and not caps_lock_active:
                keystroke_data.append(["CAPS_LOCK_ON", current_time, 0.05, 0.05, 0.05])
                caps_lock_active = True
            elif seq_len < 2 and not caps_lock_active:
                keystroke_data.append(["SHIFT_DOWN", current_time, 0.01, 0.01, 0.02])
        elif caps_lock_active and not is_upper:
            keystroke_data.append(["CAPS_LOCK_OFF", current_time, 0.05, 0.05, 0.05])
            caps_lock_active = False

        # Key timings
        key_down_time = random.uniform(0.08, 0.12)
        key_hold_time = random.uniform(0.09, 0.2)
        key_up_time = random.uniform(0.08, 0.12)

        # Micro-pauses
        if char in ",.;:":
            delay_multiplier = random.uniform(1.2, 1.5)
        elif char in "!?":
            delay_multiplier = random.uniform(1.3, 1.6)
        elif char == " ":
            delay_multiplier = random.uniform(1.1, 1.3)
        else:
            delay_multiplier = random.uniform(0.95, 1.05)

        noise = random.gauss(0, typing_conditions[condition]["base_noise"])
        delay = max(0.01, base_delay * delay_multiplier + noise + random.uniform(0.05, 0.1))

        # Typo handling
        typed_char = char
        if random.random() < typo_rate:
            typed_char = random.choice("abcdefghijklmnopqrstuvwxyz")
            if typed_char != char:
                keystroke_data.append([typed_char, current_time, 0.01, 0.1, 0.01])
                current_time += random.uniform(0.01, 0.03)
                keystroke_data.append(["BACKSPACE", current_time, 0.02, 0.05, 0.01])
                current_time += 0.05
                keystroke_data.append([char, current_time, 0.01, 0.1, 0.01])
        else:
            keystroke_data.append([char, current_time, key_down_time, key_hold_time, key_up_time])

        # Random non-typo BACKSPACE noise
        if random.random() < 0.01:
            keystroke_data.append(["BACKSPACE", current_time + 0.01, 0.02, 0.05, 0.01])

        # Shift up after single capital letter
        if is_upper and not caps_lock_active and seq_len < 2:
            keystroke_data.append(["SHIFT_UP", current_time + 0.02, 0.01, 0.01, 0.01])

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

# Random noise addition to remove artificial feeling
def add_jitter_and_format(val):
    if isinstance(val, (float, int)):
        jitter = random.uniform(-0.003, 0.003)
        jittered = val + jitter

        # Prevent unrealistic small or negative values
        jittered = max(jittered, 0.001)
        return f"{jittered:.4f}"
    return val

# Fast simulation
# Set to "true" if you want more realistiv typing speeds, although slows down content generation considerably
simulate_real_time = False

# Generate data
data = generate_keystroke_data(text_to_type, typing_condition, wpm, simulate_real_time=simulate_real_time)

# Save data
csv_file = "keystroke_data.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Key", "Timestamp (s)", "Key_Down_Time", "Key_Hold_Time", "Key_Up_Time"])

    for row in data:
        formatted_row = [add_jitter_and_format(val) if i > 0 else val for i, val in enumerate(row)]
        writer.writerow(formatted_row)

print(f"Keystroke data saved to {csv_file}")
