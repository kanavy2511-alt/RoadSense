
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

OUTPUT_GRAPH = BASE_DIR / "analysis_output" / "233445_event_duration.png"
OUTPUT_CSV = BASE_DIR / "analysis_output" / "estimated_event_durations.csv"

ACTIVITY_THRESHOLD = 0.15
SMOOTHING_WINDOW = 5
QUIET_DURATION_SECONDS = 0.10

# =====================================
# LOAD DATA
# =====================================

df = pd.read_csv(DATA_FILE)
peaks = pd.read_csv(PEAKS_FILE)
groups = pd.read_csv(GROUPS_FILE)

df = df[df["sensor_type"] == "linear_acceleration"].copy()

df["timestamp_ns"] = pd.to_numeric(df["timestamp_ns"])
for col in ["x", "y", "z"]:
    df[col] = pd.to_numeric(df[col])

df = df.dropna(subset=["timestamp_ns", "x", "y", "z"])
df = df.sort_values("timestamp_ns").reset_index(drop=True)

df["time_seconds"] = (
    df["timestamp_ns"] - df["timestamp_ns"].iloc[0]
) / 1_000_000_000

df["magnitude"] = np.sqrt(
    df["x"]**2 + df["y"]**2 + df["z"]**2
)

# Smooth small fluctuations
df["smoothed"] = df["magnitude"].rolling(
    window=SMOOTHING_WINDOW,
    center=True,
    min_periods=1
).median()

# =====================================
# FILTER RECORDING
# =====================================

filename = DATA_FILE.name

peaks = peaks[peaks["filename"] == filename].copy()
groups = groups[groups["filename"] == filename].copy()

times = df["time_seconds"].to_numpy()
signal = df["smoothed"].to_numpy()

if len(times) < 2:
    raise ValueError("Not enough sensor samples!")

sample_interval = np.median(np.diff(times))

if sample_interval <= 0:
    raise ValueError("Invalid timestamp sequence!")

quiet_samples = max(
    1,
    int(np.ceil(QUIET_DURATION_SECONDS / sample_interval))
)

# =====================================
# ESTIMATE EVENT DURATIONS
# =====================================

results = []

for _, event in groups.iterrows():

    start_idx = np.searchsorted(
        times, event["event_start_seconds"]
    )

    end_idx = np.searchsorted(
        times, event["event_end_seconds"]
    )

    start_idx = min(start_idx, len(times) - 1)
    end_idx = min(end_idx, len(times) - 1)

    # Extend backwards until sustained quiet activity
    quiet_count = 0
    i = start_idx

    while i > 0:
        i -= 1

        if signal[i] <= ACTIVITY_THRESHOLD:
            quiet_count += 1
            if quiet_count >= quiet_samples:
                break
        else:
            quiet_count = 0

    estimated_start_idx = min(
        start_idx,
        i + quiet_count
    )

    # Extend forwards until sustained quiet activity
    quiet_count = 0
    i = end_idx

    while i < len(times) - 1:
        i += 1

        if signal[i] <= ACTIVITY_THRESHOLD:
            quiet_count += 1
            if quiet_count >= quiet_samples:
                break
        else:
            quiet_count = 0

    estimated_end_idx = max(
        end_idx,
        i - quiet_count
    )

    start = times[estimated_start_idx]
    end = times[estimated_end_idx]

    results.append({
        "filename": filename,
        "start_seconds": start,
        "end_seconds": end,
        "duration_seconds": end - start,
        "peak_count": event["peak_count"],
        "max_magnitude": event["max_magnitude"]
    })

# =====================================
# SAVE RESULTS
# =====================================

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_CSV, index=False)

# =====================================
# VISUALIZATION
# =====================================

plt.figure(figsize=(15, 7))

plt.plot(
    times,
    df["magnitude"],
    color="blue",
    alpha=0.45,
    linewidth=0.8,
    label="Original Acceleration"
)

plt.plot(
    times,
    signal,
    color="blue",
    linewidth=1.2,
    label="Smoothed Acceleration"
)

plt.scatter(
    peaks["event_time_seconds"],
    peaks["peak_magnitude"],
    color="red",
    s=45,
    label="Detected Peaks",
    zorder=3
)

plt.axhline(
    ACTIVITY_THRESHOLD,
    color="green",
    linestyle="--",
    label="Activity Threshold"
)

for i, event in results_df.iterrows():
    plt.axvspan(
        event["start_seconds"],
        event["end_seconds"],
        color="orange",
        alpha=0.25,
        label="Estimated Event Duration" if i == 0 else ""
    )

plt.title("RoadSense - Event Duration Estimation")
plt.xlabel("Time (seconds)")
plt.ylabel("Acceleration Magnitude (m/s²)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(OUTPUT_GRAPH, dpi=150)
plt.show()

# =====================================
# FINAL REPORT
# =====================================

print("\n========== EVENT DURATION REPORT ==========")

print(results_df.to_string(index=False))

print("\nTotal events:", len(results_df))
print("Total detected peaks:", len(peaks))
print("Activity threshold:", ACTIVITY_THRESHOLD)
print("Estimated durations saved:", OUTPUT_CSV)
print("Graph saved:", OUTPUT_GRAPH)
