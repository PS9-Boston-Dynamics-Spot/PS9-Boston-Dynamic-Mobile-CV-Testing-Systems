from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from db.minio.connector.MinioConnector import MinioConnector
from minio import Minio

if __name__ == "__main__":
    robot_config = BostonDynamicsConfigReader()
    print(robot_config._getRobot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())
    print(robot_config.getPassword())

    with MinioConnector() as minio:
        print("minio.client")