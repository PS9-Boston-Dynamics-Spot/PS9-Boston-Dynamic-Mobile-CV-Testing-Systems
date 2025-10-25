from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from db.media.repository.MediaRepository import MediaRepository
import os

if __name__ == "__main__":
    robot_config = BostonDynamicsConfigReader()
    print(robot_config._getRobot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())
    print(robot_config.getPassword())

    path = os.path.join(os.path.dirname(__file__), "test.png")
    print(
        MediaRepository(bucket_name="ps9-analyzer-bucket").get_media(object_name="test")
    )
    #MediaRepository(bucket_name="asd").put_media(object_name="test", file_path=path)
    print(MediaRepository.get_buckets())
    print(MediaRepository(bucket_name="ps9-analyzer-bucket").get_objects())
    print(MediaRepository.get_everything_recursive())
