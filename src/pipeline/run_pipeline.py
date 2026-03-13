import subprocess
import argparse
import os

def run_step(name, command):

    print("\n===================================")
    print(f"Running step: {name}")
    print("===================================\n")

    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print(f"Step failed: {name}")
        exit(1)

    print(f"Completed: {name}")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--clip_id",
        required=True,
        help="Dataset clip id"
    )

    args = parser.parse_args()

    clip_id = args.clip_id


    os.environ["CLIP_ID"] = clip_id


    # Step 1
    run_step(
        "1. Frame Extraction",
        "python src/preprocessing/frame_extraction.py"
    )

    # Step 2
    run_step(
        "2. Object Detection",
        "python src/detection/camera_object_detection.py"
    )

    # Step 3
    run_step(
        "3. Timestamp Alignment",
        "python src/preprocessing/timestamp_alignment.py"
    )

    # Step 4
    run_step(
        "4. LiDAR Decoding",
        "python src/preprocessing/lidar_decoding.py"
    )

    # Step 5
    run_step(
        "5. LiDAR Projection",
        "python src/projection/lidar_to_camera_projection.py"
    )

    # Step 6
    run_step(
        "6. LiDAR Object Extraction",
        "python src/labeling/extract_lidar_points_from_bbox.py"
    )

    # Step 7
    run_step(
        "7. 3D Bounding Box Generation",
        "python src/labeling/generate_3d_bbox.py"
    )

    print("\n===================================")
    print("Pipeline Completed Successfully")
    print("===================================")


if __name__ == "__main__":
    main()