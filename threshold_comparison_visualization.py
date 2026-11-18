
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# ROADSENSE - VISUAL THRESHOLD VALIDATION
# ==========================================

DATA_DIR = Path("Data")
OUTPUT_DIR = Path("analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)

RECORDINGS = {
    "231031": "Candidate low-motion baseline",
    "231659": "Candidate low-motion baseline",
    "233445": "Controlled-movement comparison",
    "233058": "Sustained-activity comparison",
    "225626": "Unlabelled comparison",
    "225741": "Unlabelled comparison"
}

THRESHOLDS = [0.30, 1.00]

fig, axes = plt.subplots(3, 2, figsize=(16, 12))
axes = axes.flatten()

print("=" * 65)
print("       ROADSENSE VISUAL THRESHOLD VALIDATION")
print("=" * 65)

for ax, (recording_id, description) in zip(axes, RECORDINGS.items()):

    matching_files = list(DATA_DIR.glob(f"*{recording_id}*.csv"))

    if not matching_files:
        ax.set_title(f"{recording_id} - FILE NOT FOUND")
        ax.axis("off")
        print(f"Missing recording: {recording_id}")
        continue

    file_path = matching_files[0]

    df = pd.read_csv(file_path)

    required = {
        "timestamp_ns", "sensor_type", "x", "y", "z"
    }

    if not required.issubset(df.columns):
        ax.set_title(f"{recording_id} - INVALID FORMAT")
        ax.axis("off")
        continue

    # Use only gravity-removed acceleration
    df = df[
        df["sensor_type"] == "linear_acceleration"
    ].copy()

    for col in ["timestamp_ns", "x", "y", "z"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=["timestamp_ns", "x", "y", "z"]
    ).sort_values("timestamp_ns")

    if df.empty:
        ax.set_title(f"{recording_id} - NO SENSOR DATA")
        ax.axis("off")
        continue

    # Convert timestamp to seconds
    time = (
        df["timestamp_ns"].to_numpy(dtype=float)
        - float(df["timestamp_ns"].iloc[0])
    ) / 1e9

    # Calculate acceleration magnitude
    magnitude = np.sqrt(
        df["x"].to_numpy() ** 2
        + df["y"].to_numpy() ** 2
        + df["z"].to_numpy() ** 2
    )

    # Plot acceleration
    ax.plot(
        time,
        magnitude,
        linewidth=0.8,
        label="Acceleration magnitude"
    )

    # Plot threshold lines
    ax.axhline(
        0.30,
        linestyle="--",
        linewidth=1.2,
        label="0.30 m/s²"
    )

    ax.axhline(
        1.00,
        linestyle=":",
        linewidth=1.2,
        label="1.00 m/s²"
    )

    # Highlight readings above 0.30
    ax.fill_between(
        time,
        0.30,
        magnitude,
        where=magnitude > 0.30,
        alpha=0.20
    )

    ax.set_title(
        f"{recording_id} - {description}"
    )

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Acceleration magnitude (m/s²)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    print(
        f"{recording_id}: {len(magnitude)} samples | "
        f"Maximum: {np.max(magnitude):.3f} m/s²"
    )

# Overall graph title
fig.suptitle(
    "RoadSense - Acceleration Threshold Comparison",
    fontsize=16
)

fig.tight_layout()

# Save visualization
output_path = (
    OUTPUT_DIR / "threshold_comparison_visualization.png"
)

fig.savefig(output_path, dpi=150)
plt.close(fig)

print("\n" + "=" * 65)
print("VISUALIZATION COMPLETED")
print(f"Saved at: {output_path}")
print("=" * 65)
