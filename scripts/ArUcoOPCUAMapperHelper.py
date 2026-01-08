import cv2
import cv2.aruco as aruco
from pathlib import Path
from typing import List
import yaml
import re


class ArUcoOPCUAMapperHelper:

    def __init__(self, directory: str, dict_const=aruco.DICT_6X6_1000) -> None:
        self.directory = Path(directory)
        self.dict = dict_const
        self.aruco_dict = aruco.getPredefinedDictionary(self.dict)
        self.parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.parameters)

    def _get_dict_name(self) -> str:
        for name in dir(aruco):
            if name.startswith("DICT_") and getattr(aruco, name) == self.dict:
                return name
        return str(self.dict)

    def get_opcua_nodes_config(self) -> str:
        """
        Creates a YAML config with:
        - exactly one 'analog_gauge' node
        - multiple OPCUA nodes mapped from ArUco markers
        """

        config = {
            "overall_dict": self._get_dict_name(),
            "nodes": {"analog_gauge": self._default_analog_gauge_config()},
        }

        for file in sorted(self.directory.iterdir()):
            if not file.is_file() or file.suffix.lower() not in [
                ".jpeg",
                ".jpg",
                ".png",
            ]:
                continue

            ids = self._get_ids(str(file))
            if not ids:
                continue

            aruco_id = int(ids[0])

            stem = file.stem
            if re.fullmatch(r"\d+", stem):
                node_key = f"node_{aruco_id}"
            else:
                node_key = stem

            # Skip accidental overwrite of analog_gauge
            if node_key == "analog_gauge":
                node_key = f"node_{aruco_id}"

            config["nodes"][node_key] = {
                "opcua_node": "",
                "aruco_id": aruco_id,
                "score_function": (
                    "1.0 if min_value <= x <= max_value else "
                    "min_score+(1-min_score)*exp(-pow((min_value-x)/left_scale,left_power)) "
                    "if x < min_value else "
                    "min_score+(1-min_score)*exp(-pow((x-max_value)/right_scale,right_power))"
                ),
                "parameters": {
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "min_score": 0.0,
                    "left_scale": 7.0,
                    "left_power": 2.0,
                    "right_scale": 7.0,
                    "right_power": 2.0,
                },
                "risk_management": {
                    "safe_range": 1.0,
                    "uncertain_range": 0.5,
                    "anomaly_range": 0.0,
                },
            }

        output_path = self.directory / "opcua_nodes_config.yaml"
        with open(output_path, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

        return str(output_path)

    def _default_analog_gauge_config(self) -> dict:
        """Exactly one analog gauge configuration."""
        return {
            "min_angle": 43.87,
            "max_angle": 310.0,
            "unit": "bar",
            "score_function": (
                "1.0 if min_value <= x <= max_value else "
                "min_score+(1-min_score)*exp(-pow((min_value-x)/left_scale,left_power)) "
                "if x < min_value else "
                "min_score+(1-min_score)*exp(-pow((x-max_value)/right_scale,right_power))"
            ),
            "parameters": {
                "min_value": 0.0,
                "max_value": 6.0,
                "min_score": 0.0,
                "left_scale": 7.0,
                "left_power": 2.0,
                "right_scale": 7.0,
                "right_power": 2.0,
            },
            "risk_management": {
                "safe_range": 1.0,
                "uncertain_range": 0.5,
                "anomaly_range": 0.0,
            },
        }

    def _get_ids(self, file_path: str) -> List[int]:
        if not Path(file_path).exists():
            raise FileNotFoundError(file_path)

        image = cv2.imread(file_path)
        if image is None:
            return []

        _, ids, _ = self.detector.detectMarkers(image)
        if ids is None:
            return []

        return ids.flatten().astype(int).tolist()


if __name__ == "__main__":
    extractor = ArUcoOPCUAMapperHelper("../data/ArUco/", dict_const=aruco.DICT_6X6_1000)
    print(extractor.get_opcua_nodes_config())
