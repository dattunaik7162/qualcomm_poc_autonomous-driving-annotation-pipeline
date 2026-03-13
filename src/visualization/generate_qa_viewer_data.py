import os
import shutil

FRAME_SOURCE = "outputs/frames/front_wide"
ANNOT_SOURCE = "outputs/lidar_annotations"
LIDAR_SOURCE = "outputs/lidar_object_points"

VIEWER_ROOT = "qa_viewer"

FRAME_TARGET = f"{VIEWER_ROOT}/data/frames"
ANNOT_TARGET = f"{VIEWER_ROOT}/data/annotations"
LIDAR_TARGET = f"{VIEWER_ROOT}/data/lidar_points"

FRAME_COUNT = 50


def create_dirs():
    os.makedirs(FRAME_TARGET, exist_ok=True)
    os.makedirs(ANNOT_TARGET, exist_ok=True)
    os.makedirs(LIDAR_TARGET, exist_ok=True)


def copy_files(source, target, ext):

    copied = 0

    for i in range(FRAME_COUNT):

        name = f"frame_{i:03d}.{ext}"

        src = os.path.join(source, name)
        dst = os.path.join(target, name)

        if os.path.exists(src):
            shutil.copy(src, dst)
            copied += 1

    return copied


def main():

    print("Preparing QA viewer data")

    create_dirs()

    f = copy_files(FRAME_SOURCE, FRAME_TARGET, "jpg")
    a = copy_files(ANNOT_SOURCE, ANNOT_TARGET, "json")
    l = copy_files(LIDAR_SOURCE, LIDAR_TARGET, "json")

    print("Frames copied:", f)
    print("Annotations copied:", a)
    print("LiDAR points copied:", l)


if __name__ == "__main__":
    main()