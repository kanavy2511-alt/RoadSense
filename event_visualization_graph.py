
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================
# SETTINGS
# =====================================

BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "Data" / "RoadSense_20261113_233445.csv"
PEAKS_FILE = BASE_DIR / "analysis_output" / "detected_events.csv"
GROUPS_FILE = BASE_DIR / "analysis_output" / "grouped_events.csv"

OUTPUT_DIR = BASE_DIR / "analysis_output" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_GRAPH = OUTPUT_DIR / "233445_event_visualization.png"

# =====================================
# LOAD DATA
# =====================================

print("Loading RoadSense data...")

df = pd.read_csv(DATA_FILE)
peaks = pd.read_csv(PEAKS_FILE)
groups = pd.read_csv(GROUPS_FILE)

# Select linear acceleration only
df = df[df["sensor_type"] == "linear_acceleration"].copy()

# Convert sensor values to numeric
for col in ["timestamp_ns", "x", "y", "z"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["timestamp_ns", "x", "y", "z"])
df = df.sort_values("timestamp_ns").reset_index(drop=True)

# Calculate time in seconds
df["time_seconds"] = (
    df["timestamp_ns"] - df["timestamp_ns"].iloc[0]
) / 1_000_000_000

# Calculate acceleration magnitude
df["magnitude"] = np.sqrt(
    df["x"]**2 + df["y"]**2 + df["z"]**2
)

# =====================================
# FILTER PEAKS AND GROUPS
# =====================================

filename = DATA_FILE.name

peaks = peaks[peaks["filename"] == filename].copy()
groups = groups[groups["filename"] == filename].copy()

print("Recording:", filename)
print("Detected peaks:", len(peaks))
print("Grouped events:", len(groups))

# =====================================
# CREATE VISUALIZATION
# =====================================

plt.figure(figsize=(16, 7))

# Original acceleration signal
plt.plot(
    df["time_seconds"],
    df["magnitude"],
    color="blue",
    linewidth=0.8,
    label="Linear Acceleration"
)

# Detected peaks
plt.scatter(
    peaks["event_time_seconds"],
    peaks["peak_magnitude"],
    color="red",
    s=55,
    marker="x",
    label="Detected Peaks",
    zorder=3
)

# Grouped event intervals
for i, event in groups.iterrows():

    plt.axvspan(
        event["event_start_seconds"],
        event["event_end_seconds"],
        color="orange",
        alpha=0.3,
        label="Grouped Event" if i == groups.index[0] else ""
    )

# Graph labels
plt.title("RoadSense - Detected Peaks and Grouped Events")
plt.xlabel("Time (seconds)")
plt.ylabel("Acceleration Magnitude (m/s²)")

plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

# Save graph
plt.savefig(OUTPUT_GRAPH, dpi=150)

plt.show()

# =====================================
# FINAL REPORT
# =====================================

print("\n========== VISUALIZATION REPORT ==========")
print("Recording:", filename)
print("Total sensor samples:", len(df))
print("Detected peaks:", len(peaks))
print("Grouped events:", len(groups))
print("Graph saved at:", OUTPUT_GRAPH)
