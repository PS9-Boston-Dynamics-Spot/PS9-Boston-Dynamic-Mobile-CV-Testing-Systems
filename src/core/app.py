import os
from db.dal.DataAccessLayer import DataAccessLayer
from db.mapping.RawImageMapper import RawImageMapper
from db.mapping.AnalyzedImageMapper import AnalyzedImageMapper
from db.mapping.AnomalyMapper import AnomalyMapper
from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager
from anomaly.AnomalyChecker import AnomalyChecker
from cvision.analog.AnalogGaugeReader import AnalogGaugeReader
from cvision.analog.AnalogGaugeCropper import AnalogGaugeCropper
from cvision.aruco.ArUcoIDExtractor import ArUcoIDExtraktor
import dataclasses
import numpy as np
import cv2

@dataclasses.dataclass
class Initializer:

    raw_image_mapper: RawImageMapper = dataclasses.field(default_factory=RawImageMapper)
    analyzed_image_mapper: AnalyzedImageMapper = dataclasses.field(
        default_factory=AnalyzedImageMapper
    )
    anomaly_mapper: AnomalyMapper = dataclasses.field(default_factory=AnomalyMapper)
    settings_manager: UnifiedCredentialsManager = dataclasses.field(
        default_factory=UnifiedCredentialsManager
    )
    aruco_extractor: ArUcoIDExtraktor = dataclasses.field(
        default_factory=ArUcoIDExtraktor
    )
    anomaly_checker: AnomalyChecker = dataclasses.field(default_factory=AnomalyChecker)
    analog_gauge_cropper: AnalogGaugeCropper = dataclasses.field(
        default_factory=AnalogGaugeCropper
    )


initializer = Initializer()
services = initializer

def safe_analyzed_image(
    dal: DataAccessLayer,
    image_bytes: bytes,
    raw_image_id: int,
    sensor_type: str,
    opcua_node_id: str,
    aruco_id: int,
    detected_value: float,
    unit: str,
) -> int:

    dto_analyzed_image = services.analyzed_image_mapper.map_image(
        image_data=image_bytes,
        raw_image_id=raw_image_id,
        sensor_type=sensor_type,
        opcua_node_id=opcua_node_id,
        aruco_id=aruco_id,
        category="testsdfsdfdfss",
        quality=1.0,
        value=detected_value,
        unit=unit,
    )
    analyzed_image_id = dal.insert_analyzed_image(
        anaylzed_image_with_metadata=dto_analyzed_image
    )

    return analyzed_image_id


if __name__ == "__main__":

    path = os.path.join(os.getcwd(), "test.jpg")

    with open(path, "rb") as f:
        image_bytes = f.read()

        with DataAccessLayer() as dal:
            image_name = "tesasdt"

            dto_raw_image = services.raw_image_mapper.map_image(
                image_data=image_bytes
            )
            raw_image_id = dal.insert_raw_image(raw_image_with_metadata=dto_raw_image)

            aruco_id = services.aruco_extractor.get_id(image_bytes=image_bytes)
            print("Aruco IDs: ", aruco_id)

            if aruco_id is None:
                raise Exception("No aruco id found in image")
            

            opcua_node_id = services.settings_manager.getOPCUANodeByID(
                aruco_id=aruco_id
            )

            cropped_analog_gauge_image = services.analog_gauge_cropper.process(
                img=image_bytes
            )
            analog_unit = services.settings_manager.getAnalogGaugeUnit()

            with AnalogGaugeReader(img=cropped_analog_gauge_image) as analog_gauge_reader:
                x, y, r = analog_gauge_reader.calibrate_gauge()
                detected_value = analog_gauge_reader.get_current_value(x, y, r)

                for idx, img_bytes in enumerate(analog_gauge_reader.get_images_log()):

                    analyzed_image_id = safe_analyzed_image(
                        dal=dal,
                        image_bytes=img_bytes,
                        raw_image_id=raw_image_id,
                        sensor_type="analog",
                        opcua_node_id=opcua_node_id,
                        aruco_id=aruco_id,
                        detected_value=detected_value,
                        unit=analog_unit,
                    )

            analyzed_image_id = safe_analyzed_image(
                dal=dal,
                image_bytes=cropped_analog_gauge_image,
                raw_image_id=raw_image_id,
                sensor_type="analog",
                opcua_node_id=opcua_node_id,
                aruco_id=aruco_id,
                detected_value=detected_value,
                unit=analog_unit,
            )

            exit(0)

            #########################################################################################################################
            # TODO: get the comparative value from the opcua node / config file + image extraction and check if value is an anomaly #
            #                                                                                                                       #
            # extratc value from image (digital value)                                                                              #
            # do something ....                                                                                                     #
            #                                                                                                                       #
            # get comparative value from opcua (digital value)                                                                      #
            # value = dal.get_value_from_opcua_node(opcua_node_id=opcua_node_id)                                                    #
            #                                                                                                                       #
            # extract value from image (analog value)                                                                               #
            # do something ...                                                                                                      #
            #                                                                                                                       #
            # get comparative value from config file (analog value)                                                                 #
            # value = settings_manager.getAnalogComparativeValue(aruco_id=aruco_id)                                                 #
            #########################################################################################################################

            # min_value, max_value = services.settings_manager.getMinMaxValue(
            #     aruco_id=aruco_id
            # )

            # anomaly_checker = AnomalyChecker()
            # anomaly_score, is_anomaly = anomaly_checker.is_anomaly(
            #     value_to_check=detected_value,
            #     aruco_id=aruco_id,
            # )
            # print(anomaly_score, is_anomaly)

            # parameters = services.settings_manager.getParametersForAnomalyMapper(
            #     aruco_id=aruco_id
            # )

            # anomaly_mapper = AnomalyMapper()
            # anomaly_dto = anomaly_mapper.map_anomaly(
            #     analyzed_image_id=analyzed_image_id,
            #     is_anomaly=is_anomaly,
            #     anomaly_score=anomaly_score,
            #     used_funtion=services.settings_manager.getScoreFunctionStr(
            #         aruco_id=aruco_id
            #     ),
            #     **parameters,
            # )

            # dal.insert_anomaly(anomaly_with_metadata=anomaly_dto)
            # print("Inserted both images:", id)
