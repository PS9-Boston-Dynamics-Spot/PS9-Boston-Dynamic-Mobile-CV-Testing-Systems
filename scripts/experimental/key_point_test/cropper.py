import numpy as np
from PIL import Image
from ultralytics import YOLO
import cv2
from cv2.typing import MatLike
import io
from cvision.analog.exceptions.GaugeDetectionFailed import GaugeDetectionFailed
import os

Image.MAX_IMAGE_PIXELS = None


class AnalogGaugeCropper:

    def __init__(
        self,
        resolution=(1000, 1000),
        pad_color=(0, 0, 0),
        model: str = os.path.join(
            os.getcwd(), "./models/analog_gauge_detection_model.pt"
        ),
    ):
        self.resolution = resolution
        self.pad_color = list(pad_color)
        self.model = YOLO(model)

    def __detect_gauge_face(self, img: MatLike) -> tuple[np.ndarray, list[np.ndarray]]:

        results = self.model(img)

        boxes = results[0].boxes
        if len(boxes) == 0:
            raise GaugeDetectionFailed(error_code=1765392590)

        main_box = boxes[0]

        all_boxes = [box.xyxy[0].int() for box in boxes]

        return main_box.xyxy[0].int(), all_boxes

    def __crop(self, box, img: MatLike) -> MatLike:
        cropped = img[box[1] : box[3], box[0] : box[2], :]

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
            value=self.pad_color,
        )

        return padded

    def process(self, img: bytes) -> bytes:
        img_array = np.frombuffer(img, dtype=np.uint8)
        img: MatLike = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        box, _ = self.__detect_gauge_face(img=img)

        cropped_img = self.__crop(box=box, img=img)

        cropped_resized_img = cv2.resize(
            cropped_img, dsize=(512, 512), interpolation=cv2.INTER_CUBIC
        )

        pil_img = Image.fromarray(cropped_resized_img)

        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        return buffer.getvalue()


if __name__ == "__main__":
    cropper = AnalogGaugeCropper()
    with open("gauge-4.jpg", "rb") as f:
        img = f.read()
    print(cropper.process(img))

    # write image
    with open("gauge-4-test.jpg", "wb") as f:
        f.write(cropper.process(img))
