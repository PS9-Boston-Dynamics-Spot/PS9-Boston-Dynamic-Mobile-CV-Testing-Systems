from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
import os
from db.dal.DataAccessLayer import DataAccessLayer
from db.mapping.RawImageMapper import RawImageMapper
from db.mapping.AnalyzedImageMapper import AnalyzedImageMapper
from configs.reader.MinioBucketConfigReader import MinioBucketConfigReader
from configs.reader.OPCUANodesConfigReader import OPCUANodesConfigReader
from db.mapping.AnomalyMapper import AnomalyMapper


if __name__ == "__main__":
    robot_config = BostonDynamicsConfigReader()
    print(robot_config._getRobot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())
    print(robot_config.getPassword())

    path = os.path.join(os.path.dirname(__file__), "OPCUA.jpeg")
    with open(path, "rb") as f:
        image_bytes = f.read()
        bucket_config_reader = MinioBucketConfigReader()
        raw_bucket = bucket_config_reader.getRawBucket()
        analyzed_bucket = bucket_config_reader.getAnalyzedBucket()

        raw_image_mapper = RawImageMapper()

        with DataAccessLayer() as dal:
            dto_raw_image = raw_image_mapper.map_image(
                image_data=image_bytes,
                bucket=raw_bucket,
            )

            raw_image_id = dal.insert_raw_image(raw_image_with_metadata=dto_raw_image)

            analyzed_image_mapper = AnalyzedImageMapper()
            dto_analyzed_image = analyzed_image_mapper.map_image(
                image_data=image_bytes,
                raw_image_id=raw_image_id,
                bucket=analyzed_bucket,
                sensor_type="test2",
                opcua_node_id="test_node",
                aruco_id=123,
                category="test2",
                quality=1.0,
                value=10.0,
                unit="°C_2",
            )
            analyzed_image_id = dal.insert_analyzed_image(
                anaylzed_image_with_metadata=dto_analyzed_image
            )

            # get the aruco id through image extraction
            aruco_id = 46
            opcua_nodes_config_reader = OPCUANodesConfigReader()
            # opcua_node_id = opcua_nodes_config_reader.getOPCUANodebyID(aruco_id=aruco_id)
            opcua_node_id = 'ns=3;s="dbAppCtrl"."Hmi"."Obj"."EB"."Proc"."rActVal"'

            # TODO: check if value is an anomaly
            # value = dal.get_value_from_opcua_node(opcua_node_id=opcua_node_id)

            anomaly_mapper = AnomalyMapper()
            anomaly_dto = anomaly_mapper.map_anomaly(
                analyzed_image_id=analyzed_image_id,
                detected_value=23.0,
                comparative_value=24.0,  # e.g. 1% tolerance
                is_anomaly=False,
                node_id=opcua_node_id,
            )

            dal.insert_anomaly(anomaly_with_metadata=anomaly_dto)
