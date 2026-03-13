# Dataset Structure – Qualcomm ADAS LiDAR Dataset

## 1. Overview

The dataset used in this project contains **multi-sensor autonomous driving data**, including LiDAR point clouds, camera images, and sensor calibration parameters.

The data is stored in **Parquet format**, which enables efficient storage and fast reading of large sensor datasets.

The dataset is organized into logical folders based on sensor type.

---

## 2. Dataset Folder Structure

```text
data_source
│
├── lidar
│   ├── lidar_packets.chunk_0000.parquet
│   ├── lidar_packets.chunk_0001.parquet
│
├── camera
│   ├── camera_images.chunk_0000.parquet
│   ├── camera_images.chunk_0001.parquet
│
├── calibration
│   ├── camera_intrinsics.chunk_0000.parquet
│   ├── sensor_extrinsics.chunk_0000.parquet
```

Each folder corresponds to a specific sensor or metadata source.

---

## 3. LiDAR Data

### Location

```
data_source/lidar/
```

### File Format

```
.parquet
```

### Description

The LiDAR files contain **compressed LiDAR packets** that represent 3D point clouds captured by the LiDAR sensor.

These packets are compressed using **Draco compression**, which reduces storage size.

### Key Fields

Typical LiDAR packet fields include:

| Field        | Description             |
| ------------ | ----------------------- |
| frame_id     | Frame identifier        |
| timestamp    | Sensor timestamp        |
| lidar_packet | Compressed LiDAR data   |
| sensor_id    | LiDAR sensor identifier |

### Processing

LiDAR packets must be decoded using the **Draco decoder (`dracopy`)** before extracting the point cloud.

---

## 4. Camera Data

### Location

```
data_source/camera/
```

### File Format

```
.parquet
```

### Description

Camera files store image frames captured by vehicle cameras.

These images are synchronized with LiDAR frames and used for **sensor fusion**.

### Key Fields

| Field      | Description              |
| ---------- | ------------------------ |
| frame_id   | Frame identifier         |
| timestamp  | Image capture time       |
| camera_id  | Camera sensor identifier |
| image_data | Encoded image bytes      |

### Processing

Images can be decoded and converted into standard image formats for visualization or training.

---

## 5. Calibration Data

### Location

```
data_source/calibration/
```

### Description

Calibration files define the spatial relationship between sensors.

These parameters allow transformation between coordinate systems.

Two important calibration files are included:

#### Camera Intrinsics

Defines internal camera parameters:

* focal length
* optical center
* distortion parameters

#### Sensor Extrinsics

Defines transformation between sensors:

* LiDAR → Camera
* Camera → Vehicle frame

This allows projecting LiDAR points into camera images.

---

## 6. Data Processing Flow

Dataset processing follows this sequence:

Raw Dataset
↓
Read Parquet Files
↓
Decode LiDAR Packets (Draco)
↓
Extract Point Cloud Data
↓
Apply Calibration
↓
Visualization / Annotation

---

## 7. Typical Frame Processing

For each frame:

1. Read LiDAR packet
2. Decode compressed data
3. Extract point cloud
4. Read camera image
5. Align using calibration parameters
6. Visualize or annotate objects

---

## 8. Dataset Challenges

Autonomous driving datasets typically contain:

* large data volumes
* compressed sensor packets
* multi-sensor synchronization requirements

Efficient preprocessing pipelines are required to handle these challenges.

---

## 9. Next Steps
