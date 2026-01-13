import subprocess
import sys
from pathlib import Path

from db.dal.DataAccessLayer import DataAccessLayer
from app_lifespan import (
    services,
    process_analog_image,
    check_anomaly,
    handle_anomaly,
    process_digital_image,
)

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]
    robot_script = project_root / "src/common/sdk/robot_movement.py"
    graph_path = project_root / "data/map/downloaded_graph"

    subprocess.run(
        [sys.executable, str(robot_script), "-u", str(graph_path)],
        check=True,
        cwd=str(robot_script.parent),
    )

    path = project_root / "src/common/sdk/spot_bilder/spot.jpg"

    with open(path, "rb") as f:
        image_bytes = f.read()

    aruco_id = services.aruco_extractor.get_id(image_bytes=image_bytes)

    aruco_id_analog = None
    category_name_analog = "pressure"
    opcua_node_id = services.settings_manager.getOPCUANodeByID(
        aruco_id=aruco_id_analog, category_name=category_name_analog
    )

    with DataAccessLayer() as dal:
        dto_raw_image = services.raw_image_mapper.map_image(image_data=image_bytes)
        raw_image_id = dal.insert_raw_image(raw_image_with_metadata=dto_raw_image)

        # at first, process analog gauge
        print("Aruco IDs: ", aruco_id)

        if aruco_id is None:
            raise Exception("No aruco id found in image")

        analyzed_image_id, detected_value = process_analog_image(
            dal=dal,
            image_bytes=image_bytes,
            raw_image_id=raw_image_id,
            opcua_node_id=opcua_node_id,
            aruco_id=aruco_id_analog,
            category_name=category_name_analog,
        )

        is_anomaly = check_anomaly(
            dal=dal,
            analyzed_image_id=analyzed_image_id,
            detected_value=detected_value,
            aruco_id=aruco_id_analog,
            category_name=category_name_analog,
        )

        handle_anomaly(is_anomaly=is_anomaly)

        # TODO: same for digital sensors

        for analyzed_image_id, detected_value, category in process_digital_image(
            dal=dal,
            image_bytes=image_bytes,
            raw_image_id=raw_image_id,
            opcua_node_id=opcua_node_id,
            aruco_id=aruco_id,
        ):
            is_anomaly = check_anomaly(
                dal=dal,
                analyzed_image_id=analyzed_image_id,
                detected_value=detected_value,
                aruco_id=aruco_id,
                category_name=category,
            )

            handle_anomaly(is_anomaly=is_anomaly)
