import cv2
import os

CLIP_ID = "0a948f59-0a06-41a2-8e20-ac3a39ff4d61"

CAMERA_PATHS = {
    "front_wide": f"data_source/camera/camera_front_wide_120fov.chunk_0000/{CLIP_ID}.camera_front_wide_120fov.mp4",
    "cross_left": f"data_source/camera/camera_cross_left_120fov.chunk_0000/{CLIP_ID}.camera_cross_left_120fov.mp4",
    "cross_right": f"data_source/camera/camera_cross_right_120fov.chunk_0000/{CLIP_ID}.camera_cross_right_120fov.mp4",
}

OUTPUT_ROOT = "outputs/frames"

MAX_FRAMES = 50


def extract_frames(video_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    frame_id = 0

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret or frame_id >= MAX_FRAMES:
            break

        frame_path = os.path.join(output_folder, f"frame_{frame_id:03d}.jpg")

        cv2.imwrite(frame_path, frame)

        frame_id += 1

    cap.release()

    print(f"{frame_id} frames saved to {output_folder}")


def main():

    for camera_name, video_path in CAMERA_PATHS.items():

        output_folder = os.path.join(OUTPUT_ROOT, camera_name)

        print(f"\nProcessing {camera_name}")

        extract_frames(video_path, output_folder)


if __name__ == "__main__":
    main()