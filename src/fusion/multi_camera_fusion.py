import json
import os
import uuid
import math

INPUT_DIR = "outputs/detection_json"
OUTPUT_DIR = "outputs/fused_detections"

CAMERAS = ["front_wide", "cross_left", "cross_right"]

FRAME_COUNT = 50

CONF_THRESHOLD = 0.4
IOU_THRESHOLD = 0.25
CENTER_DIST_THRESHOLD = 250
DUPLICATE_IOU = 0.5

MAX_BBOX_AREA = 600000

previous_tracks = []


# -----------------------------
# Class normalization
# -----------------------------

CLASS_MAP = {
    "motorcycle": "bike",
    "bicycle": "bike",
    "bus": "vehicle",
    "truck": "vehicle",
    "car": "car",
    "person": "pedestrian"
}


def normalize_class(cls):
    return CLASS_MAP.get(cls, cls)


# -----------------------------
# Geometry
# -----------------------------

def bbox_center(b):
    x1,y1,x2,y2=b
    return ((x1+x2)/2,(y1+y2)/2)


def bbox_iou(b1,b2):

    x1=max(b1[0],b2[0])
    y1=max(b1[1],b2[1])
    x2=min(b1[2],b2[2])
    y2=min(b1[3],b2[3])

    inter=max(0,x2-x1)*max(0,y2-y1)

    a1=(b1[2]-b1[0])*(b1[3]-b1[1])
    a2=(b2[2]-b2[0])*(b2[3]-b2[1])

    union=a1+a2-inter

    if union==0:
        return 0

    return inter/union


def center_distance(c1,c2):
    return math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2)


# -----------------------------
# Load detections
# -----------------------------

def load_camera_detections(frame):

    detections=[]

    for cam in CAMERAS:

        path=f"{INPUT_DIR}/{cam}/frame_{frame:03d}.json"

        if not os.path.exists(path):
            continue

        with open(path) as f:
            data=json.load(f)

        for d in data["detections"]:

            if d["confidence"]<CONF_THRESHOLD:
                continue

            x1,y1,x2,y2=d["bbox"]
            area=(x2-x1)*(y2-y1)

            if area>MAX_BBOX_AREA:
                continue

            detections.append({
                "class":normalize_class(d["class_name"]),
                "bbox":d["bbox"],
                "confidence":d["confidence"],
                "camera":cam
            })

    return detections


# -----------------------------
# Remove duplicates
# -----------------------------

def remove_duplicates(detections):

    filtered=[]

    for det in detections:

        keep=True

        for f in filtered:

            iou=bbox_iou(det["bbox"],f["bbox"])

            if iou>DUPLICATE_IOU:

                if det["confidence"]>f["confidence"]:
                    filtered.remove(f)
                else:
                    keep=False

        if keep:
            filtered.append(det)

    return filtered


# -----------------------------
# Multi-camera fusion
# -----------------------------

def fuse_multi_camera(detections):

    grouped=[]

    for det in detections:

        matched=False

        for g in grouped:

            if det["class"]!=g["class"]:
                continue

            iou=bbox_iou(det["bbox"],g["bbox"])

            c1=bbox_center(det["bbox"])
            c2=bbox_center(g["bbox"])

            dist=center_distance(c1,c2)

            if iou>IOU_THRESHOLD or dist<CENTER_DIST_THRESHOLD:

                g["confidence"]=max(g["confidence"],det["confidence"])
                g["votes"]+=1
                g["sources"].append(det["camera"])

                matched=True
                break

        if not matched:

            grouped.append({
                "class":det["class"],
                "bbox":det["bbox"],
                "confidence":det["confidence"],
                "votes":1,
                "sources":[det["camera"]]
            })

    return grouped


# -----------------------------
# Temporal tracking
# -----------------------------

def track_objects(objects):

    global previous_tracks

    tracked=[]

    for obj in objects:

        center=bbox_center(obj["bbox"])

        obj_id=None

        for t in previous_tracks:

            if t["class"]!=obj["class"]:
                continue

            dist=center_distance(center,t["center"])

            if dist<CENTER_DIST_THRESHOLD:

                obj_id=t["id"]
                break

        if obj_id is None:
            obj_id=str(uuid.uuid4())[:8]

        tracked.append({
            "object_id":obj_id,
            "class":obj["class"],
            "confidence":round(obj["confidence"],3),
            "bbox_2d":obj["bbox"],
            "bbox_center":center,
            "camera_votes":obj["votes"],
            "source_cameras":list(set(obj["sources"]))
        })

    previous_tracks=[
        {
            "id":t["object_id"],
            "class":t["class"],
            "center":t["bbox_center"]
        }
        for t in tracked
    ]

    return tracked


# -----------------------------
# Process frame
# -----------------------------

def process_frame(frame):

    detections=load_camera_detections(frame)

    detections=remove_duplicates(detections)

    fused=fuse_multi_camera(detections)

    tracked=track_objects(fused)

    return tracked


# -----------------------------
# Main
# -----------------------------

def main():

    os.makedirs(OUTPUT_DIR,exist_ok=True)

    for frame in range(FRAME_COUNT):

        objects=process_frame(frame)

        out={
            "frame_index":frame,
            "objects":objects
        }

        with open(f"{OUTPUT_DIR}/frame_{frame:03d}.json","w") as f:
            json.dump(out,f,indent=4)

        print(f"Frame {frame:03d} → {len(objects)} objects fused")

    print("\nMulti-camera fusion completed")


if __name__=="__main__":
    main()