import csv
import statistics
import matplotlib.pyplot as plt

def analyze_keystroke_csv(file_path):
    timestamps = []
    hold_times = []
    down_times = []
    up_times = []
    backspace_times = []

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
                if key not in ["SHIFT_DOWN", "SHIFT_UP", "CAPS_LOCK_ON", "CAPS_LOCK_OFF"]:
                    timestamps.append(timestamp)
                    hold_times.append(key_hold)
                    down_times.append(key_down)
                    up_times.append(key_up)

                # Track backspace occurrences
                if key == "BACKSPACE":
                    backspace_times.append(timestamp)

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

    # Create a single window with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # Keystroke delay distribution
    axs[0, 0].hist(delays, bins=20, color='purple', edgecolor='black')
    axs[0, 0].set_title("Keystroke Delay Distribution")
    axs[0, 0].set_xlabel("Delay (s)")
    axs[0, 0].set_ylabel("Frequency")
    axs[0, 0].grid(True)

    # Backspace occurrences
    axs[0, 1].hist(backspace_times, bins=20, color='red', edgecolor='black')
    axs[0, 1].set_title("Backspace Occurrences")
    axs[0, 1].set_xlabel("Timestamp (s)")
    axs[0, 1].set_ylabel("Frequency")
    axs[0, 1].grid(True)

# WPM over time (with valid intervals)
    time_intervals = [timestamps[i] - timestamps[0] for i in range(len(timestamps))]
    valid_wpm_values = []
    valid_time_intervals = []

    for i in range(1, len(timestamps)):  # Start from 1 to avoid division by zero
        if time_intervals[i] > 0:
            wpm = (i) / (time_intervals[i] / 60)
            valid_wpm_values.append(wpm)
            valid_time_intervals.append(time_intervals[i])

    # Plot WPM values over time with valid intervals
    axs[1, 0].plot(valid_time_intervals, valid_wpm_values, color='blue')
    axs[1, 0].set_title("Typing Speed (WPM) Over Time")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("WPM")
    axs[1, 0].grid(True)

    # Key Hold Time Distribution
    axs[1, 1].hist(hold_times, bins=20, color='green', edgecolor='black')
    axs[1, 1].set_title("Key Hold Time Distribution")
    axs[1, 1].set_xlabel("Key Hold Time (s)")
    axs[1, 1].set_ylabel("Frequency")
    axs[1, 1].grid(True)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    file_path = input("Enter path to synthetic keystroke CSV: ")
    analyze_keystroke_csv(file_path)
