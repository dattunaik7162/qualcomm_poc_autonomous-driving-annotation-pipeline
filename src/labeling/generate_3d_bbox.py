import json
import numpy as np
import cv2
import pyarrow.parquet as pq
import DracoPy
from scipy.spatial.transform import Rotation as R
from sklearn.cluster import DBSCAN
import os

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

IMAGE_PATH = "outputs/frames/front_wide/frame_000.jpg"
DETECTION_FILE = "outputs/detection_json/front_wide/frame_000.json"

LIDAR_FILE = f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"

INTRINSICS_FILE = "data_source/calibration/camera_intrinsics.chunk_0000.parquet"
EXTRINSICS_FILE = "data_source/calibration/sensor_extrinsics.chunk_0000.parquet"


# ------------------------------------------------
# Load Camera Intrinsics
# ------------------------------------------------
def load_intrinsics():

    table = pq.read_table(INTRINSICS_FILE)
    df = table.to_pandas().reset_index()

    row = df[df["camera_name"] == "camera_front_wide_120fov"].iloc[0]

    fx = row["fw_poly_1"]
    fy = row["fw_poly_1"]
    cx = row["cx"]
    cy = row["cy"]

    return fx, fy, cx, cy


# ------------------------------------------------
# Load Sensor Extrinsics
# ------------------------------------------------
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


# ------------------------------------------------
# Transform LiDAR → Camera frame
# ------------------------------------------------
def transform(points, translation, rotation):

    rotated = rotation.apply(points)

    return rotated + translation


# ------------------------------------------------
# Project 3D → 2D
# ------------------------------------------------
def project(points, fx, fy, cx, cy):

    x = points[:,0]
    y = points[:,1]
    z = points[:,2]

    z[z == 0] = 1e-6

    u = fx * (x/z) + cx
    v = fy * (y/z) + cy

    return np.stack((u,v), axis=1)


# ------------------------------------------------
# Parse bbox safely
# ------------------------------------------------
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
        x1,y1,x2,y2 = map(int,bbox)
        return x1,y1,x2,y2
    except:
        return None


# ------------------------------------------------
# Main Pipeline
# ------------------------------------------------
def main():

    if not os.path.exists(IMAGE_PATH):
        print("Image missing")
        return

    img = cv2.imread(IMAGE_PATH)

    if img is None:
        print("Failed to load image")
        return


    if not os.path.exists(DETECTION_FILE):
        print("Detection JSON missing")
        return

    with open(DETECTION_FILE) as f:
        detections = json.load(f)

    if len(detections) == 0:
        print("No detections")
        return


    # ----------------------------
    # Load LiDAR
    # ----------------------------

    table = pq.read_table(LIDAR_FILE)
    df = table.to_pandas()

    decoded = DracoPy.decode(df.iloc[0]["draco_encoded_pointcloud"])

    lidar_points = np.array(decoded.points)

    print("Total LiDAR points:", lidar_points.shape)


    # ----------------------------
    # Calibration
    # ----------------------------

    fx, fy, cx, cy = load_intrinsics()
    translation, rotation = load_extrinsics()


    # ----------------------------
    # Transform + Project
    # ----------------------------

    camera_points = transform(lidar_points, translation, rotation)

    camera_points = camera_points[camera_points[:,2] > 0]

    pixels = project(camera_points, fx, fy, cx, cy)

    pixels_int = pixels.astype(int)

    print("Projected points:", pixels.shape)


    annotations = []


    # ----------------------------
    # Process detections
    # ----------------------------

    for det in detections:

        bbox = parse_bbox(det)

        if bbox is None:
            continue

        x1,y1,x2,y2 = bbox

        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)


        # filter lidar points inside bbox
        mask = (
            (pixels_int[:,0] >= x1) &
            (pixels_int[:,0] <= x2) &
            (pixels_int[:,1] >= y1) &
            (pixels_int[:,1] <= y2)
        )

        object_points = camera_points[mask]

        print("Points inside bbox:",len(object_points))

        if len(object_points) < 10:
            continue


        # ----------------------------
        # Cluster LiDAR points
        # ----------------------------

        clustering = DBSCAN(eps=1.5, min_samples=8).fit(object_points)

        labels = clustering.labels_

        clusters = set(labels)


        for cluster_id in clusters:

            if cluster_id == -1:
                continue

            cluster_points = object_points[labels == cluster_id]


            xmin,ymin,zmin = cluster_points.min(axis=0)
            xmax,ymax,zmax = cluster_points.max(axis=0)


            center = [
                float((xmin+xmax)/2),
                float((ymin+ymax)/2),
                float((zmin+zmax)/2)
            ]

            dimensions = [
                float(xmax-xmin),
                float(ymax-ymin),
                float(zmax-zmin)
            ]


            annotation = {

                "class": det.get("class","object"),

                "confidence": float(det.get("confidence",1.0)),

                "bbox_2d": [x1,y1,x2,y2],

                "bbox_3d": {

                    "center": center,

                    "dimensions": dimensions
                },

                "num_lidar_points": int(len(cluster_points))
            }

            annotations.append(annotation)


            # visualize center
            pixel = project(np.array([center]),fx,fy,cx,cy)[0]

            cx2,cy2 = int(pixel[0]),int(pixel[1])

            if 0 <= cx2 < img.shape[1] and 0 <= cy2 < img.shape[0]:
                cv2.circle(img,(cx2,cy2),8,(255,0,0),-1)


    # ----------------------------
    # Save annotations
    # ----------------------------

    os.makedirs("outputs/lidar_annotations", exist_ok=True)

    label_file = "outputs/lidar_annotations/frame_000.json"

    with open(label_file,"w") as f:

        json.dump({

            "frame_id":"frame_000",

            "objects":annotations

        },f,indent=2)

    print("Annotation file saved:",label_file)


    cv2.imshow("3D Bounding Box Detection",img)

    cv2.waitKey(0)

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()