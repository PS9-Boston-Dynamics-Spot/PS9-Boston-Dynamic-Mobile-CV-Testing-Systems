import cv2
import cv2.aruco as aruco
from pathlib import Path
from typing import List


class ArUcoIDExtractor:

    def __init__(self) -> None:

        self.dict = aruco.DICT_6X6_250
        self.aruco_dict = aruco.getPredefinedDictionary(self.dict)
        self.parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.parameters)

        return

    def get_id(self, file_path: str) -> List[int]:

        if not Path(file_path).exists():
            raise FileNotFoundError

        image = cv2.imread(file_path)

        _, ids, _ = self.detector.detectMarkers(image)

        return ids.flatten().tolist()


if __name__ == "__main__":

    extraktor = ArUcoIDExtractor()
    print(extraktor.get_id("../data/ArUco/ArUco(11).jpeg"))
