from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2

# Load your trained model
model = YOLO("best.pt")

# Image path
image_path = "images/5836500a-221e-40ca-a8be-caaa37f7d300.png"

# Run prediction (does NOT save anything)
results = model.predict(
    source=image_path,
    conf=0.25,
    save=False,
    verbose=False
)

# Draw bounding boxes
annotated = results[0].plot()

# Convert BGR to RGB
annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

# Display
plt.figure(figsize=(10, 10))
plt.imshow(annotated)
plt.title("Malaria Detection")
plt.axis("off")
plt.show()