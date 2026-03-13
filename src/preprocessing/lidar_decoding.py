import pyarrow.parquet as pq
import numpy as np
import DracoPy
import open3d as o3d

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

LIDAR_FILE = f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"


def load_lidar_scan(spin_index=0):

    table = pq.read_table(LIDAR_FILE)
    df = table.to_pandas()

    compressed_pc = df.iloc[spin_index]["draco_encoded_pointcloud"]

    decoded = DracoPy.decode(compressed_pc)

    points = np.array(decoded.points)

    return points


def visualize_pointcloud(points):

    pcd = o3d.geometry.PointCloud()

    pcd.points = o3d.utility.Vector3dVector(points)

    o3d.visualization.draw_geometries([pcd])


def main():

    print("Loading LiDAR scan...")

    points = load_lidar_scan(spin_index=0)

    print("Total points:", points.shape)

    visualize_pointcloud(points)


if __name__ == "__main__":
    main()