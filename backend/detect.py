from ultralytics import YOLO
import os

# -----------------------------------------
# Load trained YOLO model
# -----------------------------------------
model = YOLO("best.pt")

# -----------------------------------------
# Images folder
# -----------------------------------------
image_folder = "images"

# Find all image files
image_files = [
    f for f in os.listdir(image_folder)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
]

# Check if folder is empty
if not image_files:
    print("No image found inside the 'images' folder.")
    exit()

# -----------------------------------------
# Process every image in the folder
# -----------------------------------------
for image_name in image_files:

    image_path = os.path.join(image_folder, image_name)

    print("\n" + "=" * 60)
    print("Testing Image:", image_name)
    print("=" * 60)

    # Run detection
    results = model.predict(
        source=image_path,
        conf=0.25,
        save=True,
        project="output",
        name="prediction",
        exist_ok=True
    )

    # Count detected objects
    counts = {
        "red blood cell": 0,
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

    # Display summary
    print("\nDetection Summary")
    print("-" * 40)

    print(f"Red Blood Cells : {counts['red blood cell']}")
    print(f"Leukocytes      : {counts['leukocyte']}")
    print(f"Ring            : {counts['ring']}")
    print(f"Trophozoite     : {counts['trophozoite']}")
    print(f"Schizont        : {counts['schizont']}")
    print(f"Gametocyte      : {counts['gametocyte']}")

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

    print("\nDiagnosis :", diagnosis)

print("\n" + "=" * 60)
print("All images processed successfully!")
print("Prediction images are saved in:")
print("output/prediction/")
print("=" * 60)