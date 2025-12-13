import os

from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from configs.reader.MinioBucketConfigReader import MinioBucketConfigReader

from db.dal.DataAccessLayer import DataAccessLayer
from db.mapping.RawImageMapper import RawImageMapper
from db.mapping.AnalyzedImageMapper import AnalyzedImageMapper

from configs.mapper.ArUcoIDOPCUANodeMapper import ArUcoIDOPCUANodeMapper
from db.mapping.AnomalyMapper import AnomalyMapper
from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager
from anomaly.AnomalyChecker import AnomalyChecker
#raw Daten Croppen und speichern in Bytestream + crop folder
from common.cvision.roboflow import run_roboflow_inference, crop_predictions

if __name__ == "__main__":

    settings_manager = UnifiedCredentialsManager()
    robot_settings = settings_manager.getRobotCredentials()
    print(robot_settings)

    path = os.path.join(os.getcwd(), "test.jpg")

    with open(path, "rb") as f:
        image_bytes = f.read()

        raw_image_mapper = RawImageMapper()
        analyzed_image_mapper = AnalyzedImageMapper()

        with DataAccessLayer() as dal:
            image_name = "sensor_captasduaspsasvasgasdhhdaasdsdassdsasadfsddamdasdasdasdsasdsjhkdfgdffgfdsdasdfdre_001"

            aruco_node_mapper = ArUcoIDOPCUANodeMapper()
            opcua_node_id = aruco_node_mapper.get_opcua_node_by_id(aruco_id=46)
            print(dal.get_value_from_opcua_node(opcua_node_id=opcua_node_id))

            dto_raw_image = raw_image_mapper.map_image(
                image_data=image_bytes, size=22223429223
            )
            raw_image_id = dal.insert_raw_image(raw_image_with_metadata=dto_raw_image)

            # get the aruco id through image extraction
            aruco_id = 46
            
            aruco_node_mapper = ArUcoIDOPCUANodeMapper()
            opcua_node_id = aruco_node_mapper.get_opcua_node_by_id(aruco_id=aruco_id)

            opcua_node_id = settings_manager.getOPCUANodeByID(aruco_id=aruco_id)

            #analyzed image mit metadata in db speichern

            result = run_roboflow_inference(path)

            predictions = result["outputs"][0]["predictions"]["predictions"][:2]
            print(f"Roboflow returned {len(predictions)} predictions.")

            # Crops erzeugen (JPG speichern + Bytes erzeugen)
            cropped_images = crop_predictions(path, predictions)
            print(f"{len(cropped_images)} Cropped images created.")

            # Erfassung der Daten aus dem Crop wird noch implementiert
            detected_value = 23.0
            unit = "°C"
            category = "temperature"


            # JEDEN CROP in cvision_images_analyzed speichern
            
            for crop in cropped_images:

                dto_analyzed_image = analyzed_image_mapper.map_image(
                    image_data=crop["bytes"],        # BYTES → DB
                    raw_image_id=raw_image_id,       # Verbindung zum Raw-Bild
                    sensor_type=crop["sensor_type"],         # aus Roboflow
                    opcua_node_id=opcua_node_id,
                    aruco_id=aruco_id,
                    category=category,
                    quality=1.0,
                    value=detected_value,
                    unit=unit
                )

            analyzed_image_id = dal.insert_analyzed_image(
                analyzed_image_with_metadata=dto_analyzed_image
            )

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

            min_value, max_value = settings_manager.getMinMaxValue(aruco_id=aruco_id)

            anomaly_checker = AnomalyChecker()
            anomaly_score, is_anomaly = anomaly_checker.is_anomaly(
                value_to_check=detected_value,
                aruco_id=aruco_id,
            )
            print(anomaly_score, is_anomaly)

            parameters = settings_manager.getParametersForAnomalyMapper(
                aruco_id=aruco_id
            )

            anomaly_mapper = AnomalyMapper()
            anomaly_dto = anomaly_mapper.map_anomaly(
                analyzed_image_id=analyzed_image_id,
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                used_funtion=settings_manager.getScoreFunctionStr(aruco_id=aruco_id),
                **parameters,
            )

            dal.insert_anomaly(anomaly_with_metadata=anomaly_dto)
            print("Inserted both images:", id)
