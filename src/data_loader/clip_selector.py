import os

CAMERA_FRONT = "data_source/camera/camera_front_wide_120fov.chunk_0000"
CAMERA_LEFT = "data_source/camera/camera_cross_left_120fov.chunk_0000"
CAMERA_RIGHT = "data_source/camera/camera_cross_right_120fov.chunk_0000"

LIDAR_PATH = "data_source/lidar/lidar_top_360fov.chunk_0000"


def extract_clip_ids(folder, suffix):
    
    clip_ids = set()

    for file in os.listdir(folder):

        if file.endswith(suffix):
            clip_id = file.split(".")[0]
            clip_ids.add(clip_id)

    return clip_ids


def main():

    front_ids = extract_clip_ids(CAMERA_FRONT, ".camera_front_wide_120fov.mp4")
    left_ids = extract_clip_ids(CAMERA_LEFT, ".camera_cross_left_120fov.mp4")
    right_ids = extract_clip_ids(CAMERA_RIGHT, ".camera_cross_right_120fov.mp4")
    lidar_ids = extract_clip_ids(LIDAR_PATH, ".lidar_top_360fov.parquet")

    valid_clips = front_ids & left_ids & right_ids & lidar_ids

    print("\nValid synchronized clips:", len(valid_clips))
    print("--------------------------------")

    for clip in list(valid_clips)[:10]:
        print(clip)


if __name__ == "__main__":
    main()