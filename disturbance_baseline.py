
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# ROADSENSE - DISTURBANCE BASELINE ANALYSIS
# ==========================================

DATA_DIR = Path("Data")
OUTPUT_DIR = Path("analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)

CANDIDATE_THRESHOLDS = [0.15, 0.30, 0.50, 1.00]

BASELINE_IDS = ["231031", "231659"]

results = []

print("=" * 65)
print("       ROADSENSE DISTURBANCE BASELINE ANALYSIS")
print("=" * 65)

for file_path in sorted(DATA_DIR.glob("*.csv")):

    try:
        df = pd.read_csv(file_path)

        # Only process newer-format files
        if "sensor_type" not in df.columns:
            continue

        if "timestamp_ns" not in df.columns:
            continue

        # Use only gravity-removed acceleration
        df = df[df["sensor_type"] == "linear_acceleration"].copy()

        if df.empty:
            continue

        for col in ["x", "y", "z"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["x", "y", "z"])

        if df.empty:
            continue

        # Calculate total acceleration magnitude
        magnitude = np.sqrt(
            df["x"]**2 +
            df["y"]**2 +
            df["z"]**2
        )

        if len(magnitude) == 0:
            continue

        # Identify recording category
        if any(recording_id in file_path.name for recording_id in BASELINE_IDS):
            category = "candidate_low_motion_baseline"
        elif "233445" in file_path.name:
            category = "controlled_movement_comparison"
        else:
            category = "comparison_recording_unlabelled"

        row = {
            "filename": file_path.name,
            "category": category,
            "sample_count": len(magnitude),
            "median_magnitude": magnitude.median(),
            "p95_magnitude": magnitude.quantile(0.95),
            "p99_magnitude": magnitude.quantile(0.99),
            "max_magnitude": magnitude.max()
        }

        # Percentage of samples above each candidate threshold
        for threshold in CANDIDATE_THRESHOLDS:
            percentage = (magnitude > threshold).mean() * 100
            row[f"percent_above_{threshold:.2f}"] = percentage

        results.append(row)

    except Exception as error:
        print(f"Skipped {file_path.name}: {error}")

# ==========================================
# SAVE REPORT
# ==========================================

if not results:
    print("\nNo suitable linear_acceleration recordings found.")
else:
    report = pd.DataFrame(results)

    output_file = OUTPUT_DIR / "disturbance_baseline_report.csv"
    report.to_csv(output_file, index=False)

    print("\nRECORDING SUMMARY")
    print("-" * 65)

    for _, row in report.iterrows():
        print(f"\nFile: {row['filename']}")
        print(f"Category: {row['category']}")
        print(f"Samples: {row['sample_count']}")
        print(f"Median: {row['median_magnitude']:.4f} m/s²")
        print(f"95th percentile: {row['p95_magnitude']:.4f} m/s²")
        print(f"99th percentile: {row['p99_magnitude']:.4f} m/s²")
        print(f"Maximum: {row['max_magnitude']:.4f} m/s²")

        print("Percentage above candidate thresholds:")
        for threshold in CANDIDATE_THRESHOLDS:
            col = f"percent_above_{threshold:.2f}"
            print(f"  {threshold:.2f} m/s²: {row[col]:.2f}%")

    print("\n" + "=" * 65)
    print(f"Total recordings analysed: {len(report)}")
    print(f"Report saved: {output_file}")
    print("=" * 65)

    print("\nIMPORTANT:")
    print("These thresholds are experimental candidates, not final settings.")
    print("Low-motion recordings are candidates, not confirmed normal-road data.")
