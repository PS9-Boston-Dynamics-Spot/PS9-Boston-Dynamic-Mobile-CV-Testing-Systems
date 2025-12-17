import os

from db.dal.DataAccessLayer import DataAccessLayer
from app_lifespan import (
    services,
    process_analog_image,
    check_anomaly_analog_gauge,
    handle_anomaly,
)

if __name__ == "__main__":

    categories = services.settings_manager.getCategoriesNameByNodeID(aruco_id=46)
    print("categories: ", categories)
    exit(0)

    path = os.path.join(os.getcwd(), "spot2.jpg")

    with open(path, "rb") as f:
        image_bytes = f.read()

    # TODO: move spot to machine and capture picture

    with DataAccessLayer() as dal:
        dto_raw_image = services.raw_image_mapper.map_image(image_data=image_bytes)
        raw_image_id = dal.insert_raw_image(raw_image_with_metadata=dto_raw_image)

        aruco_id = services.aruco_extractor.get_id(image_bytes=image_bytes)
        print("Aruco IDs: ", aruco_id)

        if aruco_id is None:
            raise Exception("No aruco id found in image")

        opcua_node_id = services.settings_manager.getOPCUANodeByID(aruco_id=aruco_id)

        analyzed_image_id, detected_value = process_analog_image(
            dal=dal,
            image_bytes=image_bytes,
            raw_image_id=raw_image_id,
            opcua_node_id=opcua_node_id,
            aruco_id=aruco_id,
        )

        is_anomaly = check_anomaly_analog_gauge(
            dal=dal,
            analyzed_image_id=analyzed_image_id,
            detected_value=detected_value,
            aruco_id=None,
            allow_missing=True,
        )

        handle_anomaly(is_anomaly=is_anomaly)

        # TODO: same for digital sensors

        print("Inserted both images:", id)
