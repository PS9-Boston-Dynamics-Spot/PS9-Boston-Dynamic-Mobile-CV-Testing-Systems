from common.utils.ConfigLoader import ConfigLoader


class BostonDynamicLoader(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.config = self.load_config("configs/robot-credentials.yaml")

    def checkConfig(self):
        if self.config is None:
            raise Exception("Config not found")

    def _get_robot(self):
        return

    def getIP(self):

        pass

    def getWifi(self):
        pass

    def getUser(self):
        pass

    def getPassword(self):
        pass
