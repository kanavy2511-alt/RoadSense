
from pathlib import Path
import pandas as pd

BASE_FOLDER = Path(__file__).resolve().parent
OUTPUT_FOLDER = BASE_FOLDER / "analysis_output"

INPUT_FILE = OUTPUT_FOLDER / "detected_events.csv"
OUTPUT_FILE = OUTPUT_FOLDER / "grouped_events.csv"

GROUP_GAP_SECONDS = 0.5
MAX_EVENT_DURATION_SECONDS = 1.0

df = pd.read_csv(INPUT_FILE)

if df.empty:
    print("No detected peaks available.")
    raise SystemExit

grouped_events = []

for filename, file_df in df.groupby("filename"):

    file_df = file_df.sort_values(
        "event_time_seconds"
    ).reset_index(drop=True)

    current_group = []

    for _, row in file_df.iterrows():

        if not current_group:
            current_group.append(row)
            continue

        previous_time = current_group[-1]["event_time_seconds"]
        gap = row["event_time_seconds"] - previous_time

        event_duration = (
            row["event_time_seconds"]
            - current_group[0]["event_time_seconds"]
        )

        if (
            gap <= GROUP_GAP_SECONDS
            and event_duration <= MAX_EVENT_DURATION_SECONDS
        ):
            current_group.append(row)

        else:
            grouped_events.append({
                "filename": filename,
                "event_start_seconds": current_group[0]["event_time_seconds"],
                "event_end_seconds": current_group[-1]["event_time_seconds"],
                "peak_count": len(current_group),
                "max_magnitude": max(
                    item["peak_magnitude"]
                    for item in current_group
                ),
                "max_prominence": max(
                    item["prominence"]
                    for item in current_group
                )
            })

            current_group = [row]

    if current_group:
        grouped_events.append({
            "filename": filename,
            "event_start_seconds": current_group[0]["event_time_seconds"],
            "event_end_seconds": current_group[-1]["event_time_seconds"],
            "peak_count": len(current_group),
            "max_magnitude": max(
                item["peak_magnitude"]
                for item in current_group
            ),
            "max_prominence": max(
                item["prominence"]
                for item in current_group
            )
        })

report = pd.DataFrame(grouped_events)

report.to_csv(OUTPUT_FILE, index=False)

print("=" * 55)
print("       ROADSENSE GROUPED EVENT ANALYSIS")
print("=" * 55)

for filename, file_df in report.groupby("filename"):

    print(f"\n{filename}")
    print("Grouped events:", len(file_df))

    for _, event in file_df.iterrows():

        print(
            f"  {event['event_start_seconds']:.3f}s"
            f" - {event['event_end_seconds']:.3f}s"
            f" | Peaks: {event['peak_count']}"
            f" | Maximum: {event['max_magnitude']:.3f}"
        )

print("\n" + "=" * 55)
print("GROUPING COMPLETED")
print("Total grouped events:", len(report))
print("Report saved:", OUTPUT_FILE)
print("=" * 55)
