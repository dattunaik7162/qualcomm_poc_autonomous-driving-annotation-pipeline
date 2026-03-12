Below is a **clean, professional `README.md`** you can paste directly into your GitHub repo.
It is structured like a **real ML / autonomous driving project README** and incorporates your **notes, dataset structure, and technical table**.

---

# Qualcomm PoC — Autonomous Driving Annotation Pipeline

This repository contains a **Proof of Concept (PoC)** for building an **Autonomous Driving Data Annotation Pipeline** using a multi-sensor dataset.

The PoC focuses on **camera-based annotation tasks** while also exploring **multi-camera perception and sensor fusion concepts** for autonomous driving systems.

The dataset used in this PoC is the **NVIDIA PhysicalAI Autonomous Vehicles Dataset**, which provides multi-sensor data including cameras, LiDAR, radar, calibration data, and vehicle motion metadata.

---

# Objectives

The primary objectives of this PoC are:

* Build a **camera-based annotation workflow**
* Support **ADAS perception labeling tasks**
* Understand **multi-camera object detection**
* Explore **sensor fusion workflows**
* Design a **scalable annotation pipeline architecture**

---

# Key Research Directions

### Multi-Camera Object Detection

Detect objects using multiple camera views.

Example:

```
front camera
rear camera
cross cameras
```

Multiple camera views observing the **same object** can improve detection accuracy.

---

### Multi-Sensor Object Detection

Combine multiple sensors for perception:

* Camera
* LiDAR
* Radar

Example:

```
Camera detects visual object
LiDAR provides 3D geometry
Radar provides velocity
```

This improves object detection reliability.

---

### Sensor Fusion

Sensor fusion enables combining different sensor modalities to detect objects more accurately.

Example fusion architecture:

```
Camera + LiDAR + Radar
        ↓
Sensor Fusion Model
        ↓
Unified Object Detection
```

---

### Multi-Camera Reconstruction

Concepts like **Gaussian Splatting** can reconstruct scenes from multiple cameras.

Applications include:

* 3D scene reconstruction
* spatial understanding
* environment modeling

---

# Dataset

Dataset used:

**NVIDIA PhysicalAI Autonomous Vehicles Dataset**

This dataset contains a large-scale collection of multi-sensor autonomous driving data.

---

# Dataset Statistics

| Attribute                  | Value      |
| -------------------------- | ---------- |
| Total Driving Duration     | 1700 hours |
| Total Clips                | 306,152    |
| Clip Duration              | 20 seconds |
| Camera Frame Rate          | 30 FPS     |
| Cameras per Vehicle        | 7          |
| Frames per Camera per Clip | 600        |
| Total Frames per Clip      | 4200       |
| LiDAR Frequency            | 10 Hz      |
| LiDAR Scans per Clip       | 200        |
| Radar Sensors              | Up to 10   |
| Dataset Size               | ~100 TB    |

---

# Dataset Directory Structure

```
dataset/

calibration/
    camera_intrinsics.chunk_0000.parquet
    sensor_extrinsics.chunk_0000.parquet
    vehicle_dimensions.chunk_0000.parquet

camera/
    camera_cross_left_120fov/
    camera_cross_right_120fov/
    camera_front_tele_30fov/
    camera_front_wide_120fov/
    camera_rear_left_70fov/
    camera_rear_right_70fov/
    camera_rear_tele_30fov/

labels/
    egomotion/

lidar/
    lidar_top_360fov/

metadata/
    data_collection.parquet
    sensor_presence.parquet

radar/
    radar_corner_front_left_srr_0/
    radar_corner_front_left_srr_3/
    radar_corner_front_right_srr_0/
    radar_corner_front_right_srr_3/
    radar_corner_rear_left_srr_0/
    radar_corner_rear_left_srr_3/
    radar_corner_rear_right_srr_0/
    radar_corner_rear_right_srr_3/
    radar_front_center_imaging_lrr_1/
    radar_front_center_mrr_2/
    radar_front_center_srr_0/
    radar_rear_left_mrr_2/
    radar_rear_left_srr_0/
    radar_rear_right_mrr_2/
    radar_rear_right_srr_0/
    radar_side_left_srr_0/
    radar_side_left_srr_3/
    radar_side_right_srr_0/
    radar_side_right_srr_3/
```

---

# Sensors Overview

| Sensor      | Description                   | Frequency         |
| ----------- | ----------------------------- | ----------------- |
| Camera      | RGB visual perception         | 30 FPS            |
| LiDAR       | 3D point cloud sensing        | 10 Hz             |
| Radar       | Object detection and velocity | sensor dependent  |
| Ego Motion  | Vehicle pose and movement     | timestamp aligned |
| Calibration | Camera and sensor parameters  | static            |

---

# Camera Sensors

| Camera                    | Field of View | Position         |
| ------------------------- | ------------- | ---------------- |
| camera_front_wide_120fov  | 120°          | Front            |
| camera_front_tele_30fov   | 30°           | Front telephoto  |
| camera_cross_left_120fov  | 120°          | Left cross view  |
| camera_cross_right_120fov | 120°          | Right cross view |
| camera_rear_left_70fov    | 70°           | Rear left        |
| camera_rear_right_70fov   | 70°           | Rear right       |
| camera_rear_tele_30fov    | 30°           | Rear telephoto   |

---

# Annotation Tasks

The following annotation tasks are supported.

### 2D Bounding Boxes

Object detection labels for:

* car
* truck
* pedestrian
* cyclist
* traffic light
* traffic sign

---

### Instance Segmentation

Pixel-level segmentation for individual objects.

Example:

* vehicle masks
* pedestrian masks

---

### Semantic Segmentation

Pixel classification for scene understanding.

Example classes:

* road
* sidewalk
* vehicles
* pedestrians
* buildings
* vegetation

---

### Lane Marking Annotation

Detect lane structures such as:

* left lane
* right lane
* lane boundaries
* center lanes

---

### Traffic Sign and Signal Detection

Annotate infrastructure elements such as:

* traffic lights
* stop signs
* speed limit signs
* yield signs

---

# Calibration Data

Calibration data includes camera intrinsic parameters.

Example parameters:

| Parameter | Description                      |
| --------- | -------------------------------- |
| width     | image width                      |
| height    | image height                     |
| cx        | principal point x                |
| cy        | principal point y                |
| fw_poly   | forward distortion coefficients  |
| bw_poly   | backward distortion coefficients |

These parameters are used for:

* camera undistortion
* sensor projection
* sensor fusion

---

# Sensor Extrinsics

Extrinsic parameters define sensor placement relative to the vehicle.

| Parameter   | Description         |
| ----------- | ------------------- |
| qx qy qz qw | quaternion rotation |
| x y z       | sensor position     |

Vehicle coordinate system:

| Axis | Direction |
| ---- | --------- |
| X    | forward   |
| Y    | left      |
| Z    | upward    |

Origin: center of rear axle projected to ground.

---

# Ego Motion

Ego motion describes vehicle movement.

| Field     | Description            |
| --------- | ---------------------- |
| timestamp | measurement time       |
| x y z     | vehicle position       |
| vx vy vz  | velocity               |
| ax ay az  | acceleration           |
| curvature | vehicle path curvature |

---

# Radar Data

Radar provides motion and distance measurements.

| Field           | Description                |
| --------------- | -------------------------- |
| azimuth         | horizontal detection angle |
| elevation       | vertical detection angle   |
| distance        | object distance            |
| radial_velocity | object velocity            |
| rcs             | radar cross section        |
| snr             | signal to noise ratio      |

Radar is primarily used for:

* object tracking
* motion detection
* sensor fusion

---

# Multi-Sensor Fusion

Combining sensors improves perception accuracy.

Example architecture:

```
Camera Data
     +
LiDAR Point Cloud
     +
Radar Detection
        ↓
Sensor Fusion Model
        ↓
Unified Object Detection
```

---

# Future Work

Future improvements for this PoC include:

* LiDAR annotation pipeline
* radar-assisted detection
* sensor fusion models
* multi-camera 3D reconstruction
* automated labeling pipelines

---

# References

NVIDIA PhysicalAI Autonomous Vehicles Dataset

## Developer Toolkit and Dataset

The dataset and tools used in this PoC are available at the following resources.

### NVIDIA PhysicalAI Autonomous Vehicles Dataset

Hugging Face dataset:

https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles

This dataset provides a large-scale multi-sensor autonomous driving dataset including:

- 7 camera sensors
- LiDAR point clouds
- Radar sensors
- Ego motion data
- Calibration parameters

Total dataset scale:

- 1700 hours of driving
- 306,152 clips
- 20 seconds per clip
- ~100 TB dataset size

---

### NVIDIA Developer Toolkit

GitHub repository:

https://github.com/NVlabs/physical_ai_av

The toolkit provides utilities to:

- Load dataset clips
- Decode sensor data
- Handle multi-sensor synchronization
- Process camera, LiDAR, and radar data

Example installation:

```bash
pip install physical_ai_av