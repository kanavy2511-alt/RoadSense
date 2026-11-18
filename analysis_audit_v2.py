
import pandas as pd
from pathlib import Path

OUT = Path(__file__).parent / "analysis_output"

peaks = pd.read_csv(OUT / "detected_events.csv")
groups = pd.read_csv(OUT / "grouped_events.csv")

print("\n========== DEEP GROUP AUDIT ==========\n")

mismatches = 0
overlapping_groups = 0

for filename in sorted(groups["filename"].unique()):

    p = peaks[peaks["filename"] == filename]
    g = groups[groups["filename"] == filename].reset_index(drop=True)

    for i, group in g.iterrows():

        actual = p[
            (p["event_time_seconds"] >= group["event_start_seconds"]) &
            (p["event_time_seconds"] <= group["event_end_seconds"])
        ]

        expected = int(group["peak_count"])

        if len(actual) != expected:
            mismatches += 1
            print("COUNT MISMATCH:", filename)
            print("  Group:", i)
            print("  Recorded:", expected)
            print("  Actual:", len(actual))

        if i > 0:
            previous = g.iloc[i - 1]

            if group["event_start_seconds"] < previous["event_end_seconds"]:
                overlapping_groups += 1
                print("OVERLAPPING GROUPS:", filename, "Group", i)

print("\n========== FINAL RESULTS ==========")
print("Peak count mismatches:", mismatches)
print("Overlapping group intervals:", overlapping_groups)

if mismatches == 0 and overlapping_groups == 0:
    print("\nAll tested grouping consistency checks passed.")

