import json
import numpy as np
import cv2
import pyarrow.parquet as pq
import DracoPy
from scipy.spatial.transform import Rotation as R
import os

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

IMAGE_PATH = "outputs/frames/front_wide/frame_000.jpg"
DETECTION_FILE = "outputs/detection_json/front_wide/frame_000.json"

LIDAR_FILE = f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"

INTRINSICS_FILE = "data_source/calibration/camera_intrinsics.chunk_0000.parquet"
EXTRINSICS_FILE = "data_source/calibration/sensor_extrinsics.chunk_0000.parquet"


# -------------------------
# Load intrinsics
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
# Load extrinsics
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
    return rotated + translation


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
# Parse bbox safely
# -------------------------
def parse_bbox(det):

    if "bbox" in det:
        bbox = det["bbox"]

    elif "box" in det:
        bbox = det["box"]

    elif "xyxy" in det:
        bbox = det["xyxy"]

    else:
        return None

    if len(bbox) != 4:
        return None

    try:
        x1, y1, x2, y2 = map(int, bbox)
        return x1, y1, x2, y2
    except:
        return None


# -------------------------
# Main
# -------------------------
def main():

    if not os.path.exists(IMAGE_PATH):
        print("Image not found")
        return

    img = cv2.imread(IMAGE_PATH)

    if img is None:
        print("Failed to load image")
        return


    # ---------------------
    # Load detections
    # ---------------------

    if not os.path.exists(DETECTION_FILE):
        print("Detection file not found")
        return

    with open(DETECTION_FILE) as f:
        detections = json.load(f)

    if len(detections) == 0:
        print("No detections found")
        return


    # ---------------------
    # Load LiDAR
    # ---------------------

    table = pq.read_table(LIDAR_FILE)
    df = table.to_pandas()

    decoded = DracoPy.decode(df.iloc[0]["draco_encoded_pointcloud"])
    lidar_points = np.array(decoded.points)

    print("Total LiDAR points:", lidar_points.shape)


    # ---------------------
    # Calibration
    # ---------------------

    fx, fy, cx, cy = load_intrinsics()
    translation, rotation = load_extrinsics()


    # ---------------------
    # Transform + project
    # ---------------------

    camera_points = transform_lidar(lidar_points, translation, rotation)

    camera_points = camera_points[camera_points[:,2] > 0]

    pixels = project(camera_points, fx, fy, cx, cy)

    pixels_int = pixels.astype(int)

    print("Projected points:", pixels.shape)


    # ---------------------
    # Process detections
    # ---------------------

    for det in detections:

        bbox = parse_bbox(det)

        if bbox is None:
            continue

        x1, y1, x2, y2 = bbox

        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)


        # Vectorized filtering
        mask = (
            (pixels_int[:,0] >= x1) &
            (pixels_int[:,0] <= x2) &
            (pixels_int[:,1] >= y1) &
            (pixels_int[:,1] <= y2)
        )

        object_points = pixels_int[mask]

        print("Points inside bbox:", len(object_points))


        # Draw lidar points
        for p in object_points:

            x, y = p

            if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:
                cv2.circle(img,(x,y),4,(0,0,255),-1)


    cv2.imshow("LiDAR Points in Object",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()