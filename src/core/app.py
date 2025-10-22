from common.utils.reader.BostonDynamicsReader import BostonDynamicsConfigReader
from minio import Minio

if __name__ == "__main__":
    robot_config = BostonDynamicsConfigReader()
    print(robot_config._get_robot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())
    print(robot_config.getPassword())

    client = Minio(
        "minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
    )

    # Liste Buckets
    buckets = client.list_buckets()
    for b in buckets:
        print(b.name)
