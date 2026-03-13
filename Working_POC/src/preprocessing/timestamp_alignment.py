import os
import pandas as pd
import pyarrow.parquet as pq

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

CAMERA_TIMESTAMP_FILE = f"data_source/camera/camera_front_wide_120fov.chunk_0000/{CLIP_ID}.camera_front_wide_120fov.timestamps.parquet"

LIDAR_FILE = f"data_source/lidar/lidar_top_360fov.chunk_0000/{CLIP_ID}.lidar_top_360fov.parquet"

OUTPUT_FOLDER = "outputs/sensor_alignment"
OUTPUT_FILE = f"{OUTPUT_FOLDER}/alignment_table.csv"

MAX_FRAMES = 50


def load_camera_timestamps():

    table = pq.read_table(CAMERA_TIMESTAMP_FILE)
    df = table.to_pandas()

    df = df.head(MAX_FRAMES)

    return df


def load_lidar_timestamps():

    table = pq.read_table(LIDAR_FILE)
    df = table.to_pandas()

    # create spin index manually
    df["spin_index"] = df.index

    return df[["spin_index", "reference_timestamp"]]


def align_timestamps(camera_df, lidar_df):

    alignment = []

    for i, cam_row in camera_df.iterrows():

        cam_ts = cam_row["timestamp"]

        lidar_df["time_diff"] = abs(lidar_df["reference_timestamp"] - cam_ts)

        closest = lidar_df.loc[lidar_df["time_diff"].idxmin()]

        alignment.append({
            "camera_frame_index": i,
            "camera_timestamp": cam_ts,
            "lidar_spin_index": int(closest["spin_index"]),
            "lidar_timestamp": int(closest["reference_timestamp"]),
            "time_difference": int(closest["time_diff"])
        })

    return pd.DataFrame(alignment)


def main():

    print("Loading camera timestamps...")
    camera_df = load_camera_timestamps()

    print("Loading lidar timestamps...")
    lidar_df = load_lidar_timestamps()

    print("Aligning timestamps...")
    aligned_df = align_timestamps(camera_df, lidar_df)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    aligned_df.to_csv(OUTPUT_FILE, index=False)

    print("Alignment saved:", OUTPUT_FILE)
    print(aligned_df.head())


if __name__ == "__main__":
    main()