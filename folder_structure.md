# Project Structure

The repository follows a modular architecture to support **multi-camera perception, sensor fusion, and automated annotation generation**.

```id="bt0uqh"
qualcomm_poc_autonomous-driving-annotation-pipeline
│
├── README.md
│
├── data_source
│   ├── calibration
│   │   ├── camera_intrinsics.chunk_0000.parquet
│   │   ├── sensor_extrinsics.chunk_0000.parquet
│   │   └── vehicle_dimensions.chunk_0000.parquet
│   │
│   ├── camera
│   │   ├── camera_front_wide_120fov.chunk_0000.zip
│   │   ├── camera_cross_left_120fov.chunk_0000.zip
│   │   └── camera_cross_right_120fov.chunk_0000.zip
│   │
│   ├── lidar
│   │   └── lidar_top_360fov.chunk_0000.zip
│   │
│   ├── labels
│   │   └── egomotion.chunk_0000.zip
│   │
│   └── metadata
│       ├── data_collection.parquet
│       └── sensor_presence.parquet
│
├── configs
│   ├── dataset_config.yaml
│   └── sensor_config.yaml
│
├── src
│   ├── data_loader
│   │   ├── load_camera.py
│   │   ├── load_lidar.py
│   │   ├── load_calibration.py
│   │   └── load_metadata.py
│   │
│   ├── preprocessing
│   │   ├── frame_extraction.py
│   │   ├── lidar_decoding.py
│   │   └── timestamp_alignment.py
│   │
│   ├── detection
│   │   └── camera_object_detection.py
│   │
│   ├── fusion
│   │   ├── multi_camera_fusion.py
│   │   └── sensor_fusion.py
│   │
│   ├── projection
│   │   └── lidar_to_camera_projection.py
│   │
│   ├── clustering
│   │   └── lidar_point_clustering.py
│   │
│   ├── labeling
│   │   └── generate_lidar_labels.py
│   │
│   └── visualization
│       ├── visualize_camera_detections.py
│       └── visualize_lidar_pointcloud.py
│
├── notebooks
│   ├── dataset_exploration.ipynb
│   └── sensor_fusion_demo.ipynb
│
├── outputs
│   ├── camera_detections
│   ├── fused_detections
│   └── lidar_annotations
│
└── docs
    ├── dataset_description.md
    ├── pipeline_workflow.md
    └── sensor_fusion_architecture.md
```

---

# Folder Explanation

## data_source

Stores the **raw dataset files** downloaded from the NVIDIA dataset.

Contains:

* calibration parameters
* camera videos
* LiDAR scans
* ego motion
* metadata

---

# src/data_loader

Responsible for **reading dataset files**.

Modules:

| Script              | Purpose                    |
| ------------------- | -------------------------- |
| load_camera.py      | read camera video          |
| load_lidar.py       | read LiDAR parquet         |
| load_calibration.py | load intrinsics/extrinsics |
| load_metadata.py    | read dataset metadata      |

---

# src/preprocessing

Handles raw data preparation.

| Script                 | Function                  |
| ---------------------- | ------------------------- |
| frame_extraction.py    | extract frames from video |
| lidar_decoding.py      | decode Draco point clouds |
| timestamp_alignment.py | synchronize sensors       |

---

# src/detection

Runs **camera-based object detection**.

Example models:

```
YOLOv8
Detectron2
Mask RCNN
```

Output:

```
2D bounding boxes
```

---

# src/fusion

Handles multi-sensor fusion.

Modules:

| Script                 | Function                               |
| ---------------------- | -------------------------------------- |
| multi_camera_fusion.py | merge detections from multiple cameras |
| sensor_fusion.py       | combine camera + LiDAR                 |

---

# src/projection

Transforms LiDAR points into camera coordinate space.

Uses:

```
camera_intrinsics
sensor_extrinsics
```

Output:

```
projected lidar points
```

---

# src/clustering

Clusters LiDAR points corresponding to objects.

Algorithms:

```
DBSCAN
Euclidean clustering
```

Output:

```
3D object clusters
```

---

# src/labeling

Generates **automatic LiDAR labels** using camera detections.

Process:

```
camera bbox
↓
lidar projection
↓
point clustering
↓
3D bounding box
```

---

# src/visualization

Used to visualize results.

Includes:

```
camera detections
lidar point cloud
fused detections
```

---

# outputs

Stores generated outputs.

Examples:

```
camera_detections
lidar_annotations
sensor_fusion_results
```

---

# notebooks

Exploratory notebooks for debugging and experiments.

Examples:

```
dataset exploration
sensor fusion experiments
```

---

# docs

Project documentation.

Includes:

```
dataset description
pipeline workflow
sensor fusion architecture
```

---

# First Milestones

We will implement modules in this order:

1️⃣ load LiDAR parquet
2️⃣ decode LiDAR point cloud
3️⃣ visualize LiDAR scan
4️⃣ extract camera frames
5️⃣ run YOLO detection
6️⃣ project LiDAR → camera
7️⃣ cluster LiDAR points
8️⃣ generate LiDAR labels

---

# PoC Goal

The PoC demonstrates:

```
multi-camera perception
+
sensor fusion
+
camera-assisted LiDAR annotation
```
