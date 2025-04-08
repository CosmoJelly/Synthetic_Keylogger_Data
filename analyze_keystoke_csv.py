import csv
import statistics
import matplotlib.pyplot as plt

def analyze_keystroke_csv(file_path):
    timestamps = []
    hold_times = []
    down_times = []
    up_times = []

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                key = row['Key']
                timestamp = float(row['Timestamp (s)'])
                key_down = float(row['Key_Down_Time'])
                key_hold = float(row['Key_Hold_Time'])
                key_up = float(row['Key_Up_Time'])

                # Ignore SHIFT, CAPSLOCK, BACKSPACE for speed stats
                if key not in ["SHIFT_DOWN", "SHIFT_UP", "CAPS_LOCK_ON", "CAPS_LOCK_OFF", "BACKSPACE"]:
                    timestamps.append(timestamp)
                    hold_times.append(key_hold)
                    down_times.append(key_down)
                    up_times.append(key_up)

            except ValueError:
                continue

    if len(timestamps) < 2:
        print("Not enough data points.")
        return

    # Calculate delays
    delays = [round(timestamps[i] - timestamps[i - 1], 4) for i in range(1, len(timestamps))]

    # Basic stats
    print("\n--- Keystroke Data Analysis ---")
    print(f"Total Keystrokes: {len(timestamps)}")
    print(f"Typing Duration: {timestamps[-1]:.2f} seconds")
    print(f"Average Delay Between Keystrokes: {statistics.mean(delays):.4f} s")
    print(f"Average Key Hold Time: {statistics.mean(hold_times):.4f} s")
    print(f"Average Key Down Time: {statistics.mean(down_times):.4f} s")
    print(f"Average Key Up Time: {statistics.mean(up_times):.4f} s")

    # Approximate WPM
    chars = len(timestamps)
    words = chars / 5
    duration_minutes = timestamps[-1] / 60
    estimated_wpm = words / duration_minutes
    print(f"Estimated Typing Speed: {estimated_wpm:.2f} WPM")

    # Optional: Plot histogram of delays
    plt.hist(delays, bins=20, color='purple', edgecolor='black')
    plt.title("Keystroke Delay Distribution")
    plt.xlabel("Delay (s)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    file_path = input("Enter path to synthetic keystroke CSV: ")
    analyze_keystroke_csv(file_path)