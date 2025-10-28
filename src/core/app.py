from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
import os
from db.dal.DataAccessLayer import DataAccessLayer

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
        metadata_raw = {
            "image_data": image_bytes,
            "name": "sensor_captusaasasddsdasdre_001",
            "format": "jpg",
            "bucket": "raw-images",
            "size": len(image_bytes),  # in Bytes
            "compressed": False,
            "compression_method": None,
        }

        with DataAccessLayer() as dal:
            result = dal.insert_raw_image(metadata_raw)
            print("Inserted raw image:", result)
