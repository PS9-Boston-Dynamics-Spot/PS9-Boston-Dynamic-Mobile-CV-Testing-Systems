from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from db.media.repository.MediaRepository import MediaRepository
import os
from db.dal.DataAccessLayer import DataAccessLayer

if __name__ == "__main__":
    robot_config = BostonDynamicsConfigReader()
    print(robot_config._getRobot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())
    print(robot_config.getPassword())

    path = os.path.join(os.path.dirname(__file__), "test.png")
    """    print(
        MediaRepository(bucket_name="ps9-analyzer-bucket").get_media(object_name="test")
    )
    #MediaRepository(bucket_name="asd").put_media(object_name="test", file_path=path)
    print(MediaRepository.get_buckets())
    print(MediaRepository(bucket_name="ps9-analyzer-bucket").get_objects())
    print(MediaRepository.get_everything_recursive())
    """

    metadata_raw = {
        "file_path": path,
        "name": "sensor_capture_001",
        "format": "png",
        "bucket": "raw-images",
        "size": 204800,  # in Bytes
        "compressed": False,
        "compression_method": None
    }

    with DataAccessLayer() as dal:
        result = dal.insert_raw_image(metadata_raw)
        print("Inserted raw image:", result)
