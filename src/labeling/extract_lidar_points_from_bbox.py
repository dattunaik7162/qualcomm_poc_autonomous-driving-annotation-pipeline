import json
import numpy as np
import pyarrow.parquet as pq
import DracoPy
from scipy.spatial.transform import Rotation as R
import os

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

FUSED_DETECTIONS_DIR = "outputs/fused_detections"
OUTPUT_DIR = "outputs/lidar_object_points"

LIDAR_FILE = f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"

INTRINSICS_FILE = "data_source/calibration/camera_intrinsics.chunk_0000.parquet"
EXTRINSICS_FILE = "data_source/calibration/sensor_extrinsics.chunk_0000.parquet"

FRAME_COUNT = 50
BBOX_MARGIN = 20
MIN_LIDAR_POINTS = 3


# -------------------------
# Camera intrinsics
# -------------------------

def load_intrinsics():

    table = pq.read_table(INTRINSICS_FILE)
    df = table.to_pandas().reset_index()

    row = df[df["camera_name"] == "camera_front_wide_120fov"].iloc[0]

    fx = row["fw_poly_1"]
    fy = row["fw_poly_1"]
    cx = row["cx"]
    cy = row["cy"]

    return fx, fy, cx, cy


# -------------------------
# Sensor extrinsics
# -------------------------

def load_extrinsics():

    table = pq.read_table(EXTRINSICS_FILE)
    df = table.to_pandas().reset_index()

    row = df[df["sensor_name"] == "camera_front_wide_120fov"].iloc[0]

    translation = np.array([row["x"], row["y"], row["z"]])

    rotation = R.from_quat([
        row["qx"],
        row["qy"],
        row["qz"],
        row["qw"]
    ])

    return translation, rotation


# -------------------------
# Transform LiDAR → Camera
# -------------------------

def transform_lidar(points, translation, rotation):

    rotated = rotation.apply(points)
    transformed = rotated + translation

    return transformed


# -------------------------
# Projection
# -------------------------

def project(points, fx, fy, cx, cy):

    x = points[:,0]
    y = points[:,1]
    z = points[:,2]

    z[z == 0] = 1e-6

    u = fx * (x/z) + cx
    v = fy * (y/z) + cy

    return np.stack((u,v), axis=1)


# -------------------------
# Load LiDAR
# -------------------------

def load_lidar():

    print("Loading LiDAR scan...")

    table = pq.read_table(LIDAR_FILE)
    df = table.to_pandas()

    decoded = DracoPy.decode(df.iloc[0]["draco_encoded_pointcloud"])
    lidar_points = np.array(decoded.points)

    print("Total LiDAR points:", lidar_points.shape)

    return lidar_points


# -------------------------
# Process single frame
# -------------------------

def process_frame(frame_index, pixels, camera_points):

    detection_file = f"{FUSED_DETECTIONS_DIR}/frame_{frame_index:03d}.json"

    if not os.path.exists(detection_file):
        print(f"Frame {frame_index:03d} detection file missing")
        return

    with open(detection_file) as f:
        data = json.load(f)

    objects = data.get("objects", [])

    frame_output = []

    for obj in objects:

        x1, y1, x2, y2 = obj["bbox_2d"]

        mask = (
            (pixels[:,0] >= x1 - BBOX_MARGIN) &
            (pixels[:,0] <= x2 + BBOX_MARGIN) &
            (pixels[:,1] >= y1 - BBOX_MARGIN) &
            (pixels[:,1] <= y2 + BBOX_MARGIN)
        )

        lidar_pts = camera_points[mask]

        print(
            f"Frame {frame_index:03d} | Object {obj['class']} | LiDAR points:",
            lidar_pts.shape[0]
        )

        if lidar_pts.shape[0] < MIN_LIDAR_POINTS:
            continue

        frame_output.append({

            "object_id": obj["object_id"],
            "class": obj["class"],
            "confidence": obj["confidence"],

            "bbox_2d": obj["bbox_2d"],
            "bbox_center": obj["bbox_center"],

            "camera_votes": obj["camera_votes"],
            "source_cameras": obj["source_cameras"],

            "lidar_point_count": int(lidar_pts.shape[0]),

            "points_3d": lidar_pts.tolist()

        })

    output_file = f"{OUTPUT_DIR}/frame_{frame_index:03d}.json"

    with open(output_file, "w") as f:

        json.dump({
            "frame_index": frame_index,
            "objects": frame_output
        }, f, indent=4)

    print(f"Frame {frame_index:03d} → {len(frame_output)} lidar objects")


# -------------------------
# Main pipeline
# -------------------------

def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lidar_points = load_lidar()

    fx, fy, cx, cy = load_intrinsics()
    translation, rotation = load_extrinsics()

    camera_points = transform_lidar(lidar_points, translation, rotation)

    camera_points = camera_points[camera_points[:,2] > 0]

    pixels = project(camera_points, fx, fy, cx, cy)

    print("Projected points:", pixels.shape)

    for frame in range(FRAME_COUNT):

        process_frame(frame, pixels, camera_points)

    print("\nLiDAR object extraction completed")


if __name__ == "__main__":
    main()