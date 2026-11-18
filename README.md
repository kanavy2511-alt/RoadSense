
# RoadSense 🚗

### Smartphone-Based Road Disturbance Monitoring System

RoadSense is an experimental smartphone-based road monitoring project designed to analyse road disturbances using accelerometer sensor data.

The project combines Android-based sensor data collection with Python-powered signal processing and event analysis to explore how unusual road vibrations can be identified and studied.

## 🎯 Project Vision

The long-term vision of RoadSense is to develop a system capable of identifying unusual road disturbances and contributing towards smarter road condition monitoring through crowdsourced sensor data.

## 🏗️ Project Architecture

RoadSense currently consists of two major components:

### 1. Android Application

Located in `AndroidApp/`

- Collects smartphone accelerometer sensor data.
- Records acceleration measurements.
- Provides the mobile interface for data collection.
- Built using Kotlin and Android Studio.

### 2. Python Analysis Pipeline

Located in the repository root.

- Accelerometer data analysis.
- Signal processing and acceleration analysis.
- Peak detection using SciPy.
- Disturbance event grouping.
- Event duration estimation.
- Threshold comparison and validation.
- Data visualization and analysis reports.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Kotlin | Android application |
| Android Studio | Mobile development |
| Python | Data analysis |
| Pandas | Data processing |
| NumPy | Numerical computation |
| SciPy | Signal processing |
| Matplotlib | Data visualization |
| Git & GitHub | Version control |

## 📂 Repository Structure

```text
RoadSENSE/
│
├── AndroidApp/
│   ├── app/
│   │   └── src/
│   ├── gradle/
│   ├── build.gradle.kts
│   └── settings.gradle.kts
│
├── analysis_output/       # Generated locally; not tracked
├── Data/                  # Raw recordings; not tracked
│
├── first_analysis.py
├── event_detection.py
├── event_grouping.py
├── event_duration_analysis.py
├── event_visualization.py
├── event_visualization_graph.py
├── disturbance_baseline.py
├── threshold_comparison_visualization.py
├── threshold_persistence_analysis.py
├── analysis_audit.py
└── README.md
```

## ⚙️ Getting Started

### Android Application

1. Clone or download this repository.
2. Open the `AndroidApp` directory in Android Studio.
3. Allow Gradle to synchronize dependencies.
4. Connect a compatible Android device or start an emulator.
5. Build and run the application.

### Python Analysis

Install the required libraries:

```bash
pip install pandas numpy scipy matplotlib
```

Run an analysis script from the repository root:

```bash
python event_detection.py
```

Note: Raw sensor recordings are not included in the repository. You will need your own compatible CSV recordings.

## 🔬 Current Development Status

RoadSense is under active development.

Current experimental work includes:

- Smartphone sensor data collection.
- Acceleration magnitude analysis.
- Peak-based disturbance detection.
- Event grouping and duration estimation.
- Threshold comparison and persistence analysis.
- Visual validation of detected events.

## 🚀 Future Goals

- Improve disturbance classification.
- Distinguish potholes, speed breakers and other road disturbances.
- Improve detection reliability across different vehicles and smartphones.
- Integrate real-time disturbance alerts.
- Explore crowdsourced road condition mapping.
- Develop a scalable road monitoring system.

## ⚠️ Disclaimer

RoadSense is an experimental project. Its current detection algorithms are under development and have not been established as a reliable pothole detection or road safety system.

It should not be used as a substitute for safe driving practices or official road condition assessments.

## 👨‍💻 Project

**RoadSense — Smarter Roads Through Smartphone-Based Sensing**
