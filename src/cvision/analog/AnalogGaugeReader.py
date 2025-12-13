import cv2
from cv2.typing import MatLike
import numpy as np
from cvision.analog.exceptions.ImageEncodingFailed import ImageEncodingFailed
from cvision.analog.exceptions.CenterNotFound import CenterNotFound
from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager


class AnalogGaugeReader:

    def __init__(self, img: bytes) -> None:
        self.credentials_manager = UnifiedCredentialsManager()
        img_array = np.frombuffer(img, dtype=np.uint8)
        self.__img: MatLike = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    def __enter__(
        self,
    ):
        # TODO: read from config
        self.min_angle = self.credentials_manager.getAnalogGaugeMinAngle()
        self.max_angle = self.credentials_manager.getAnalogGaugeMaxAngle()
        self.min_value = self.credentials_manager.getAnalogGaugeMinValue()
        self.max_value = self.credentials_manager.getAnalogGaugeMaxValue()
        self.units = self.credentials_manager.getAnalogGaugeUnit()
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

    def find_gauge_center_combined(self, img: MatLike) -> tuple[int, int, int]:

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        self.__log_image(gray_blur)

        circles = cv2.HoughCircles(
            gray_blur,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,
            param1=100,
            param2=40,
            minRadius=0,
            maxRadius=50,
        )

        if circles is not None:
            circles = np.uint16(np.around(circles[0]))
            selected_circle = min(circles, key=lambda c: c[2])
            cx, cy, _ = selected_circle
            print(f"Hough-Circle Center gefunden: ({cx}, {cy})")
        else:
            cx, cy = None, None
            print("Hough-Circle: Kein Center gefunden!")

        edges = self.__get_edges(img)
        self.__log_image(edges)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            print("Fallback: Keine Konturen gefunden!")
            return None, None, None

        cnt = max(contours, key=cv2.contourArea)
        if len(cnt) < 5:
            print("Fallback: Kontur zu klein!")
            return None, None, None

        (MA, ma) = cv2.fitEllipse(cnt)[1]
        (_, _), radius_circle = cv2.minEnclosingCircle(cnt)
        radius = (
            int((MA + ma) / 4 + radius_circle) // 2
        )  # Average of major and minor axis
        print(f"Fallback Radius: {radius}")

        if cx is None or cy is None:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = 0, 0  # fallback
            print(f"Fallback Center verwendet: ({cx}, {cy})")

        out = img.copy()
        cv2.circle(out, (cx, cy), radius, (0, 255, 0), 2)
        cv2.circle(out, (cx, cy), 3, (0, 0, 255), -1)
        self.__log_image(out)

        return cx, cy, radius

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

    def calibrate_gauge(self) -> tuple[int, int, int]:
        result = self.find_gauge_center_combined(img=self.__img)

        if result is None:
            raise CenterNotFound(error_code=1765392500)

        x, y, r = result

        cv2.circle(self.__img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.circle(self.__img, (x, y), 3, (0, 255, 0), -1, cv2.LINE_AA)

        img = self.__write_angles(img=self.__img, x=x, y=y, r=r)

        self.__log_image(img)

        return x, y, r

    def __get_edges(self, img: MatLike) -> MatLike:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
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

        if lines is None:
            print("No lines detected")
            return 0

        final_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            d1 = self.__dist_2_pts(x, y, x1, y1)
            d2 = self.__dist_2_pts(x, y, x2, y2)
            if d1 > d2:
                d1, d2 = d2, d1
            if 0.05 * r < d1 < 0.3 * r and 0.5 * r < d2 < 1.05 * r:
                final_lines.append([x1, y1, x2, y2])

        if len(final_lines) == 0:
            print("Keine Linien im Radiusbereich gefunden")
            return 0

        best_line = max(
            final_lines, key=lambda l: self.__dist_2_pts(l[0], l[1], l[2], l[3])
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


def main():
    with open("./gauge-51.jpg", "rb") as f:
        img = f.read()

    with AnalogGaugeReader(img=img) as analog_gauge_reader:
        x, y, r = analog_gauge_reader.calibrate_gauge()
        value = analog_gauge_reader.get_current_value(x, y, r)

        for idx, img_bytes in enumerate(analog_gauge_reader.get_images_log()):
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imwrite(f"./{idx}.png", img)


if __name__ == "__main__":
    main()
