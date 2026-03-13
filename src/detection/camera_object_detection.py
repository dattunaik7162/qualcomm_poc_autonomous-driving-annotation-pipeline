from ultralytics import YOLO
import os
import cv2
import json

# -----------------------------
# CONFIGURATION
# -----------------------------

MODEL_PATH = "yolov8n.pt"

FRAME_ROOT = "outputs/frames"
IMAGE_OUTPUT_ROOT = "outputs/camera_detections"
JSON_OUTPUT_ROOT = "outputs/detection_json"

CAMERAS = ["front_wide", "cross_left", "cross_right"]

CONF_THRESHOLD = 0.25


# -----------------------------
# LOAD MODEL
# -----------------------------

print("Loading YOLO model...")
MODEL = YOLO(MODEL_PATH)

print("Model classes:", MODEL.names)


# -----------------------------
# DETECTION FUNCTION
# -----------------------------

def run_detection():

    for camera in CAMERAS:

        print("\n--------------------------------")
        print(f"Processing camera: {camera}")
        print("--------------------------------")

        input_folder = os.path.join(FRAME_ROOT, camera)

        image_output_folder = os.path.join(IMAGE_OUTPUT_ROOT, camera)
        json_output_folder = os.path.join(JSON_OUTPUT_ROOT, camera)

        os.makedirs(image_output_folder, exist_ok=True)
        os.makedirs(json_output_folder, exist_ok=True)

        frames = sorted(os.listdir(input_folder))

        for frame_name in frames:

            frame_path = os.path.join(input_folder, frame_name)

            img = cv2.imread(frame_path)

            if img is None:
                print("Skipping corrupted frame:", frame_path)
                continue

            frame_index = int(frame_name.split("_")[1].split(".")[0])

            results = MODEL(img)

            annotated = results[0].plot()

            image_save_path = os.path.join(image_output_folder, frame_name)

            cv2.imwrite(image_save_path, annotated)

            detections = []

            if results[0].boxes is not None:

                for box in results[0].boxes:

                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    if confidence < CONF_THRESHOLD:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    detections.append({

                        "frame_index": frame_index,

                        "camera": camera,

                        "class_id": cls_id,

                        "class_name": MODEL.names[cls_id],

                        "confidence": round(confidence, 3),

                        "bbox": [
                            int(x1),
                            int(y1),
                            int(x2),
                            int(y2)
                        ]
                    })

            json_path = os.path.join(
                json_output_folder,
                frame_name.replace(".jpg", ".json")
            )

            with open(json_path, "w") as f:
                json.dump({
                    "camera": camera,
                    "frame_index": frame_index,
                    "detections": detections
                }, f, indent=4)

        print(f"Detection completed for {camera}")


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    run_detection()

    print("\nCamera detection pipeline completed")