# Autonomous Driving Annotation Pipeline (PoC)

## Overview

This Proof of Concept (PoC) demonstrates an automated **multi-sensor data annotation pipeline** for autonomous driving datasets.

The system integrates **camera and LiDAR sensors** to automatically generate **3D object annotations**.

The pipeline performs:

* Camera frame extraction
* Object detection using deep learning
* Sensor timestamp alignment
* LiDAR point cloud decoding
* Camera–LiDAR sensor fusion
* LiDAR point clustering
* Automatic 3D bounding box generation
* Annotation file creation

The final output is a **machine-generated annotation dataset** that can be used to train **ADAS perception models**.

---

# Dataset

Dataset Source
NVIDIA PhysicalAI Autonomous Vehicles Dataset

Developer Toolkit
[https://github.com/NVlabs/physical_ai_av](https://github.com/NVlabs/physical_ai_av)

Dataset Link
[https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)

## Dataset Characteristics

| Attribute          | Value         |
| ------------------ | ------------- |
| Total driving data | 1700 hours    |
| Clips              | 306,152       |
| Clip duration      | 20 seconds    |
| Camera FPS         | 30 FPS        |
| LiDAR frequency    | 10 Hz         |
| Number of cameras  | 7             |
| Radar sensors      | Up to 10      |
| LiDAR              | 360° rotating |
| Dataset size       | ~100 TB       |

For this PoC we use **a small subset of the dataset**.

---

# System Architecture

Pipeline Overview

Camera Video
↓
Frame Extraction
↓
Object Detection (YOLO)
↓
Timestamp Alignment
↓
LiDAR Decoding
↓
LiDAR → Camera Projection
↓
Sensor Fusion
↓
LiDAR Object Extraction
↓
LiDAR Clustering
↓
3D Bounding Box Generation
↓
Annotation File Creation

---

# Project Structure

```
qualcomm_poc_autonomous-driving-annotation-pipeline

data_source
    calibration
    camera
    lidar
    metadata
    labels

src
    data_loader
    preprocessing
    detection
    fusion
    projection
    clustering
    labeling
    visualization

outputs

docs
```

---

# Milestone 1 — Frame Extraction

## Objective

Convert raw camera video into image frames for perception models.

## File Location

src/preprocessing/frame_extraction.py

## Input

Camera video clips

```
data_source/camera/*.mp4
```

Example

```
camera_front_wide_120fov.chunk_0000.zip
```

Each clip

* Duration = 20 seconds
* Frame rate = 30 FPS

Total frames per clip

```
frames = duration × fps
frames = 20 × 30
frames = 600
```

For three cameras

```
600 × 3 = 1800 frames
```

For PoC we only extract **first 50 frames per camera**.

PoC subset

```
50 × 3 = 150 frames
```

## Output

```
outputs/frames/

front_wide/
cross_left/
cross_right/
```

Example

```
frame_000.jpg
frame_001.jpg
```

## Usage in Next Stage

These frames are used as input for **object detection models**.

---

# Milestone 2 — Clip Synchronization

## Objective

Ensure camera and LiDAR sensors correspond to the **same driving clip**.

## File Location

src/data_loader/clip_selector.py

## Input

```
metadata/sensor_presence.parquet
```

## Process

Select clips that contain all required sensors

Required sensors

* camera_front_wide
* camera_cross_left
* camera_cross_right
* lidar_top_360fov

## Output

Valid synchronized clip IDs

Example

```
0a948f59-0a06-41a2-8e20-ac3a39ff4d61
```

## Usage

The selected clip becomes the **master clip ID for the pipeline**.

---

# Milestone 3 — Camera Object Detection

## Objective

Detect road objects from camera frames.

## File Location

src/detection/camera_object_detection.py

## Model

YOLOv8

Installation

```
pip install ultralytics
```

## Input

```
outputs/frames/*.jpg
```

## Process

Deep neural network performs

```
image → convolution layers → bounding boxes
```

Each detection contains

* class label
* confidence score
* bounding box coordinates

Bounding box format

```
(x1, y1, x2, y2)
```

## Output

Detection images

```
outputs/camera_detections/
```

Detection metadata

```
outputs/detection_json/
```

Example JSON

```
{
 "class": "car",
 "confidence": 0.91,
 "bbox": [512,410,620,480]
}
```

## Usage

Bounding boxes are used to locate objects in LiDAR space.

---

# Milestone 4 — Timestamp Alignment

## Objective

Align camera frames with LiDAR scans.

## File Location

src/preprocessing/timestamp_alignment.py

## Input

Camera timestamps

```
camera_*_timestamps.parquet
```

LiDAR timestamps

```
lidar_top_360fov.parquet
```

## Process

Find closest LiDAR scan for each camera frame.

Time difference formula

```
Δt = |T_camera − T_lidar|
```

Select LiDAR scan with minimum difference.

## Output

```
outputs/sensor_alignment/alignment_table.csv
```

Example

| camera_frame | lidar_spin |
| ------------ | ---------- |
| 0            | 0          |
| 5            | 1          |

## Usage

Ensures **camera frames and LiDAR scans represent the same moment**.

---

# Milestone 5 — LiDAR Decoding

## Objective

Decode compressed LiDAR data.

## File Location

src/preprocessing/lidar_decoding.py

## Input

Compressed LiDAR data

```
draco_encoded_pointcloud
```

## Process

Use Draco decoder

```
DracoPy.decode()
```

Output format

```
[x, y, z]
```

Example

```
(310000 points, 3)
```

## Output

3D point cloud representing the environment.

## Usage

Used for spatial reasoning and 3D object detection.

---

# Milestone 6 — LiDAR to Camera Projection

## Objective

Project LiDAR points onto camera image plane.

## File Location

src/projection/lidar_to_camera_projection.py

## Inputs

* LiDAR points
* Camera intrinsics
* Sensor extrinsics

## Mathematical Model

Projection equation

```
u = fx * (X/Z) + cx
v = fy * (Y/Z) + cy
```

Where

```
(X,Y,Z) = LiDAR 3D coordinates
(u,v) = pixel coordinates
```

Coordinate transformation

```
P_camera = R * P_lidar + T
```

Where

* R = rotation matrix
* T = translation vector

## Output

LiDAR points projected onto the camera image.

## Usage

Allows LiDAR data to align with camera detections.

---

# Milestone 7 — Sensor Fusion

## Objective

Combine camera perception with LiDAR geometry.

Fusion approach

```
camera detection
        +
lidar depth
        ↓
3D object understanding
```

## Process

For each detected bounding box

1. Identify LiDAR points inside the bounding box
2. Associate those points with the detected object

## Output

LiDAR points corresponding to each detected object.

---

# Milestone 8 — LiDAR Point Clustering

## Objective

Separate object points from background noise.

## File Location

src/clustering/lidar_point_clustering.py

## Algorithm

DBSCAN clustering

Installation

```
pip install scikit-learn
```

## Mathematical Concept

Density-based clustering.

A point is a **core point** if it has at least `min_samples` neighbors within radius `eps`.

Typical parameters

```
eps = 1.5
min_samples = 8
```

## Output

Clusters representing individual objects.

---

# Milestone 9 — 3D Bounding Box Generation

## Objective

Generate 3D object annotations.

## File Location

src/labeling/generate_3d_bbox.py

## Process

Compute spatial limits

```
xmin = min(x)
xmax = max(x)
ymin = min(y)
ymax = max(y)
zmin = min(z)
zmax = max(z)
```

Dimensions

```
length = xmax − xmin
width  = ymax − ymin
height = zmax − zmin
```

Bounding box center

```
center_x = (xmin + xmax) / 2
center_y = (ymin + ymax) / 2
center_z = (zmin + zmax) / 2
```

## Output

3D bounding box parameters.

---

# Milestone 10 — Annotation Generation

## Objective

Generate machine-readable label files.

## Output

```
outputs/lidar_annotations/frame_000.json
```

Example

```
{
 "frame_id": "frame_000",
 "objects": [
  {
   "class": "car",
   "bbox_2d": [512,410,620,480],
   "bbox_3d": {
       "center": [3.4,-1.2,12.7],
       "dimensions": [4.2,1.8,1.6]
   },
   "num_lidar_points": 72
  }
 ]
}
```

## Usage

These annotations can be used to train

* 3D object detection models
* ADAS perception systems
* autonomous driving datasets

---

# Final Pipeline Summary

Video
↓
Frame Extraction
↓
Object Detection
↓
Timestamp Alignment
↓
LiDAR Decoding
↓
Sensor Fusion
↓
LiDAR Clustering
↓
3D Bounding Box
↓
Automatic Label Generation

---

# PoC Achievements

This PoC demonstrates

* automated camera-LiDAR annotation
* multi-sensor perception pipeline
* 3D object labeling generation
* scalable annotation workflow

The architecture can scale to

* millions of frames
* multi-camera fusion
* real-time labeling systems
 