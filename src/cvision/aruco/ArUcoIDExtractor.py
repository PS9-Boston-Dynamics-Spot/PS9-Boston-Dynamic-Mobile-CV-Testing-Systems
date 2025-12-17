import cv2
import cv2.aruco as aruco
import numpy as np
from credentials.manager.SettingsManager import SettingsManager


class ArUcoIDExtraktor:

    def __init__(self):
        self._settings_manager = SettingsManager()
        self.dict_name = self._settings_manager.getArUcoOverallDict()
        self.aruco_dict_id = getattr(aruco, self.dict_name)
        self.aruco_dict = aruco.getPredefinedDictionary(self.aruco_dict_id)
        self.parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.parameters)

    def get_id(self, image_bytes: bytes) -> int | None:

        np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            return None

        _, ids, _ = self.detector.detectMarkers(image)

        if ids is None:
            return None

        ids = ids.flatten().tolist()

        return ids[0]
