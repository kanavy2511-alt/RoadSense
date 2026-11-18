from pathlib import Path
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

BASE_FOLDER = Path(__file__).resolve().parent
DATA_FOLDER = BASE_FOLDER / "Data"
OUTPUT_FOLDER = BASE_FOLDER / "analysis_output"

OUTPUT_FOLDER.mkdir(exist_ok=True)

MIN_HEIGHT = 0.3
MIN_PROMINENCE = 0.2
MIN_DISTANCE_SECONDS = 0.15

detected_events = []

print("=" * 55)
print("       ROADSENSE EVENT DETECTION")
print("=" * 55)

for file in sorted(DATA_FOLDER.glob("*.csv")):

    df = pd.read_csv(file)

    if "sensor_type" not in df.columns:
        continue

    if "timestamp_ns" in df.columns:
        time_column = "timestamp_ns"
        divisor = 1_000_000_000

    elif "timestamp_ms" in df.columns:
        time_column = "timestamp_ms"
        divisor = 1000

    else:
        continue

    df = df[
        df["sensor_type"] == "linear_acceleration"
    ].copy()

    if df.empty:
        continue

    for col in [time_column, "x", "y", "z"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=[time_column, "x", "y", "z"]
    )

    df = df.sort_values(time_column)

    if len(df) < 3:
        continue

    df["time_seconds"] = (
        df[time_column] - df[time_column].iloc[0]
    ) / divisor

    df["magnitude"] = np.sqrt(
        df["x"]**2 +
        df["y"]**2 +
        df["z"]**2
    )

    time_differences = np.diff(df["time_seconds"])

    sample_interval = np.median(time_differences)

    if sample_interval <= 0:
        continue

    distance_samples = max(
        1,
        int(MIN_DISTANCE_SECONDS / sample_interval)
    )

    peaks, properties = find_peaks(
        df["magnitude"].to_numpy(),
        height=MIN_HEIGHT,
        prominence=MIN_PROMINENCE,
        distance=distance_samples
    )

    print(f"\nFile: {file.name}")
    print(f"Detected peaks: {len(peaks)}")

    for i, peak in enumerate(peaks):

        event_time = df["time_seconds"].iloc[peak]
        event_magnitude = df["magnitude"].iloc[peak]

        detected_events.append({
            "filename": file.name,
            "event_time_seconds": event_time,
            "peak_magnitude": event_magnitude,
            "prominence": properties["prominences"][i]
        })

        print(
            f"  Event at {event_time:.3f}s"
            f" | Magnitude: {event_magnitude:.3f}"
        )

report = pd.DataFrame(detected_events)

report.to_csv(
    OUTPUT_FOLDER / "detected_events.csv",
    index=False
)

print("\n" + "=" * 55)
print("EVENT DETECTION COMPLETED")
print("Total detected peaks:", len(detected_events))
print("Report saved: detected_events.csv")
print("=" * 55)