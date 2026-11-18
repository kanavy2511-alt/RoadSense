
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# ROADSENSE - THRESHOLD PERSISTENCE ANALYSIS
# ==========================================

DATA_DIR = Path("Data")
OUTPUT_DIR = Path("analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)

THRESHOLDS = [0.15, 0.30, 0.50, 1.00]

summary_results = []
event_results = []

print("=" * 65)
print("       ROADSENSE THRESHOLD PERSISTENCE ANALYSIS")
print("=" * 65)

for file_path in sorted(DATA_DIR.glob("*.csv")):

    try:
        df = pd.read_csv(file_path)

        if not {"timestamp_ns", "sensor_type", "x", "y", "z"}.issubset(df.columns):
            continue

        df = df[df["sensor_type"] == "linear_acceleration"].copy()

        if df.empty:
            continue

        df["timestamp_ns"] = pd.to_numeric(
            df["timestamp_ns"], errors="coerce"
        )

        for col in ["x", "y", "z"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(
            subset=["timestamp_ns", "x", "y", "z"]
        ).sort_values("timestamp_ns").reset_index(drop=True)

        if len(df) < 2:
            continue

        timestamps = df["timestamp_ns"].to_numpy(dtype=float) / 1e9

        magnitude = np.sqrt(
            df["x"].to_numpy() ** 2 +
            df["y"].to_numpy() ** 2 +
            df["z"].to_numpy() ** 2
        )

        time_differences = np.diff(timestamps)
        valid_differences = time_differences[
            time_differences > 0
        ]

        if len(valid_differences) == 0:
            continue

        median_interval = np.median(valid_differences)

        # A large timestamp gap separates two independent runs.
        maximum_gap = median_interval * 2.5

        for threshold in THRESHOLDS:

            above = magnitude > threshold
            indices = np.where(above)[0]

            runs = []

            if len(indices) > 0:

                current_run = [indices[0]]

                for index in indices[1:]:

                    previous = current_run[-1]

                    consecutive = index == previous + 1
                    time_gap_ok = (
                        timestamps[index] - timestamps[previous]
                        <= maximum_gap
                    )

                    if consecutive and time_gap_ok:
                        current_run.append(index)
                    else:
                        runs.append(current_run)
                        current_run = [index]

                runs.append(current_run)

            durations = []

            for run_number, run in enumerate(runs, start=1):

                start_time = timestamps[run[0]]
                end_time = timestamps[run[-1]]

                duration = (
                    end_time - start_time + median_interval
                )

                peak_magnitude = float(np.max(magnitude[run]))

                durations.append(duration)

                event_results.append({
                    "filename": file_path.name,
                    "threshold": threshold,
                    "run_number": run_number,
                    "start_seconds": start_time,
                    "end_seconds": end_time,
                    "estimated_duration_seconds": duration,
                    "sample_count": len(run),
                    "peak_magnitude": peak_magnitude
                })

            summary_results.append({
                "filename": file_path.name,
                "threshold": threshold,
                "samples_above_threshold": len(indices),
                "run_count": len(runs),
                "longest_run_seconds": max(durations, default=0),
                "total_run_duration_seconds": sum(durations),
                "median_sample_interval_seconds": median_interval
            })

    except Exception as error:
        print(f"Skipped {file_path.name}: {error}")


# ==========================================
# SAVE RESULTS
# ==========================================

if not summary_results:

    print("\nNo suitable recordings found.")

else:

    summary = pd.DataFrame(summary_results)
    events = pd.DataFrame(event_results)

    summary_path = OUTPUT_DIR / "threshold_persistence_summary.csv"
    events_path = OUTPUT_DIR / "threshold_persistence_events.csv"

    summary.to_csv(summary_path, index=False)
    events.to_csv(events_path, index=False)

    print("\nPERSISTENCE SUMMARY")
    print("-" * 65)

    for filename in summary["filename"].unique():

        recording = summary[summary["filename"] == filename]

        print(f"\nRecording: {filename}")

        for _, row in recording.iterrows():

            print(
                f"Threshold {row['threshold']:.2f} m/s² | "
                f"Runs: {row['run_count']} | "
                f"Longest: {row['longest_run_seconds']:.4f}s | "
                f"Total duration: {row['total_run_duration_seconds']:.4f}s"
            )

    print("\n" + "=" * 65)
    print(f"Recordings analysed: {summary['filename'].nunique()}")
    print(f"Thresholds tested: {len(THRESHOLDS)}")
    print(f"Summary saved: {summary_path}")
    print(f"Individual runs saved: {events_path}")
    print("=" * 65)

    print("\nNOTE:")
    print("Durations are estimates based on consecutive sensor samples.")
    print("They are not yet validated physical disturbance durations.")
