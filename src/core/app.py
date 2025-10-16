from common.utils.BostonDynamicLoader import BostonDynamicsConfigLoader

if __name__ == "__main__":
    robot_config = BostonDynamicsConfigLoader()
    print(robot_config._get_robot())
    print(robot_config.getIP())
    print(robot_config.getUser())
    print(robot_config.getWifi())