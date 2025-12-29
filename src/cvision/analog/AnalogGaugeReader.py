import cv2
from cv2.typing import MatLike
import numpy as np
from cvision.analog.exceptions.ImageEncodingFailed import ImageEncodingFailed
from cvision.analog.exceptions.CenterNotFound import CenterNotFound
from credentials.manager.SettingsManager import SettingsManager
from cvision.analog.KeyPointDetector import KeyPointDetector
from common.imports.Typing import Tuple

class AnalogGaugeReader:

    def __init__(self, img: bytes) -> None:
        self._settings_manager = SettingsManager()
        img_array = np.frombuffer(img, dtype=np.uint8)
        self.__img: MatLike = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        self.kp_detector = KeyPointDetector()

    def __enter__(
        self,
    ):
        self.start_point, self.end_point, self.kp_resolution = self.kp_detector.detect_key_points(image_bytes)
        self.min_value, self.max_value = self._settings_manager.getMinMaxValue(category_name="pressure")

        self.units = self._settings_manager.getUnit(category_name="pressure")
        self.__images_log: bytes = []
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__images_log = []

    def __log_image(self, img: MatLike) -> None:
        success, encoded_img = cv2.imencode(".png", img)

        if not success:
            raise ImageEncodingFailed(error_code=1765392430)

        img_bytes = encoded_img.tobytes()
        self.__images_log.append(img_bytes)

    def get_images_log(self) -> list[bytes]:
        return self.__images_log

    def __dist_2_pts(self, x1: int, y1: int, x2: np.int32, y2: np.int32) -> np.float64:
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def __get_contours(self, img: MatLike, use_morph: bool = False) -> list[MatLike]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        self.__log_image(gray_blur)

        edges = self.__get_edges(img)

        if use_morph:
            kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close)

        self.__log_image(edges)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            print("Keine Konturen gefunden")
            return []

        out_img = img.copy()
        cv2.drawContours(out_img, contours, -1, (0, 255, 0), 2)
        self.__log_image(out_img)

        return contours

    def find_gauge_center_combined(self, img: np.ndarray) -> Tuple[int, int, int]:
        large_contours_normal = self.__get_contours(img=img, use_morph=False)
        large_contours_morph = self.__get_contours(img=img, use_morph=True)

        all_large_contours = large_contours_normal + large_contours_morph
        if not all_large_contours:
            print("Keine großen Konturen gefunden")
            return 0, 0, 0

        cnt = max(all_large_contours, key=cv2.contourArea)
        if len(cnt) < 5:
            print("Kontur zu klein für Ellipsen-Fit")
            return 0, 0, 0

        ellipse = cv2.fitEllipse(cnt)
        (cx, cy), (MA, ma), angle = ellipse
        cx, cy = int(cx), int(cy)
        radius = int((MA + ma) / 4)

        out = img.copy()
        cv2.ellipse(out, ellipse, (0, 255, 0), 2)
        cv2.circle(out, (cx, cy), 3, (0, 0, 255), -1)
        self.__log_image(out)

        print(f"Ellipse-Center: ({cx}, {cy}), Radius approx.: {radius}")
        return cx, cy, radius
    
    def __scale(self) -> Tuple[float, float, float, float]:
        h, w = self.__img.shape[:2]
        rx, ry = self.kp_resolution

        start_point_x = self.start_point[0][0] * (w / rx)
        start_point_y = self.start_point[0][1] * (h / ry)

        end_point_x = self.end_point[0][0] * (w / rx)
        end_point_y = self.end_point[0][1] * (h / ry)

        dbg = self.__img.copy()
        cv2.circle(dbg, (int(start_point_x), int(start_point_y)), 6, (0, 255, 0), -1)
        cv2.circle(dbg, (int(end_point_x), int(end_point_y)), 6, (255, 0, 0), -1)

        self.__log_image(img=dbg)

        return start_point_x, start_point_y, end_point_x, end_point_y
    
    def __calculate_angle(self, center_x: int, center_y: int) -> Tuple[float, float]:
        sx, sy, ex, ey = self.__scale()

        min_angle = self.__point_to_gauge_angle(center_x, center_y, sx, sy)
        max_angle = self.__point_to_gauge_angle(center_x, center_y, ex, ey)

        if max_angle < min_angle:
            max_angle += 360

        min_angle = min_angle - 2
        max_angle = max_angle - 2

        return min_angle, max_angle

    def __write_angles(self, img: MatLike, x: int, y: int, r: int) -> MatLike:

        separation = 3.0
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
        center_x, center_y, radius = self.find_gauge_center_combined(self.__img)
        if radius == 0:
            raise CenterNotFound(error_code=1765392500)

        self.min_angle, self.max_angle = self.__calculate_angle(center_x=center_x, center_y=center_y)

        img = self.__write_angles(img=self.__img, x=center_x, y=center_y, r=radius)

        self.__log_image(img)

        print(f"[CALIB] min={self.min_angle:.2f}°, max={self.max_angle:.2f}°")

        return center_x, center_y, radius


    def __get_edges(self, img: MatLike) -> MatLike:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 0)
        edges = cv2.Canny(gray, 50, 150)

        return edges

    def __draw_circle(
        self, img: MatLike, tip: tuple[int, int], x: int, y: int
    ) -> MatLike:
        cv2.line(img, (x, y), tip, (0, 255, 0), 2)
        cv2.circle(img, tip, 3, (0, 0, 255), -1)

        return img

    def get_current_value(self, x: int, y: int, r: int) -> float:

        edges = self.__get_edges(self.__img)

        self.__log_image(edges)

        lines = cv2.HoughLinesP(
            edges,
            rho=2,
            theta=np.pi / 180 * 2,
            threshold=90,
            minLineLength=5,
            maxLineGap=10,
        )

        out_img = self.__img.copy()

        if lines is None:
            print("No lines detected")
            return -1.0

        final_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(out_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            d1 = self.__dist_2_pts(x, y, x1, y1)
            d2 = self.__dist_2_pts(x, y, x2, y2)
            if d1 > d2:
                d1, d2 = d2, d1
            if 0.05 * r < d1 < 0.3 * r and 0.5 * r < d2 < 1.05 * r:
                final_lines.append([x1, y1, x2, y2])

        self.__log_image(out_img)

        if len(final_lines) == 0:
            print("Keine Linien im Radiusbereich gefunden")
            return -1.0

        best_line = max(
            final_lines,
            key=lambda line: self.__dist_2_pts(line[0], line[1], line[2], line[3]),
        )

        if self.__dist_2_pts(x, y, best_line[0], best_line[1]) > self.__dist_2_pts(
            x, y, best_line[2], best_line[3]
        ):
            tip = (best_line[0], best_line[1])
        else:
            tip = (best_line[2], best_line[3])

        dx = tip[0] - x
        dy = tip[1] - y
        angle_rad = np.arctan2(dy, dx)
        gauge_angle = (np.rad2deg(angle_rad) - 90) % 360
        print(f"Debug: gauge_angle = {gauge_angle:.2f}°")

        img_circles = self.__draw_circle(img=self.__img.copy(), tip=tip, x=x, y=y)
        self.__log_image(img_circles)

        old_range = float(self.max_angle) - float(self.min_angle)
        new_range = float(self.max_value) - float(self.min_value)

        if gauge_angle < float(self.min_angle):
            gauge_angle += 360

        new_value = (
            (gauge_angle - float(self.min_angle)) / old_range
        ) * new_range + float(self.min_value)
        print(f"Debug: gauge_value = {new_value:.2f}")
        return float(new_value)

    def __point_to_gauge_angle(
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






if __name__ == "__main__":
    with open("gauge-4-test.jpg", "rb") as f:
        image_bytes = f.read()

    print(image_bytes)

    # Gauge
    with AnalogGaugeReader(image_bytes) as gauge:
        cx, cy, r = gauge.calibrate()

        value = gauge.get_current_value(cx, cy, r)
        print("Gauge Value:", value)

        for idx, img_bytes in enumerate(gauge.get_images_log()):
            with open(f"test-{idx}.jpg", "wb") as f:
                f.write(img_bytes)
