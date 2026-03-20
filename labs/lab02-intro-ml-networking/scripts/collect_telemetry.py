#!/usr/bin/env python3
"""
collect_telemetry.py
Collect interface stats from network devices via Netmiko,
or generate sample data with --sample flag (no devices needed).
"""
import argparse
import csv
import random
import os
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

DEVICES = ['R1', 'R2', 'R3', 'R4']
INTERFACES = ['Gi0/0', 'Gi0/1', 'Gi0/2']


def generate_sample_data(rows=500):
    """Generate synthetic interface telemetry CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, 'interface_stats.csv')

    base_time = datetime(2024, 1, 1)
    with open(out_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'device', 'interface',
                         'in_bps', 'out_bps', 'in_errors', 'out_errors',
                         'utilization_pct'])
        for i in range(rows):
            ts = base_time + timedelta(minutes=5 * i)
            for device in DEVICES:
                for intf in INTERFACES:
                    # Inject anomalies ~5% of the time
                    anomaly = random.random() < 0.05
                    in_bps = random.randint(5_000_000, 50_000_000) if anomaly else random.randint(500_000, 5_000_000)
                    out_bps = random.randint(3_000_000, 30_000_000) if anomaly else random.randint(300_000, 3_000_000)
                    in_err = random.randint(50, 500) if anomaly else random.randint(0, 5)
                    out_err = random.randint(10, 100) if anomaly else 0
                    util = round((in_bps + out_bps) / 200_000_000 * 100, 2)
                    writer.writerow([ts, device, intf, in_bps, out_bps,
                                     in_err, out_err, util])

    print(f'[+] Sample data written to {out_file}')

    # Also generate events CSV
    events_file = os.path.join(OUTPUT_DIR, 'network_events.csv')
    severities = [('7', 'debug', 'normal'), ('6', 'informational', 'normal'),
                  ('5', 'notice', 'normal'), ('4', 'warning', 'warning'),
                  ('3', 'error', 'critical'), ('2', 'critical', 'critical')]
    messages = {
        'normal': ['Interface up', 'Neighbor established', 'Config saved', 'Route added'],
        'warning': ['High CPU utilization', 'Interface flap detected', 'Memory threshold reached'],
        'critical': ['Interface down', 'BGP session dropped', 'Routing loop detected', 'Link failure']
    }
    with open(events_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'device', 'severity', 'message', 'label'])
        for i in range(rows):
            ts = base_time + timedelta(minutes=random.randint(0, 60 * 24 * 30))
            device = random.choice(DEVICES)
            sev_num, sev_name, label = random.choices(
                severities, weights=[5, 20, 30, 25, 10, 10])[0]
            msg = random.choice(messages[label])
            writer.writerow([ts, device, sev_num, msg, label])
    print(f'[+] Events data written to {events_file}')


def collect_from_devices(inventory_file):
    """Collect live data using Netmiko (requires devices reachable)."""
    from netmiko import ConnectHandler
    import yaml
    with open(inventory_file) as f:
        inventory = yaml.safe_load(f)
    # TODO: implement live collection
    print('[!] Live collection not yet implemented — run with --sample for now')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Network telemetry collector')
    parser.add_argument('--sample', action='store_true',
                        help='Generate synthetic sample data (no devices needed)')
    parser.add_argument('--inventory', default='../inventory/hosts.yaml',
                        help='Inventory file for live collection')
    args = parser.parse_args()

    if args.sample:
        generate_sample_data()
    else:
        collect_from_devices(args.inventory)
