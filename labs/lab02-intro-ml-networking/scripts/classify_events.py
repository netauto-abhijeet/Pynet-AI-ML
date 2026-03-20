#!/usr/bin/env python3
"""
classify_events.py
Train a Random Forest classifier to categorise network events as:
  normal / warning / critical
Run collect_telemetry.py --sample first to generate data.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib

BASE = os.path.dirname(__file__)
DATA_DIR  = os.path.join(BASE, '..', 'data')
MODEL_DIR = os.path.join(BASE, '..', 'models')
OUT_DIR   = os.path.join(BASE, '..', 'outputs')

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    csv_path = os.path.join(DATA_DIR, 'network_events.csv')
    if not os.path.exists(csv_path):
        print('[!] Data not found. Run: python3 collect_telemetry.py --sample')
        return

    print('[*] Loading events data...')
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    print(f'    Rows: {len(df):,}')
    print('    Label distribution:\n', df['label'].value_counts())

    # Feature engineering
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    le_device = LabelEncoder()
    le_msg    = LabelEncoder()
    df['device_enc']  = le_device.fit_transform(df['device'])
    df['message_enc'] = le_msg.fit_transform(df['message'])

    FEATURES = ['severity', 'device_enc', 'message_enc', 'hour', 'day_of_week']
    df['severity'] = pd.to_numeric(df['severity'], errors='coerce').fillna(6)
    X = df[FEATURES]
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    print('\n[*] Training Random Forest classifier...')
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print('\n[*] Classification Report:')
    print(classification_report(y_test, y_pred))

    # Confusion matrix heatmap
    cm = confusion_matrix(y_test, y_pred, labels=['normal', 'warning', 'critical'])
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['normal', 'warning', 'critical'],
                yticklabels=['normal', 'warning', 'critical'], ax=ax)
    ax.set_title('Event Classifier — Confusion Matrix')
    ax.set_ylabel('Actual')
    ax.set_xlabel('Predicted')
    plt.tight_layout()
    chart = os.path.join(OUT_DIR, 'event_classifier_cm.png')
    plt.savefig(chart, dpi=120)
    print(f'[+] Confusion matrix saved to {chart}')

    # Feature importance
    fi = pd.Series(clf.feature_importances_, index=FEATURES).sort_values(ascending=True)
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    fi.plot(kind='barh', ax=ax2, color='steelblue')
    ax2.set_title('Feature Importance — Random Forest')
    plt.tight_layout()
    chart2 = os.path.join(OUT_DIR, 'feature_importance.png')
    plt.savefig(chart2, dpi=120)
    print(f'[+] Feature importance chart saved to {chart2}')

    # Save model and encoders
    joblib.dump(clf,       os.path.join(MODEL_DIR, 'event_classifier.pkl'))
    joblib.dump(le_device, os.path.join(MODEL_DIR, 'le_device.pkl'))
    joblib.dump(le_msg,    os.path.join(MODEL_DIR, 'le_message.pkl'))
    print('[+] Classifier and encoders saved to models/')


if __name__ == '__main__':
    main()
