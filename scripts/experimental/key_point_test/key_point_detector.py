from key_point_detection.key_point_inference import KeyPointInference, detect_key_points
import numpy as np
from PIL import Image, ImageDraw
import io

RESOLUTION = (448, 448)


class KeyPointDetector:

    def __init__(
        self, key_point_model_path: str = "./models/key_point_model.pt"
    ) -> None:
        self.key_point_model_path = key_point_model_path
        self.key_point_inferencer = KeyPointInference(key_point_model_path)

    def detect_key_points(self, image_bytes: bytes) -> tuple[float, float]:

        heatmaps = self.key_point_inferencer.predict_heatmaps(image_bytes)

        for i, hm in enumerate(heatmaps):
            hm_norm = hm - hm.min()
            if hm_norm.max() > 0:
                hm_norm /= hm_norm.max()

            hm_img = Image.fromarray((hm_norm * 255).astype(np.uint8))
            hm_img = hm_img.resize(RESOLUTION, Image.BICUBIC)

            hm_img.save(f"./heatmap_{i:02d}.png")

        key_point_list = detect_key_points(heatmaps)

        start_point = key_point_list[0]
        end_point = key_point_list[2]

        return (start_point, end_point)


def resize_image_bytes(image_bytes, resolution):
    """
    Bytes -> resized PIL Image
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_resized = img.resize(resolution, Image.BICUBIC)
    return img_resized
