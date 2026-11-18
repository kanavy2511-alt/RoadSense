
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "analysis_output"

peaks_file = OUTPUT_DIR / "detected_events.csv"
groups_file = OUTPUT_DIR / "grouped_events.csv"

peaks = pd.read_csv(peaks_file)
groups = pd.read_csv(groups_file)

print("\n========== ROAD SENSE ANALYSIS AUDIT ==========\n")

print("Total detected peaks:", len(peaks))
print("Total grouped events:", len(groups))

print("\n--- PEAKS AND GROUPS BY RECORDING ---\n")

for filename in sorted(peaks["filename"].unique()):

    file_peaks = peaks[
        peaks["filename"] == filename
    ]

    file_groups = groups[
        groups["filename"] == filename
    ]

    assigned = 0
    duplicated = 0

    for _, peak in file_peaks.iterrows():

        time = peak["event_time_seconds"]

        matches = file_groups[
            (file_groups["event_start_seconds"] <= time) &
            (file_groups["event_end_seconds"] >= time)
        ]

        if len(matches) >= 1:
            assigned += 1

        if len(matches) > 1:
            duplicated += 1

    unassigned = len(file_peaks) - assigned

    print("Recording:", filename)
    print("  Detected peaks:", len(file_peaks))
    print("  Grouped events:", len(file_groups))
    print("  Assigned peaks:", assigned)
    print("  Unassigned peaks:", unassigned)
    print("  Peaks in overlapping groups:", duplicated)

print("\n--- GROUP DURATION CHECK ---\n")

groups["duration_seconds"] = (
    groups["event_end_seconds"] -
    groups["event_start_seconds"]
)

print("Shortest group:",
      round(groups["duration_seconds"].min(), 3), "seconds")

print("Longest group:",
      round(groups["duration_seconds"].max(), 3), "seconds")

print("\nTotal peaks represented by group counts:",
      groups["peak_count"].sum())

print("\n========== AUDIT COMPLETE ==========")
