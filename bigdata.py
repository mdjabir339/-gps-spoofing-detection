import pandas as pd
import numpy as np
import time
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# === Step 1: Load AIS CSV ===
csv_path = r"C:\Users\mdjab\Downloads\PythonProject\aisdk-2025-01-27\aisdk-2025-01-27.csv"

print("📦 Loading AIS data...")
df_iter = pd.read_csv(csv_path, chunksize=1000000)
df_list = []

for chunk in df_iter:
    chunk = chunk.rename(columns=lambda x: x.strip())
    chunk = chunk[chunk['Latitude'].notnull() & chunk['Longitude'].notnull()]
    chunk = chunk[(chunk['Latitude'] >= -90) & (chunk['Latitude'] <= 90)]
    chunk = chunk[(chunk['Longitude'] >= -180) & (chunk['Longitude'] <= 180)]
    df_list.append(chunk)

df = pd.concat(df_list)
df = df.sort_values(['MMSI', '# Timestamp'])
print(f"✔️ Loaded {len(df):,} records.")

# === Step 2: Define spoofing logic ===
def detect_spoofing(group_df):
    mmsi = group_df['MMSI'].iloc[0]
    anomalies = []
    prev_point = None

    for _, row in group_df.iterrows():
        current_point = (row['Latitude'], row['Longitude'])
        current_time = row['# Timestamp']

        if prev_point:
            distance_km = geodesic(prev_point, current_point).km
            time_diff = 1 / 60
            speed = distance_km / time_diff if time_diff else 0
            if distance_km > 100 or speed > 1000:
                anomalies.append((mmsi, current_time, distance_km, speed))

        prev_point = current_point

    return anomalies

# === Step 3: Processing functions ===
def process_sequential(df):
    anomalies = []
    for _, group in df.groupby('MMSI'):
        anomalies.extend(detect_spoofing(group))
    return anomalies

def process_parallel(df, workers):
    vessel_groups = [group for _, group in df.groupby('MMSI')]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(detect_spoofing, vessel_groups)
    return [item for sublist in results for item in sublist]

# === Step 4: Run sequential once ===
print("\n⏳ Running sequential processing...")
start_seq = time.time()
seq_anomalies = process_sequential(df)
end_seq = time.time()
sequential_time = end_seq - start_seq
print(f"✅ Sequential time: {sequential_time:.2f} seconds")

# === Step 5: Test parallel with varying CPU counts ===
cpu_counts = [2, 4, 6, 8]
parallel_times = []

print("\n⚙️ Testing parallel with different CPU counts:")
for count in cpu_counts:
    print(f" - {count} CPUs...")
    start = time.time()
    process_parallel(df, workers=count)
    end = time.time()
    time_taken = end - start
    parallel_times.append(time_taken)
    print(f"   Time: {time_taken:.2f} seconds")

# === Step 6: Save anomalies CSV ===
output_csv = "anomalies_detected.csv"
pd.DataFrame(seq_anomalies, columns=["MMSI", "Timestamp", "Distance(km)", "Speed(km/h)"]).to_csv(output_csv, index=False)
print(f"\n📁 Anomalies saved to: {output_csv}")

# === Step 7: Plot and auto-open performance chart ===
plt.figure(figsize=(8, 5))
plt.plot(cpu_counts, parallel_times, marker='o', label="Parallel Time")
plt.axhline(y=sequential_time, color='red', linestyle='--', label="Sequential Time")
plt.title("Parallel Execution Time vs. CPU Count")
plt.xlabel("Number of CPUs")
plt.ylabel("Execution Time (seconds)")
plt.legend()
plt.grid(True)
plt.tight_layout()

chart_path = "cpu_scaling_chart.png"
plt.savefig(chart_path)
plt.close()
print(f"📊 Chart saved as: {chart_path}")

# === Auto-open chart on Windows ===
try:
    os.startfile(chart_path)
except:
    print("🔔 Chart saved but could not auto-open (non-Windows system?)")

print("✅ Done!")
