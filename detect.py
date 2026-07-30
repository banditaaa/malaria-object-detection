from ultralytics import YOLO
import os


# Load model once
model = YOLO("best.pt")


def detect_image(image_path):

    # Run YOLO prediction

    results = model.predict(
        source=image_path,
        conf=0.25,
        save=True,
        project="output",
        name="prediction",
        exist_ok=True
    )


    # Count objects

    counts = {

        "red_blood_cell": 0,
        "leukocyte": 0,
        "ring": 0,
        "trophozoite": 0,
        "schizont": 0,
        "gametocyte": 0

    }


    # Read detections

    for result in results:

        for box in result.boxes:

            cls = int(box.cls)

            label = model.names[cls].lower()


            if label in counts:
                counts[label] += 1



    # Diagnosis

    if (
        counts["ring"] > 0 or
        counts["trophozoite"] > 0 or
        counts["schizont"] > 0 or
        counts["gametocyte"] > 0
    ):

        diagnosis = "INFECTED"

    else:

        diagnosis = "UNINFECTED"



    # Prediction image path

    filename = os.path.basename(image_path)

    predicted_image = (
        "output/prediction/" + filename
    )


    return {

        "counts": counts,

        "diagnosis": diagnosis,

        "predicted_image": predicted_image

    }