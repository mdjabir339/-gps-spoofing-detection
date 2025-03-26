# -gps-spoofing-detection

# 🚢 GPS Spoofing Detection with Parallel Computing

This project analyzes AIS (Automatic Identification System) vessel tracking data to detect potential **GPS spoofing** events. It utilizes **Python parallel processing** to enhance performance and demonstrates how execution time scales with the number of CPUs.

---

## 🎯 Objective

Detect anomalies in maritime GPS data that indicate spoofing attacks by:

- Identifying sudden, unrealistic position jumps
- Detecting impossible vessel speeds (>1000 km/h)
- Evaluating performance of parallel vs sequential processing

---

## 🛠 Technologies Used

- Python 3
- pandas
- geopy (for geodesic distance)
- matplotlib
- concurrent.futures (with `ProcessPoolExecutor`)

---

## 🚀 How to Run

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/gps-spoofing-detection.git
cd gps-spoofing-detection
