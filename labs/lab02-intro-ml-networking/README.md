# Lab 02 — Introduction to AI/ML for Network Engineers

## Objective
Learn foundational AI/ML concepts and apply them to real network data using Python. By the end of this lab you will be able to:

- Load and explore network telemetry data with **pandas**
- Visualize interface/device statistics with **matplotlib** and **seaborn**
- Build a simple **anomaly detection** model using scikit-learn (Isolation Forest)
- Classify network events using a **Random Forest** classifier
- Save and reload trained models for inference

## Lab Structure

```
lab02-intro-ml-networking/
├── README.md
├── requirements.txt
├── data/                   # Input CSVs / raw telemetry
├── notebooks/              # Step-by-step Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_anomaly_detection.ipynb
│   └── 03_event_classification.ipynb
├── scripts/                # Standalone Python scripts
│   ├── collect_telemetry.py     # Collect data from network devices
│   ├── train_anomaly_model.py   # Train Isolation Forest model
│   └── classify_events.py       # Train + run Random Forest classifier
├── models/                 # Saved .pkl model files (gitignored)
└── outputs/                # Charts, reports (gitignored)
```

## Concepts Covered

| Concept | Tool | Network Use Case |
|---------|------|-----------------|
| Data wrangling | pandas | Parse interface stats, syslog, routing tables |
| Visualisation | matplotlib/seaborn | Bandwidth graphs, heatmaps |
| Anomaly detection | Isolation Forest (sklearn) | Detect unusual traffic spikes |
| Classification | Random Forest (sklearn) | Classify log events (normal/warning/critical) |
| Model persistence | joblib | Save trained model, reload for live inference |

## How to Run

### 1. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Generate sample data (no devices needed)
```bash
python3 scripts/collect_telemetry.py --sample
```

### 3. Train anomaly detection model
```bash
python3 scripts/train_anomaly_model.py
```

### 4. Classify network events
```bash
python3 scripts/classify_events.py
```

### 5. Open Jupyter notebooks
```bash
jupyter notebook notebooks/
```

## Sample Data Format

`data/interface_stats.csv` — interface counters collected every 5 minutes:
```
timestamp,device,interface,in_bps,out_bps,in_errors,out_errors,utilization_pct
2024-01-01 00:00:00,R1,Gi0/0,1500000,980000,0,0,14.3
```

`data/network_events.csv` — syslog/event feed:
```
timestamp,device,severity,message,label
2024-01-01 00:01:00,R1,5,Interface up,normal
```
