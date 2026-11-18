
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_FOLDER = Path(__file__).resolve().parent
DATA_FOLDER = BASE_FOLDER / "Data"
OUTPUT_FOLDER = BASE_FOLDER / "analysis_output"
PLOT_FOLDER = OUTPUT_FOLDER / "plots"

PLOT_FOLDER.mkdir(parents=True, exist_ok=True)

summary = []

print("=" * 55)
print("          ROADSENSE SENSOR ANALYSIS")
print("=" * 55)

for file in sorted(DATA_FOLDER.glob("*.csv")):

    df = pd.read_csv(file)

    if "timestamp_ms" in df.columns:
        time_column = "timestamp_ms"
        time_divisor = 1000

    elif "timestamp_ns" in df.columns:
        time_column = "timestamp_ns"
        time_divisor = 1_000_000_000

    else:
        print("Skipping:", file.name)
        continue

    for column in ["x", "y", "z", time_column]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["x", "y", "z", time_column])

    if df.empty:
        continue

    df["time_seconds"] = (
        df[time_column] - df[time_column].min()
    ) / time_divisor

    df["magnitude"] = np.sqrt(
        df["x"]**2 + df["y"]**2 + df["z"]**2
    )

    if "sensor_type" in df.columns:

        sensor_types = df["sensor_type"].dropna().unique()

        for sensor in sensor_types:

            sensor_df = df[
                df["sensor_type"] == sensor
            ].copy()

            sensor_df = sensor_df.sort_values("time_seconds")

            if sensor_df.empty:
                continue

            plt.figure(figsize=(12, 5))

            plt.plot(
                sensor_df["time_seconds"],
                sensor_df["magnitude"],
                linewidth=1
            )

            plt.title(f"{file.name} - {sensor}")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Acceleration magnitude (m/s²)")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            plot_path = PLOT_FOLDER / (
                f"{file.stem}_{sensor}.png"
            )

            plt.savefig(plot_path, dpi=150)
            plt.close()

            summary.append({
                "filename": file.name,
                "sensor_type": sensor,
                "readings": len(sensor_df),
                "mean_magnitude": sensor_df["magnitude"].mean(),
                "max_magnitude": sensor_df["magnitude"].max()
            })

    else:

        df = df.sort_values("time_seconds")

        plt.figure(figsize=(12, 5))

        plt.plot(
            df["time_seconds"],
            df["magnitude"],
            linewidth=1
        )

        plt.title(f"{file.name} - Unspecified acceleration")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Acceleration magnitude (m/s²)")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plot_path = PLOT_FOLDER / f"{file.stem}_unspecified.png"

        plt.savefig(plot_path, dpi=150)
        plt.close()

        summary.append({
            "filename": file.name,
            "sensor_type": "unspecified",
            "readings": len(df),
            "mean_magnitude": df["magnitude"].mean(),
            "max_magnitude": df["magnitude"].max()
        })

    print("Analysed:", file.name)

if summary:

    report = pd.DataFrame(summary)

    report.to_csv(
        OUTPUT_FOLDER / "acceleration_summary.csv",
        index=False
    )

    print("\n" + "=" * 55)
    print("ANALYSIS COMPLETED")
    print("Summary saved successfully!")
    print("Graphs saved in:", PLOT_FOLDER)
    print("Total sensor records:", len(summary))
    print("=" * 55)

else:
    print("No valid sensor recordings found.")
