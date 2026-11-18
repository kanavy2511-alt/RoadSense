
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.signal import peak_widths

# ==========================================
# ROADSENSE EVENT DURATION ANALYSIS
# VERSION 2
# ==========================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Data"
OUT_DIR = BASE_DIR / "analysis_output"

PEAKS_FILE = OUT_DIR / "detected_events.csv"
GROUPS_FILE = OUT_DIR / "grouped_events.csv"

peaks_df = pd.read_csv(PEAKS_FILE)
groups_df = pd.read_csv(GROUPS_FILE)

duration_results = []

print("\n========== ROADSENSE DURATION ANALYSIS V2 ==========\n")

# ==========================================
# PROCESS EACH RECORDING
# ==========================================

for filename in sorted(groups_df["filename"].unique()):

    print("Processing:", filename)

    file_path = DATA_DIR / filename

    df = pd.read_csv(file_path)

    df = df[
        df["sensor_type"] == "linear_acceleration"
    ].copy()

    df["timestamp_ns"] = pd.to_numeric(
        df["timestamp_ns"], errors="coerce"
    )

    for col in ["x", "y", "z"]:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(
        subset=["timestamp_ns", "x", "y", "z"]
    )

    df = df.sort_values(
        "timestamp_ns"
    ).reset_index(drop=True)

    if len(df) < 3:
        continue

    # Convert nanoseconds into seconds

    time = (
        df["timestamp_ns"].to_numpy() -
        df["timestamp_ns"].iloc[0]
    ) / 1e9

    # Calculate acceleration magnitude

    magnitude = np.sqrt(
        df["x"].to_numpy() ** 2 +
        df["y"].to_numpy() ** 2 +
        df["z"].to_numpy() ** 2
    )

    file_peaks = peaks_df[
        peaks_df["filename"] == filename
    ].copy().reset_index(drop=True)

    file_groups = groups_df[
        groups_df["filename"] == filename
    ].copy()

    if file_peaks.empty:
        continue

    # ==========================================
    # FIND PEAK POSITIONS
    # ==========================================

    peak_indices = []

    for _, peak in file_peaks.iterrows():

        idx = np.argmin(
            np.abs(
                time - peak["event_time_seconds"]
            )
        )

        peak_indices.append(idx)

    # ==========================================
    # CALCULATE PEAK WIDTHS
    # ==========================================

    widths = peak_widths(
        magnitude,
        np.array(peak_indices),
        rel_height=0.5
    )

    left_indices = widths[2]
    right_indices = widths[3]

    left_times = np.interp(
        left_indices,
        np.arange(len(time)),
        time
    )

    right_times = np.interp(
        right_indices,
        np.arange(len(time)),
        time
    )

    peak_width_data = pd.DataFrame({
        "peak_time": file_peaks[
            "event_time_seconds"
        ].to_numpy(),

        "left_time": left_times,

        "right_time": right_times,

        "width_seconds": (
            right_times - left_times
        )
    })

    # ==========================================
    # ANALYSE EACH GROUP
    # ==========================================

    for _, group in file_groups.iterrows():

        members = peak_width_data[
            (
                peak_width_data["peak_time"]
                >= group["event_start_seconds"]
            ) &
            (
                peak_width_data["peak_time"]
                <= group["event_end_seconds"]
            )
        ]

        if members.empty:
            continue

        intervals = sorted(
            zip(
                members["left_time"],
                members["right_time"]
            )
        )

        # Merge overlapping peak-width intervals

        merged = []

        for start, end in intervals:

            if not merged or start > merged[-1][1]:

                merged.append([start, end])

            else:

                merged[-1][1] = max(
                    merged[-1][1],
                    end
                )

        # Total time covered by the merged intervals

        union_duration = sum(
            end - start
            for start, end in merged
        )

        # Time from first peak-width boundary
        # to last peak-width boundary

        envelope_duration = (
            max(end for start, end in intervals)
            -
            min(start for start, end in intervals)
        )

        duration_results.append({

            "filename": filename,

            "event_start_seconds":
                group["event_start_seconds"],

            "event_end_seconds":
                group["event_end_seconds"],

            "peak_count": len(members),

            "group_span_seconds": (
                group["event_end_seconds"]
                -
                group["event_start_seconds"]
            ),

            "sum_of_peak_widths_seconds": round(
                members["width_seconds"].sum(), 4
            ),

            "union_peak_width_seconds": round(
                union_duration, 4
            ),

            "peak_width_envelope_seconds": round(
                envelope_duration, 4
            )
        })

    # ==========================================
    # VISUALIZATION FOR 233445
    # ==========================================

    if "233445" in filename:

        plt.figure(figsize=(14, 6))

        plt.plot(
            time,
            magnitude,
            color="blue",
            linewidth=0.8,
            label="Acceleration magnitude"
        )

        plt.scatter(
            file_peaks["event_time_seconds"],
            magnitude[peak_indices],
            color="red",
            s=35,
            label="Detected peaks",
            zorder=3
        )

        for _, row in peak_width_data.iterrows():

            plt.axvspan(
                row["left_time"],
                row["right_time"],
                color="green",
                alpha=0.22
            )

        plt.xlabel("Time (seconds)")
        plt.ylabel("Acceleration magnitude (m/s²)")

        plt.title(
            "RoadSense - Event Duration Analysis V2"
        )

        plt.legend()
        plt.grid(alpha=0.25)
        plt.tight_layout()

        graph_path = (
            OUT_DIR /
            "233445_duration_visualization.png"
        )

        plt.savefig(
            graph_path,
            dpi=150
        )

        plt.close()

        print("Duration graph saved:", graph_path)


# ==========================================
# SAVE RESULTS
# ==========================================

results = pd.DataFrame(duration_results)

csv_path = (
    OUT_DIR /
    "estimated_event_durations.csv"
)

results.to_csv(
    csv_path,
    index=False
)

# ==========================================
# FINAL REPORT
# ==========================================

print("\n========== FINAL DURATION RESULTS ==========\n")

if not results.empty:

    print(
        results.to_string(index=False)
    )

    print(
        "\nTotal events analysed:",
        len(results)
    )

else:

    print("No events were analysed.")

print("\nReport saved:", csv_path)

print("\n========== ANALYSIS COMPLETE ==========\n")
