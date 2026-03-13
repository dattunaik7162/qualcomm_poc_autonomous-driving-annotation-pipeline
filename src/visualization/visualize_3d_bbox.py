import json
import numpy as np
import pyarrow.parquet as pq
import DracoPy
import plotly.graph_objects as go
from pathlib import Path


# -----------------------------
# CONFIGURATION
# -----------------------------

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

LIDAR_FILE = Path(
    f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"
)

ANNOTATION_FILE = Path("outputs/lidar_annotations/frame_000.json")

POINT_SUBSAMPLE = 50


# Color map for object classes
CLASS_COLORS = {
    "car": "red",
    "truck": "blue",
    "person": "green",
    "traffic_light": "yellow",
    "bicycle": "cyan",
    "object": "orange"
}


# -----------------------------
# LOAD LIDAR
# -----------------------------

def load_lidar(lidar_file: Path):

    if not lidar_file.exists():
        raise FileNotFoundError(f"LiDAR file not found: {lidar_file}")

    print(f"Reading LiDAR parquet: {lidar_file}")

    table = pq.read_table(lidar_file)
    df = table.to_pandas()

    if len(df) == 0:
        raise ValueError("Empty LiDAR parquet file")

    print("Decoding Draco compressed point cloud...")

    decoded = DracoPy.decode(df.iloc[0]["draco_encoded_pointcloud"])

    points = np.array(decoded.points)

    print(f"Loaded {points.shape[0]} LiDAR points")

    return points


# -----------------------------
# LOAD ANNOTATIONS
# -----------------------------

def load_annotations(annotation_file: Path):

    if not annotation_file.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotation_file}")

    with open(annotation_file) as f:
        data = json.load(f)

    return data.get("objects", [])


# -----------------------------
# CREATE 3D BOUNDING BOX
# -----------------------------

def create_bbox(center, dims):

    cx, cy, cz = center
    dx, dy, dz = dims

    x = dx / 2
    y = dy / 2
    z = dz / 2

    corners = np.array([
        [cx-x, cy-y, cz-z],
        [cx+x, cy-y, cz-z],
        [cx+x, cy+y, cz-z],
        [cx-x, cy+y, cz-z],
        [cx-x, cy-y, cz+z],
        [cx+x, cy-y, cz+z],
        [cx+x, cy+y, cz+z],
        [cx-x, cy+y, cz+z]
    ])

    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]

    return corners, edges


# -----------------------------
# VISUALIZATION
# -----------------------------

def visualize(lidar_points, annotations):

    fig = go.Figure()

    # LiDAR cloud
    fig.add_trace(go.Scatter3d(
        x=lidar_points[:,0],
        y=lidar_points[:,1],
        z=lidar_points[:,2],
        mode='markers',
        marker=dict(size=2, color='gray', opacity=0.4),
        name="LiDAR Point Cloud"
    ))

    legend_added = set()

    for obj in annotations:

        center = obj["bbox_3d"]["center"]
        dims = obj["bbox_3d"]["dimensions"]
        label = obj.get("class", "object")
        conf = obj.get("confidence",1.0)

        text = f"{label} ({conf:.2f})"

        color = CLASS_COLORS.get(label, "orange")

        corners, edges = create_bbox(center, dims)

        # draw box edges
        for e in edges:

            fig.add_trace(go.Scatter3d(
                x=[corners[e[0]][0], corners[e[1]][0]],
                y=[corners[e[0]][1], corners[e[1]][1]],
                z=[corners[e[0]][2], corners[e[1]][2]],
                mode='lines',
                line=dict(color=color, width=2),
                name=label if label not in legend_added else None,
                showlegend=label not in legend_added
            ))

        legend_added.add(label)

        # box corners
        fig.add_trace(go.Scatter3d(
            x=corners[:,0],
            y=corners[:,1],
            z=corners[:,2],
            mode='markers',
            marker=dict(size=4, color=color),
            showlegend=False
        ))

        # label text
        fig.add_trace(go.Scatter3d(
            x=[center[0]],
            y=[center[1]],
            z=[center[2]],
            mode="text",
            text=[text],
            textposition="top center",
            showlegend=False
        ))

    fig.update_layout(
        title="3D LiDAR Object Detection Visualization",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        ),
        legend=dict(
            title="Object Classes"
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    fig.show()


# -----------------------------
# MAIN
# -----------------------------

def main():

    print("Starting LiDAR visualization pipeline")

    lidar = load_lidar(LIDAR_FILE)

    # reduce point cloud
    lidar = lidar[::POINT_SUBSAMPLE]

    annotations = load_annotations(ANNOTATION_FILE)

    print(f"Loaded {len(annotations)} objects")

    visualize(lidar, annotations)


if __name__ == "__main__":
    main()