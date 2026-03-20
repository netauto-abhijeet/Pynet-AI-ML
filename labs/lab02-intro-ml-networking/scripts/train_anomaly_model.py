#!/usr/bin/env python3
"""
train_anomaly_model.py
Train an Isolation Forest model to detect anomalous interface behaviour.
Run collect_telemetry.py --sample first to generate data.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

BASE = os.path.dirname(__file__)
DATA_DIR  = os.path.join(BASE, '..', 'data')
MODEL_DIR = os.path.join(BASE, '..', 'models')
OUT_DIR   = os.path.join(BASE, '..', 'outputs')

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

FEATURES = ['in_bps', 'out_bps', 'in_errors', 'out_errors', 'utilization_pct']


def main():
    csv_path = os.path.join(DATA_DIR, 'interface_stats.csv')
    if not os.path.exists(csv_path):
        print('[!] Data not found. Run: python3 collect_telemetry.py --sample')
        return

    print('[*] Loading data...')
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    print(f'    Rows: {len(df):,}  |  Columns: {list(df.columns)}')
    print(df[FEATURES].describe().round(2))

    print('\n[*] Scaling features...')
    scaler = StandardScaler()
    X = scaler.fit_transform(df[FEATURES])

    print('[*] Training Isolation Forest (contamination=0.05)...')
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    df['anomaly_score'] = model.fit_predict(X)
    df['is_anomaly'] = df['anomaly_score'] == -1

    n_anomalies = df['is_anomaly'].sum()
    print(f'    Detected anomalies: {n_anomalies} / {len(df)} rows '
          f'({n_anomalies/len(df)*100:.1f}%)')

    # Plot anomalies per device
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle('Interface Anomaly Detection — Isolation Forest', fontsize=14)

    for ax, device in zip(axes.flat, df['device'].unique()):
        d = df[df['device'] == device]
        normal = d[~d['is_anomaly']]
        anomal = d[d['is_anomaly']]
        ax.scatter(normal['timestamp'], normal['utilization_pct'],
                   s=5, alpha=0.4, label='Normal')
        ax.scatter(anomal['timestamp'], anomal['utilization_pct'],
                   s=20, color='red', alpha=0.8, label='Anomaly')
        ax.set_title(device)
        ax.set_ylabel('Utilization %')
        ax.legend(fontsize=7)

    plt.tight_layout()
    chart = os.path.join(OUT_DIR, 'anomaly_detection.png')
    plt.savefig(chart, dpi=120)
    print(f'\n[+] Chart saved to {chart}')

    # Save model + scaler
    joblib.dump(model,  os.path.join(MODEL_DIR, 'isolation_forest.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
    print('[+] Model and scaler saved to models/')

    # Save anomaly rows
    anomalies_csv = os.path.join(OUT_DIR, 'anomalies.csv')
    df[df['is_anomaly']].to_csv(anomalies_csv, index=False)
    print(f'[+] Anomaly records saved to {anomalies_csv}')


if __name__ == '__main__':
    main()
