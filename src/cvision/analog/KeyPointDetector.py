from key_point_detection.key_point_inference import KeyPointInference, detect_key_points
import numpy as np
from PIL import Image, ImageDraw
import io
from common.imports.Typing import Literal, Tuple

class KeyPointDetector:

    RESOLUTION = (448, 448)

    def __init__(self, key_point_model_path: str = "./models/key_point_model.pt") -> None:
        self.key_point_model_path = key_point_model_path
        self.key_point_inferencer = KeyPointInference(key_point_model_path)

    def detect_key_points(self, image_bytes: bytes) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:

        img_resized = self.resize_image_bytes(image_bytes)

        buf = io.BytesIO()
        img_resized.save(buf, format="JPEG")
        resized_bytes = buf.getvalue()

        heatmaps = self.key_point_inferencer.predict_heatmaps(resized_bytes)
        key_point_list = detect_key_points(heatmaps)

        start_point = key_point_list[0]
        end_point = key_point_list[2]

        return start_point, end_point, self.RESOLUTION

    def resize_image_bytes(self, image_bytes: bytes):

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_resized = img.resize(self.RESOLUTION, Image.BICUBIC)
        return img_resized



def save_image_with_keypoints(img_pil, key_point_list, out_path):
    """
    Draw keypoints ON THE RESIZED IMAGE
    """
    draw = ImageDraw.Draw(img_pil)

    start_point, end_point = key_point_list

    def draw_point(x, y, r=4, color="red"):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    if start_point.shape == (1, 2):
        draw_point(start_point[0][0], start_point[0][1], color="green")

    if end_point.shape == (1, 2):
        draw_point(end_point[0][0], end_point[0][1], color="blue")

    img_pil.save(out_path)