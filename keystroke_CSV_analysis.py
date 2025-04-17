import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("keystroke_data.csv")

sns.set(style="whitegrid")
filtered_keys = df[~df['Key'].str.contains("SHIFT|CTRL|ALT|TAB|ENTER|CAPS", case=False, na=False)]

# Error stats
total_keystrokes = len(filtered_keys[~filtered_keys['Key'].str.contains("BACKSPACE", case=False)])
backspaces = len(filtered_keys[filtered_keys['Key'].str.contains("BACKSPACE", case=False)])
error_rate = (backspaces / total_keystrokes) * 100 if total_keystrokes > 0 else 0

# Group average hold time per key
key_avg_durations = filtered_keys.groupby("Key")["Key_Hold_Time"].mean().sort_values(ascending=False)
heatmap_data = pd.DataFrame(key_avg_durations)

# Set up subplots
fig, axs = plt.subplots(2, 2, figsize=(20, 14))
fig.suptitle("Keystroke Dynamics Visualizations", fontsize=22)

# Heatmap of Key Press Durations
sns.heatmap(heatmap_data.T, cmap="YlGnBu", ax=axs[0, 0], cbar_kws={'label': 'Avg Hold Time (s)'})
axs[0, 0].set_title("Heatmap of Average Key Hold Durations", fontsize=14)
axs[0, 0].set_xlabel("Key", fontsize=12)
axs[0, 0].set_ylabel("")
axs[0, 0].tick_params(axis='x', rotation=90)

# Distribution of Hold Times
sns.histplot(df["Key_Hold_Time"], bins=40, kde=True, ax=axs[0, 1], color="skyblue")
axs[0, 1].set_title("Distribution of Key Hold Times", fontsize=14)
axs[0, 1].set_xlabel("Hold Time (s)", fontsize=12)
axs[0, 1].set_ylabel("Frequency")
axs[0, 1].set_yscale("log")

# Hold Time vs Down Time Scatter
sns.scatterplot(data=df, x="Key_Down_Time", y="Key_Hold_Time", alpha=0.4, ax=axs[1, 0], s=30)
axs[1, 0].set_title("Hold Time vs Down Time", fontsize=14)
axs[1, 0].set_xlabel("Key Down Time (s)", fontsize=12)
axs[1, 0].set_ylabel("Key Hold Time (s)")
axs[1, 0].grid(True)

# Donut chart for Typing Error Rate
labels = ['Correct Keystrokes', 'Backspaces']
sizes = [total_keystrokes, backspaces]
colors = ['#4CAF50', '#F44336']  # Green for correct, red for errors

axs[1, 1].pie(sizes, labels=labels, colors=colors, startangle=90, autopct='%1.1f%%', wedgeprops={'width':0.4})
axs[1, 1].set_title("Typing Error Rate (Backspace Usage)", fontsize=14)

# Printing layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.subplots_adjust(wspace=0.105, hspace=0.27)
plt.show()
