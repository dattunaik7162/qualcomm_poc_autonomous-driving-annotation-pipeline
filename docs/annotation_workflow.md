# Annotation Workflow – ADAS LiDAR Dataset

## 1. Overview

Annotation is the process of labeling objects in sensor data to create **ground truth datasets** for training autonomous driving perception models.

In this project, LiDAR point clouds and camera images are used to generate annotations such as:

* 3D bounding boxes
* object classes
* object positions
* tracking IDs

These annotations are later used to train machine learning models for object detection and perception tasks.

---

## 2. Annotation Pipeline

The annotation process follows a multi-stage workflow:

Raw Sensor Data
↓
LiDAR Decoding
↓
Point Cloud Generation
↓
Auto Pre-Labeling (ML Model)
↓
Human Annotation Review
↓
Ground Truth Dataset

---

## 3. Step 1 – Data Preprocessing

Before annotation can begin, the raw dataset must be prepared.

### Tasks performed

* Decode LiDAR packets
* Extract point clouds
* Load camera images
* Synchronize sensor frames
* Apply sensor calibration

This produces aligned **LiDAR + camera frames** for annotation.

---

## 4. Step 2 – Automatic Pre-Labeling

To reduce manual work, object detection models can generate **initial bounding boxes**.

Common models used:

* YOLO
* PointPillars
* CenterPoint
* SECOND

Example objects detected:

* Vehicles
* Pedestrians
* Cyclists
* Traffic signs

The output contains preliminary bounding boxes.

---

## 5. Step 3 – Human Annotation Review

Human annotators review and correct the automatically generated labels.

Typical annotation tasks include:

* adjusting bounding box dimensions
* correcting object class
* removing false positives
* adding missed objects

This step ensures high-quality labeled data.

---

## 6. Step 4 – 3D Bounding Box Creation

For LiDAR data, objects are labeled using **3D bounding boxes**.

Each box contains:

| Field    | Description     |
| -------- | --------------- |
| x        | object center X |
| y        | object center Y |
| z        | object center Z |
| width    | object width    |
| length   | object length   |
| height   | object height   |
| rotation | orientation     |
| class    | object category |

These boxes represent objects in **3D space**.

---

## 7. Step 5 – Annotation Storage

Annotations are typically stored in structured formats such as:

JSON

```json
{
  "frame_id": 101,
  "objects": [
    {
      "class": "vehicle",
      "bbox": [x, y, z, w, l, h],
      "rotation": 1.57
    }
  ]
}
```

or

KITTI / Waymo dataset formats.

---

## 8. Annotation Tools

Common tools used for LiDAR annotation include:

* CVAT
* Labelbox
* Supervisely
* Scale AI
* Amazon SageMaker Ground Truth

These tools support **3D point cloud labeling**.

---

## 9. Quality Assurance

To ensure annotation quality, the following validation steps are applied:

* multi-stage human review
* automated consistency checks
* object tracking validation
* dataset sampling audits

High-quality annotations are critical for reliable model training.

---

## 10. Output of Annotation Pipeline

Final output contains:

* labeled LiDAR frames
* 3D bounding boxes
* object classes
* timestamp alignment
* metadata for training

These datasets are then used to train perception models.

---

## 11. Future Improvements

Possible improvements for the annotation pipeline include:

* active learning for label suggestion
* semi-automatic labeling
* model-assisted annotation
* automated dataset validation
* scalable cloud-based labeling workflows
