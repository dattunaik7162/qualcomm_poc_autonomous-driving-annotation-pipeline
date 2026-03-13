from ultralytics import YOLO
import os
import cv2
import json

MODEL = YOLO("yolov8n.pt")

FRAME_ROOT = "outputs/frames"
IMAGE_OUTPUT_ROOT = "outputs/camera_detections"
JSON_OUTPUT_ROOT = "outputs/detection_json"

CAMERAS = ["front_wide", "cross_left", "cross_right"]


def run_detection():

    for camera in CAMERAS:

        input_folder = os.path.join(FRAME_ROOT, camera)

        image_output_folder = os.path.join(IMAGE_OUTPUT_ROOT, camera)
        json_output_folder = os.path.join(JSON_OUTPUT_ROOT, camera)

        os.makedirs(image_output_folder, exist_ok=True)
        os.makedirs(json_output_folder, exist_ok=True)

        frames = sorted(os.listdir(input_folder))

        for frame_name in frames:

            frame_path = os.path.join(input_folder, frame_name)

            img = cv2.imread(frame_path)

            results = MODEL(img)

            annotated = results[0].plot()

            image_save_path = os.path.join(image_output_folder, frame_name)

            cv2.imwrite(image_save_path, annotated)

            detections = []

            for box in results[0].boxes:

                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({
                    "class_id": cls_id,
                    "class_name": MODEL.names[cls_id],
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

            json_path = os.path.join(
                json_output_folder,
                frame_name.replace(".jpg", ".json")
            )

            with open(json_path, "w") as f:
                json.dump(detections, f, indent=4)

        print(f"Detection completed for {camera}")


if __name__ == "__main__":
    run_detection()