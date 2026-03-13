# Qualcomm ADAS LiDAR Annotation Pipeline (PoC)

## 1. Project Overview

This Proof-of-Concept demonstrates an automated pipeline for processing and annotating LiDAR sensor data for autonomous driving applications. The pipeline decodes compressed LiDAR packets, processes point cloud data, and prepares the data for annotation and visualization.

The goal of this project is to simulate an **ADAS data processing workflow similar to those used in autonomous driving companies**.

Key capabilities:

* Decode LiDAR point cloud data stored in parquet format
* Convert compressed data using Draco decoding
* Prepare point cloud data for annotation
* Enable visualization of LiDAR frames
* Build a scalable preprocessing pipeline for autonomous driving datasets

---

## 2. System Architecture

Raw Sensor Data
↓
Parquet Files (Compressed LiDAR Packets)
↓
Draco Decoding (`dracopy`)
↓
Point Cloud Extraction (XYZ + Intensity)
↓
Preprocessing Pipeline
↓
Annotation / Visualization

---

## 3. Project Structure

```
qual-poc1
│
├── README.md
├── requirements.txt
│
├── data_source
│   ├── lidar
│   │   ├── lidar_packets.chunk_0000.parquet
│   │
│   ├── camera
│   │   ├── camera_images.chunk_0000.parquet
│   │
│   ├── calibration
│   │   ├── camera_intrinsics.parquet
│   │   ├── sensor_extrinsics.parquet
│
├── src
│   ├── preprocessing
│   │   ├── lidar_decoding.py
│   │   ├── camera_decoding.py
│   │
│   ├── utils
│   │   ├── lidar_utils.py
│   │   ├── visualization.py
│
└── docs
    ├── lidar_pipeline.md
    ├── dataset_structure.md
```

---

## 4. Environment Setup

Create Python virtual environment:

```
python -m venv venv
```

Activate environment:

Windows

```
venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Important packages used:

* numpy
* pandas
* pyarrow
* dracopy
* open3d
* tqdm

---

## 5. LiDAR Decoding Workflow

The LiDAR dataset contains compressed point cloud packets stored in parquet files.

### Step 1 — Load parquet file

LiDAR packets are read using **PyArrow**.

### Step 2 — Decode Draco compressed data

Draco compression is used to efficiently store point cloud data.

```
dracopy.decode(...)
```

This converts compressed binary data into raw point cloud coordinates.

### Step 3 — Extract point cloud attributes

The following attributes are extracted:

* X coordinate
* Y coordinate
* Z coordinate
* Intensity
* Laser ring

### Step 4 — Convert to numpy format

The decoded data is converted to a NumPy array for further processing.

### Step 5 — Save / visualize point cloud

The output can be visualized using Open3D.

---

## 6. Running the Pipeline

Run LiDAR decoding module:

```
python src/preprocessing/lidar_decoding.py
```

Expected output:

* decoded LiDAR frames
* processed point cloud arrays
* optional visualization output

---

## 7. Visualization

LiDAR point cloud can be visualized using **Open3D**.

Example output:

* 3D point cloud visualization
* sensor perspective view
* object clusters visible

This is commonly used for debugging ADAS datasets.

---

## 8. Future Improvements

Possible extensions for this pipeline:

* Automated 3D bounding box generation
* Integration with annotation tools
* Multi-sensor fusion (LiDAR + Camera)
* Dataset quality validation
* Distributed processing for large datasets

---

## 9. Use Cases

This pipeline can be used for:

* Autonomous Driving dataset preprocessing
* LiDAR sensor debugging
* ADAS perception model training
* Data annotation pipelines

---

## 10. References

* Qualcomm Autonomous Driving Dataset
* Draco Compression Library
* Open3D Visualization Framework
* PyArrow Parquet Processing
