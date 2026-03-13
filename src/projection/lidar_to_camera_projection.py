import pyarrow.parquet as pq
import numpy as np
from scipy.spatial.transform import Rotation as R
import cv2
import DracoPy

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

LIDAR_FILE = f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"
INTRINSICS_FILE = "data_source/calibration/camera_intrinsics.chunk_0000.parquet"
EXTRINSICS_FILE = "data_source/calibration/sensor_extrinsics.chunk_0000.parquet"

IMAGE_PATH = "outputs/frames/front_wide/frame_000.jpg"


# -------------------------
# Camera Intrinsics
# -------------------------
def load_intrinsics():

    table = pq.read_table(INTRINSICS_FILE)
    df = table.to_pandas().reset_index()

    print("Intrinsics columns:", df.columns)

    row = df[df["camera_name"] == "camera_front_wide_120fov"].iloc[0]

    fx = row["fw_poly_1"]
    fy = row["fw_poly_1"]
    cx = row["cx"]
    cy = row["cy"]

    return fx, fy, cx, cy


# -------------------------
# Sensor Extrinsics
# -------------------------
def load_extrinsics():

    table = pq.read_table(EXTRINSICS_FILE)
    df = table.to_pandas().reset_index()

    print("Extrinsics columns:", df.columns)

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
def transform_lidar_to_camera(points, translation, rotation):

    rotated = rotation.apply(points)
    transformed = rotated + translation

    return transformed


# -------------------------
# Projection Function
# -------------------------
def project_points(points, fx, fy, cx, cy):

    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]

    z[z == 0] = 0.0001

    u = fx * (x / z) + cx
    v = fy * (y / z) + cy

    return np.stack((u, v), axis=1)


# -------------------------
# Main Pipeline
# -------------------------
def main():

    print("Loading camera image...")
    img = cv2.imread(IMAGE_PATH)

    print("Loading LiDAR scan...")
    table = pq.read_table(LIDAR_FILE)
    df = table.to_pandas()

    decoded = DracoPy.decode(df.iloc[0]["draco_encoded_pointcloud"])
    lidar_points = np.array(decoded.points)

    print("Total LiDAR points:", lidar_points.shape)

    fx, fy, cx, cy = load_intrinsics()
    translation, rotation = load_extrinsics()

    # Transform points to camera frame
    camera_points = transform_lidar_to_camera(lidar_points, translation, rotation)

    # Keep points in front of camera
    camera_points = camera_points[camera_points[:, 2] > 0]

    pixels = project_points(camera_points, fx, fy, cx, cy)

    print("Projected points:", pixels.shape)

    z = camera_points[:, 2]

    # Draw many points for demo clarity
    for i in range(0, len(pixels), 20):

        x = int(pixels[i][0])
        y = int(pixels[i][1])

        depth = z[i]

        # Depth-based color
        r = int(max(0, 255 - depth * 5))
        g = int(min(255, depth * 5))
        b = 50

        if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:
            cv2.circle(img, (x, y), 4, (b, g, r), -1)

    # Title overlay for demo
    cv2.putText(
        img,
        "Camera + LiDAR Sensor Fusion",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    cv2.imshow("LiDAR Projection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()