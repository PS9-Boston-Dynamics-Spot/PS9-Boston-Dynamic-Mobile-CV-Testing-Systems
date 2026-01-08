from PIL import Image
import io

from cvision.analog.key_point_detection.key_point_extraction import (
    full_key_point_extraction,
)
from cvision.analog.key_point_detection.model import load_model
from cvision.analog.key_point_detection.key_point_dataset import custom_transforms


class KeyPointInference:
    def __init__(self, model_path):

        self.model = load_model(model_path)

    def predict_heatmaps(self, image_bytes: bytes):

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_t = custom_transforms(train=False, image=img)
        image_t = image_t.unsqueeze(0)

        heatmaps = self.model(image_t)

        heatmaps = heatmaps.detach().squeeze(0).numpy()

        return heatmaps


def detect_key_points(heatmaps):
    key_point_list = full_key_point_extraction(heatmaps, 0.6)

    return key_point_list
