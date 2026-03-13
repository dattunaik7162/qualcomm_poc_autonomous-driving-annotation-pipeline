import json
import numpy as np
from sklearn.cluster import DBSCAN
import os
import plotly.graph_objects as go

FRAME_COUNT = 50

LIDAR_POINTS_DIR = "outputs/lidar_object_points"
OUTPUT_DIR = "outputs/lidar_annotations"

VISUALIZE = False


# ------------------------------------------------
# Clean and validate LiDAR points
# ------------------------------------------------
def clean_points(points):

    if len(points) == 0:
        return np.empty((0,3))

    pts = np.array(points)

    if pts.ndim != 2 or pts.shape[1] != 3:
        return np.empty((0,3))

    pts = pts[np.isfinite(pts).all(axis=1)]

    return pts


# ------------------------------------------------
# Cluster LiDAR points
# ------------------------------------------------
def cluster_points(points):

    if len(points) < 10:
        return []

    try:
        clustering = DBSCAN(eps=1.2, min_samples=8).fit(points)
    except:
        return []

    labels = clustering.labels_

    clusters = []

    for cid in set(labels):

        if cid == -1:
            continue

        cluster = points[labels == cid]

        if len(cluster) < 10:
            continue

        clusters.append(cluster)

    return clusters


# ------------------------------------------------
# Compute 3D bounding box
# ------------------------------------------------
def compute_bbox(cluster):

    xmin, ymin, zmin = cluster.min(axis=0)
    xmax, ymax, zmax = cluster.max(axis=0)

    center = [
        float((xmin + xmax) / 2),
        float((ymin + ymax) / 2),
        float((zmin + zmax) / 2)
    ]

    dimensions = [
        float(xmax - xmin),
        float(ymax - ymin),
        float(zmax - zmin)
    ]

    return center, dimensions


# ------------------------------------------------
# Plotly visualization (optional)
# ------------------------------------------------
def visualize(points, annotations):

    fig = go.Figure()

    pts = points[::30]

    fig.add_trace(go.Scatter3d(
        x=pts[:,0],
        y=pts[:,1],
        z=pts[:,2],
        mode='markers',
        marker=dict(size=2,color='gray'),
        name="LiDAR"
    ))

    for obj in annotations:

        c = obj["bbox_3d"]["center"]

        label = f'{obj["class"]} ({obj["confidence"]:.2f}) {obj["distance_meters"]}m'

        fig.add_trace(go.Scatter3d(
            x=[c[0]],
            y=[c[1]],
            z=[c[2]],
            mode='markers+text',
            marker=dict(size=8,color='red'),
            text=[label],
            name=obj["class"]
        ))

    fig.update_layout(
        title="3D LiDAR Detection",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )

    fig.show()


# ------------------------------------------------
# Process each frame
# ------------------------------------------------
def process_frame(frame_index):

    file = f"{LIDAR_POINTS_DIR}/frame_{frame_index:03d}.json"

    if not os.path.exists(file):
        print(f"Frame {frame_index:03d} skipped (no lidar file)")
        return

    try:
        with open(file) as f:
            data = json.load(f)
    except:
        print(f"Frame {frame_index:03d} invalid JSON")
        return

    objects = data.get("objects", [])

    if len(objects) == 0:
        print(f"Frame {frame_index:03d} no objects")
        return

    annotations = []

    for obj in objects:

        points = clean_points(obj.get("points_3d", []))

        if len(points) < 10:
            continue

        clusters = cluster_points(points)

        if len(clusters) == 0:
            continue

        # choose largest cluster
        largest_cluster = max(clusters, key=len)

        center, dims = compute_bbox(largest_cluster)

        # distance from ego vehicle
        distance = float(np.linalg.norm(center))

        annotation = {

            "object_id": obj.get("object_id","unknown"),

            "class": obj.get("class","object"),

            "confidence": float(obj.get("confidence",0.0)),

            "bbox_2d": obj.get("bbox_2d",[]),

            "camera_votes": len(obj.get("source_cameras",[])),

            "source_cameras": obj.get("source_cameras",[]),

            "distance_meters": round(distance,2),

            "bbox_3d": {

                "center": center,
                "dimensions": dims

            },

            "num_lidar_points": int(len(largest_cluster))

        }

        annotations.append(annotation)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    out_file = f"{OUTPUT_DIR}/frame_{frame_index:03d}.json"

    with open(out_file,"w") as f:

        json.dump({

            "frame_index": frame_index,
            "objects": annotations

        },f,indent=4)

    print(f"Frame {frame_index:03d} → {len(annotations)} 3D objects")

    if VISUALIZE and len(annotations)>0:

        all_pts = np.vstack([
            clean_points(o["points_3d"])
            for o in objects
            if len(o.get("points_3d",[]))>0
        ])

        visualize(all_pts, annotations)


# ------------------------------------------------
# Main
# ------------------------------------------------
def main():

    print("Starting 3D bounding box generation")

    for frame in range(FRAME_COUNT):

        process_frame(frame)

    print("\n3D Bounding box generation completed")


if __name__ == "__main__":
    main()