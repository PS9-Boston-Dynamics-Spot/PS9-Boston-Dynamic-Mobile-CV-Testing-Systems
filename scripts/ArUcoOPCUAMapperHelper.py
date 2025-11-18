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

        config = {
            "overall_dict": self._get_dict_name(),
            "nodes": {}
        }

        for file in sorted(self.directory.iterdir()):
            if file.is_file() and file.suffix.lower() in [".jpeg", ".jpg", ".png"]:
                ids = self._get_ids(str(file))
                if not ids:
                    continue

                first_id = int(ids[0])

                stem = file.stem
                if re.fullmatch(r"\d+", stem):
                    node_key = f"node_{first_id}"
                else:
                    node_key = stem if stem else f"node_{first_id}"

                config["nodes"][node_key] = {
                    "opcua_node": "",     
                    "aruco_id": first_id
                }

        output_path = self.directory / "opcua_nodes_config.yaml"

        with open(output_path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        return str(output_path)

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
    # Example call with the directory where the markers are located and the marker dictionary configuration
    extractor = ArUcoOPCUAMapperHelper("../data/ArUco/", dict_const=aruco.DICT_6X6_1000)
    print(extractor.get_opcua_nodes_config())
