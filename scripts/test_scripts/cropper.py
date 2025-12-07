import numpy as np
from PIL import Image
from ultralytics import YOLO
import cv2
from cv2.typing import MatLike
import io

Image.MAX_IMAGE_PIXELS = None

class GaugeCropper:

    def __init__(self, resolution=(1000, 1000), pad_color=(0, 0, 0), model: str = "./models/detection_model.pt"):
        self.resolution = resolution
        self.pad_color = list(pad_color)
        self.model = YOLO(model)

    def detect_gauge_face(self, img: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:

        results = self.model(img)

        boxes = results[0].boxes
        if len(boxes) == 0:
            raise Exception("No gauge detected in image")

        main_box = boxes[0]

        all_boxes = [box.xyxy[0].int() for box in boxes]

        return main_box.xyxy[0].int(), all_boxes

    def crop(self, img: np.ndarray, box, return_padding=False, two_dimensional=False) -> MatLike:
        img_copy = np.copy(img)

        if two_dimensional:
            cropped = img_copy[box[1]:box[3], box[0]:box[2]]
        else:
            cropped = img_copy[box[1]:box[3], box[0]:box[2], :]

        height = int(box[3] - box[1])
        width = int(box[2] - box[0])

        if height > width:
            delta = height - width
            pad_left = delta // 2
            pad_right = delta - pad_left
            pad_top = pad_bottom = 0
        else:
            delta = width - height
            pad_top = delta // 2
            pad_bottom = delta - pad_top
            pad_left = pad_right = 0

        padded = cv2.copyMakeBorder(
            cropped,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            cv2.BORDER_CONSTANT,
            value=self.pad_color
        )

        if return_padding:
            return padded, (pad_top, pad_bottom, pad_left, pad_right)
        return padded

    def process(self, image) -> MatLike:
        if not isinstance(image, np.ndarray):
            image = Image.open(image).convert("RGB")
            image = np.asarray(image)

        box, _ = self.detect_gauge_face(image)

        cropped_img = self.crop(image, box)

        cropped_resized_img = cv2.resize(
            cropped_img,
            dsize=(512, 512),
            interpolation=cv2.INTER_CUBIC
        )

        pil_img = Image.fromarray(cropped_resized_img)

        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        return buffer.getvalue()



if __name__ == '__main__':

    input_image = "test.jpg"
    output_path = "gauge-5.jpg"

    gauge_cropper = GaugeCropper()
    image_bytes = gauge_cropper.process(image=input_image)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print("Gespeichert unter:", output_path)
