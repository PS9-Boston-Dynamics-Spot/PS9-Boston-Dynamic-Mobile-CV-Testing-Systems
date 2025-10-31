from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
import os
from db.dal.DataAccessLayer import DataAccessLayer
from db.mapping.RawImageMapper import RawImageMapper
from db.mapping.AnalyzedImageMapper import AnalyzedImageMapper
from configs.reader.MinioBucketConfigReader import MinioBucketConfigReader

if __name__ == "__main__":
    robot_config = BostonDynamicsConfigReader()
    print(robot_config._getRobot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())
    print(robot_config.getPassword())

    path = os.path.join(os.path.dirname(__file__), "test.jpg")
    """    print(
        MediaRepository(bucket_name="ps9-analyzer-bucket").get_media(object_name="test")
    )
    #MediaRepository(bucket_name="asd").put_media(object_name="test", file_path=path)
    print(MediaRepository.get_buckets())
    print(MediaRepository(bucket_name="ps9-analyzer-bucket").get_objects())
    print(MediaRepository.get_everything_recursive())
    """
    with open(path, "rb") as f:
        image_bytes = f.read()
        bucket_config_reader = MinioBucketConfigReader()
        raw_bucket = bucket_config_reader.getRawBucket()
        analyzed_bucket = bucket_config_reader.getAnalyzedBucket()

        raw_image_mapper = RawImageMapper()
        image_name = "sensor_captusaasdaasdsasddasdasdsasdsdffdsdasdre_001"

        dto_raw_image = raw_image_mapper.map_image(
            image_data=image_bytes,
            name=image_name,  # TODO: generate name automatically through uuid or hash
            bucket=raw_bucket,
        )

        with DataAccessLayer() as dal:
            raw_image_id = dal.insert_raw_image(raw_image_with_metadata=dto_raw_image)
            print("Inserted raw image:", id)

        analyzed_image_mapper = AnalyzedImageMapper()
        dto_analyzed_image = analyzed_image_mapper.map_image(
            image_data=image_bytes,
            raw_image_id=raw_image_id,
            name=image_name,  # TODO: generate name automatically through uuid or hash
            bucket=analyzed_bucket,
            sensor_type="test",
            category="test",
            quality=1.0,
            value=10.0,
            unit="°C",
        )

        with DataAccessLayer() as dal:
            result = dal.insert_analyzed_image(anaylzed_image_with_metadata=dto_analyzed_image)
            print("Inserted analyzed image:", result)
