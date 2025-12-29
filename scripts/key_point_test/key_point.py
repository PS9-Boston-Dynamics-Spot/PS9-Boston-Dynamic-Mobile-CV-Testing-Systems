from key_point_detection.key_point_inference import KeyPointInference, detect_key_points
import numpy as np
from PIL import Image, ImageDraw
import io

RESOLUTION = (448, 448)

class KeyPointDetector:

    def __init__(self, key_point_model_path: str = "./models/key_point_model.pt") -> None:
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



# =====================
# Entry point
# =====================
if __name__ == "__main__":

    # Load image as bytes
    with open("gauge-4-test.jpg", "rb") as f:
        image_bytes = f.read()

    # Resize once
    resized_img = resize_image_bytes(image_bytes, RESOLUTION)

    # Run inference
    key_point_detector = KeyPointDetector()
    start_point, end_point = key_point_detector.detect_key_points(image_bytes=image_bytes)

    print("start_point", start_point)
    print("end_point", end_point)

    # Save debug image with keypoints
    save_image_with_keypoints(
        resized_img,
        key_point_list=[start_point, end_point],
        out_path="test4.jpg"
    )

    print("Saved debug image with keypoints to test3.jpg")
