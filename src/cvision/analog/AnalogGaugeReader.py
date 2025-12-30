import cv2
from cv2.typing import MatLike
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Optional

from cvision.analog.exceptions.ImageEncodingFailed import ImageEncodingFailed
from cvision.analog.exceptions.CenterNotFound import CenterNotFound
from credentials.manager.SettingsManager import SettingsManager
from cvision.analog.KeyPointDetector import KeyPointDetector


@dataclass
class GaugeCalibration:
    center_x: int
    center_y: int
    radius: int
    min_angle: float
    max_angle: float
    min_value: float
    max_value: float


@dataclass
class ScaledPoints:
    start_x: float
    start_y: float
    end_x: float
    end_y: float


class GaugeDetectionConfig:
    # Canny edge detection
    CANNY_THRESHOLD_LOW = 50
    CANNY_THRESHOLD_HIGH = 150
    GAUSSIAN_KERNEL = (9, 9)
    MEDIAN_BLUR_KERNEL = 5

    # Morphological operations
    MORPH_KERNEL_SIZE = (7, 7)

    # Hough line detection
    HOUGH_RHO = 2
    HOUGH_THETA = np.pi / 180 * 2
    HOUGH_THRESHOLD = 90
    HOUGH_MIN_LINE_LENGTH = 5
    HOUGH_MAX_LINE_GAP = 10

    # Line filtering (relative to radius)
    LINE_FILTER_MIN_D1 = 0.05
    LINE_FILTER_MAX_D1 = 0.3
    LINE_FILTER_MIN_D2 = 0.5
    LINE_FILTER_MAX_D2 = 1.05

    # Angle visualization
    ANGLE_SEPARATION = 3.0
    ANGLE_ADJUSTMENT = -2.0  # Degrees to subtract from min/max angles

    # Ellipse fitting
    MIN_CONTOUR_POINTS = 5


class AnalogGaugeReader:

    def __init__(self, img: bytes, category: str = "pressure") -> None:
        self._settings_manager = SettingsManager()
        self._category = category
        self._img_bytes = img

        img_array = np.frombuffer(img, dtype=np.uint8)
        self._img: MatLike = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if self._img is None:
            raise ValueError("Failed to decode image")

        self.kp_detector = KeyPointDetector()
        self._images_log: List[bytes] = []
        self._calibration: Optional[GaugeCalibration] = None

    def __enter__(self):
        self.start_point, self.end_point, self.kp_resolution = (
            self.kp_detector.detect_key_points(self._img_bytes)
        )

        self.min_value, self.max_value = self._settings_manager.getMinMaxValue(
            category_name=self._category
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._images_log.clear()

    def _log_image(self, img: MatLike) -> None:
        success, encoded_img = cv2.imencode(".png", img)

        if not success:
            raise ImageEncodingFailed(error_code=1765392430)

        img_bytes = encoded_img.tobytes()
        self._images_log.append(img_bytes)

    def get_images_log(self) -> List[bytes]:
        return self._images_log

    @staticmethod
    def _calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _get_edges(self, img: MatLike) -> MatLike:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, GaugeDetectionConfig.GAUSSIAN_KERNEL, 0)
        edges = cv2.Canny(
            gray,
            GaugeDetectionConfig.CANNY_THRESHOLD_LOW,
            GaugeDetectionConfig.CANNY_THRESHOLD_HIGH,
        )
        return edges

    def _get_contours(self, img: MatLike, use_morph: bool = False) -> List[MatLike]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, GaugeDetectionConfig.MEDIAN_BLUR_KERNEL)
        self._log_image(gray_blur)

        edges = self._get_edges(img)

        if use_morph:
            kernel_close = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, GaugeDetectionConfig.MORPH_KERNEL_SIZE
            )
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close)

        self._log_image(edges)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            print("Warning: No contours found")
            return []

        out_img = img.copy()
        cv2.drawContours(out_img, contours, -1, (0, 255, 0), 2)
        self._log_image(out_img)

        return contours

    def find_gauge_center_combined(self, img: np.ndarray) -> Tuple[int, int, int]:
        large_contours_normal = self._get_contours(img=img, use_morph=False)
        large_contours_morph = self._get_contours(img=img, use_morph=True)

        all_large_contours = large_contours_normal + large_contours_morph
        if not all_large_contours:
            print("Warning: No large contours found")
            return 0, 0, 0

        cnt = max(all_large_contours, key=cv2.contourArea)
        if len(cnt) < GaugeDetectionConfig.MIN_CONTOUR_POINTS:
            print(
                f"Warning: Contour too small for ellipse fitting "
                f"(need {GaugeDetectionConfig.MIN_CONTOUR_POINTS} points)"
            )
            return 0, 0, 0

        ellipse = cv2.fitEllipse(cnt)
        (cx, cy), (MA, ma), angle = ellipse
        cx, cy = int(cx), int(cy)
        radius = int((MA + ma) / 4)

        out = img.copy()
        cv2.ellipse(out, ellipse, (0, 255, 0), 2)
        cv2.circle(out, (cx, cy), 3, (0, 0, 255), -1)
        self._log_image(out)

        print(f"Ellipse center: ({cx}, {cy}), approximate radius: {radius}")
        return cx, cy, radius

    def _scale_keypoints(self) -> ScaledPoints:
        h, w = self._img.shape[:2]
        rx, ry = self.kp_resolution

        start_x = self.start_point[0][0] * (w / rx)
        start_y = self.start_point[0][1] * (h / ry)
        end_x = self.end_point[0][0] * (w / rx)
        end_y = self.end_point[0][1] * (h / ry)

        dbg = self._img.copy()
        cv2.circle(dbg, (int(start_x), int(start_y)), 6, (0, 255, 0), -1)
        cv2.circle(dbg, (int(end_x), int(end_y)), 6, (255, 0, 0), -1)
        self._log_image(img=dbg)

        return ScaledPoints(start_x, start_y, end_x, end_y)

    def _point_to_gauge_angle(
        self,
        cx: int,
        cy: int,
        px: float,
        py: float,
    ) -> float:
        dx = px - cx
        dy = py - cy
        angle_rad = np.arctan2(dy, dx)
        return (np.rad2deg(angle_rad) - 90) % 360

    def _calculate_angle_range(
        self, center_x: int, center_y: int
    ) -> Tuple[float, float]:
        scaled = self._scale_keypoints()

        min_angle = self._point_to_gauge_angle(
            center_x, center_y, scaled.start_x, scaled.start_y
        )
        max_angle = self._point_to_gauge_angle(
            center_x, center_y, scaled.end_x, scaled.end_y
        )

        if max_angle < min_angle:
            max_angle += 360

        min_angle += GaugeDetectionConfig.ANGLE_ADJUSTMENT
        max_angle += GaugeDetectionConfig.ANGLE_ADJUSTMENT

        return min_angle, max_angle

    def _visualize_angles(self, img: MatLike, x: int, y: int, r: int) -> MatLike:
        separation = GaugeDetectionConfig.ANGLE_SEPARATION
        angles = np.arange(0, 360, separation)
        rad = np.deg2rad(angles)

        p1 = np.column_stack((x + 0.9 * r * np.cos(rad), y + 0.9 * r * np.sin(rad)))
        p2 = np.column_stack((x + 1.0 * r * np.cos(rad), y + 1.0 * r * np.sin(rad)))

        label_rad = np.deg2rad(angles + 90)
        p_text = np.column_stack(
            (x + 1.2 * r * np.cos(label_rad), y + 1.2 * r * np.sin(label_rad))
        )

        for i, angle in enumerate(angles):
            cv2.line(
                img,
                (int(p1[i, 0]), int(p1[i, 1])),
                (int(p2[i, 0]), int(p2[i, 1])),
                (0, 255, 0),
                2,
            )
            cv2.putText(
                img,
                str(int(angle)),
                (int(p_text[i, 0]), int(p_text[i, 1])),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        return img

    def calibrate(self) -> Tuple[int, int, int]:
        center_x, center_y, radius = self.find_gauge_center_combined(self._img)

        if radius == 0:
            raise CenterNotFound(error_code=1765392500)

        min_angle, max_angle = self._calculate_angle_range(center_x, center_y)

        self._calibration = GaugeCalibration(
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            min_angle=min_angle,
            max_angle=max_angle,
            min_value=self.min_value,
            max_value=self.max_value,
        )

        img = self._visualize_angles(
            img=self._img.copy(), x=center_x, y=center_y, r=radius
        )
        self._log_image(img)

        print(f"[CALIBRATION] min_angle={min_angle:.2f}°, max_angle={max_angle:.2f}°")

        return center_x, center_y, radius

    def _filter_lines_by_radius(
        self, lines: np.ndarray, center_x: int, center_y: int, radius: int
    ) -> List[List[int]]:
        final_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            d1 = self._calculate_distance(center_x, center_y, x1, y1)
            d2 = self._calculate_distance(center_x, center_y, x2, y2)

            if d1 > d2:
                d1, d2 = d2, d1

            if (
                GaugeDetectionConfig.LINE_FILTER_MIN_D1 * radius
                < d1
                < GaugeDetectionConfig.LINE_FILTER_MAX_D1 * radius
                and GaugeDetectionConfig.LINE_FILTER_MIN_D2 * radius
                < d2
                < GaugeDetectionConfig.LINE_FILTER_MAX_D2 * radius
            ):
                final_lines.append([x1, y1, x2, y2])

        return final_lines

    def _find_pointer_tip(
        self, line: List[int], center_x: int, center_y: int
    ) -> Tuple[int, int]:
        x1, y1, x2, y2 = line

        d1 = self._calculate_distance(center_x, center_y, x1, y1)
        d2 = self._calculate_distance(center_x, center_y, x2, y2)

        return (x1, y1) if d1 > d2 else (x2, y2)

    def _angle_to_value(self, gauge_angle: float) -> float:
        if self._calibration is None:
            raise RuntimeError("Gauge must be calibrated before reading values")

        if gauge_angle < self._calibration.min_angle:
            gauge_angle += 360

        old_range = self._calibration.max_angle - self._calibration.min_angle
        new_range = self._calibration.max_value - self._calibration.min_value

        new_value = (
            (gauge_angle - self._calibration.min_angle) / old_range
        ) * new_range + self._calibration.min_value

        return float(new_value)

    def get_current_value(self, x: int, y: int, r: int) -> float:
        edges = self._get_edges(self._img)
        self._log_image(edges)

        lines = cv2.HoughLinesP(
            edges,
            rho=GaugeDetectionConfig.HOUGH_RHO,
            theta=GaugeDetectionConfig.HOUGH_THETA,
            threshold=GaugeDetectionConfig.HOUGH_THRESHOLD,
            minLineLength=GaugeDetectionConfig.HOUGH_MIN_LINE_LENGTH,
            maxLineGap=GaugeDetectionConfig.HOUGH_MAX_LINE_GAP,
        )

        if lines is None:
            print("Warning: No lines detected")
            return -1.0

        out_img = self._img.copy()
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(out_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        self._log_image(out_img)

        final_lines = self._filter_lines_by_radius(lines, x, y, r)

        if len(final_lines) == 0:
            print("Warning: No lines found within expected radius range")
            return -1.0

        best_line = max(
            final_lines,
            key=lambda line: self._calculate_distance(
                line[0], line[1], line[2], line[3]
            ),
        )

        tip = self._find_pointer_tip(best_line, x, y)

        dx = tip[0] - x
        dy = tip[1] - y
        angle_rad = np.arctan2(dy, dx)
        gauge_angle = (np.rad2deg(angle_rad) - 90) % 360

        if gauge_angle <= self._calibration.min_angle:
            return self.min_value

        if gauge_angle >= self._calibration.max_angle:
            return self.max_value

        print(f"Debug: gauge_angle = {gauge_angle:.2f}°")

        img_circles = self._img.copy()
        cv2.line(img_circles, (x, y), tip, (0, 255, 0), 2)
        cv2.circle(img_circles, tip, 3, (0, 0, 255), -1)
        self._log_image(img_circles)

        gauge_value = self._angle_to_value(gauge_angle)
        print(f"Debug: gauge_value = {gauge_value:.2f}")

        return gauge_value


# def main() -> None:
#     with open("test2.jpg", "rb") as f:
#         image_bytes = f.read()

#     with AnalogGaugeReader(image_bytes, category="pressure") as gauge:
#         cx, cy, r = gauge.calibrate()
#         value = gauge.get_current_value(cx, cy, r)

#         print(f"Gauge Value: {value:.2f} {gauge.units}")

#         for idx, img_bytes in enumerate(gauge.get_images_log()):
#             with open(f"test-{idx}.png", "wb") as f:
#                 f.write(img_bytes)


# if __name__ == "__main__":
#     main()
