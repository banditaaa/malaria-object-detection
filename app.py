from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import os
import cv2
import uuid

app = Flask(__name__)
CORS(app)

# ---------------------------------------
# Load YOLO Model
# ---------------------------------------
model = YOLO("best.pt")

# ---------------------------------------
# Folders
# ---------------------------------------
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}

# ---------------------------------------
# Home
# ---------------------------------------
@app.route("/")
def home():
    return "Backend Running"


# ---------------------------------------
# Serve Result Images
# ---------------------------------------
@app.route("/results/<filename>")
def get_result(filename):
    return send_from_directory(RESULT_FOLDER, filename)


# ---------------------------------------
# Prediction API
# ---------------------------------------
@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "No image selected"}), 400

    extension = image.filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported image format"}), 400

    unique_name = f"{uuid.uuid4()}.{extension}"

    image_path = os.path.join(
        UPLOAD_FOLDER,
        unique_name
    )

    image.save(image_path)

    print("Image received:", image_path)

    # ---------------------------------------
    # YOLO Prediction
    # ---------------------------------------
    results = model.predict(
        source=image_path,
        conf=0.25,
        verbose=False
    )

    result = results[0]

    # ---------------------------------------
    # Save Bounding Box Image
    # ---------------------------------------
    annotated = result.plot()

    output_filename = "result_" + unique_name

    output_path = os.path.join(
        RESULT_FOLDER,
        output_filename
    )

    cv2.imwrite(
        output_path,
        annotated
    )

    print("Bounding Box Image Saved:", output_path)

    # ---------------------------------------
    # Initialize Counters
    # ---------------------------------------
    counts = {
        "red blood cell": 0,
        "leukocyte": 0,
        "ring": 0,
        "trophozoite": 0,
        "schizont": 0,
        "gametocyte": 0
    }

    infected_cells = []
    parasite_confidences = []

    # ---------------------------------------
    # Read YOLO Detections
    # ---------------------------------------
    for box in result.boxes:

        cls = int(box.cls[0])
        confidence = float(box.conf[0])
        label = model.names[cls].lower()

        if label in counts:

            counts[label] += 1

            if label in [
                "ring",
                "trophozoite",
                "schizont",
                "gametocyte"
            ]:

                parasite_confidences.append(confidence)

                infected_cells.append({
                    "type": label.title(),
                    "confidence": round(confidence * 100, 2)
                })

    # Highest confidence first
    infected_cells.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    # ---------------------------------------
    # Analysis
    # ---------------------------------------
    parasite_count = (
        counts["ring"] +
        counts["trophozoite"] +
        counts["schizont"] +
        counts["gametocyte"]
    )

    normal_cells = (
        counts["red blood cell"] +
        counts["leukocyte"]
    )

    total_objects = parasite_count + normal_cells

    infection_percentage = (
        (parasite_count / total_objects) * 100
        if total_objects > 0
        else 0
    )

    average_confidence = (
        (sum(parasite_confidences) / len(parasite_confidences)) * 100
        if parasite_confidences
        else 0
    )

    # ---------------------------------------
    # Final Diagnosis
    # ---------------------------------------
    diagnosis = (
        "INFECTED"
        if parasite_count > 0
        else "UNINFECTED"
    )

    # ---------------------------------------
    # Response
    # ---------------------------------------
    return jsonify({

        "diagnosis": diagnosis,

        "uploaded_image": unique_name,

        "image": output_filename,

        "detections": counts,

        "parasite_count": parasite_count,

        "normal_cells": normal_cells,

        "total_objects": total_objects,

        "infection_percentage": round(
            infection_percentage,
            2
        ),

        "average_confidence": round(
            average_confidence,
            2
        ),

        "infected_cells": infected_cells

    })


# ---------------------------------------
# Run Flask
# ---------------------------------------
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )