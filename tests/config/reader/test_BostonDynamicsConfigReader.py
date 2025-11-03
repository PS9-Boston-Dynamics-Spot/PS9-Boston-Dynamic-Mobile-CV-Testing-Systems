import unittest
from unittest.mock import patch
from configs.reader.BostonDynamicsConfigReader import BostonDynamicsConfigReader
from configs.enum.ConfigEnum import ROBOT_KEYS


class TestBostonDynamicsConfigReader(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            ROBOT_KEYS.ROBOT: {
                ROBOT_KEYS.IP: "192.168.0.101",
                ROBOT_KEYS.WIFI: "MyWifi",
                ROBOT_KEYS.USER: "robotuser",
                ROBOT_KEYS.PASSWORD: "robotpass",
            }
        }

    @patch.object(BostonDynamicsConfigReader, "load_config")
    def test_get_robot_methods(self, mock_load_config):
        mock_load_config.return_value = self.mock_config

        reader = BostonDynamicsConfigReader()

        robot_data = reader._getRobot()
        self.assertEqual(robot_data, self.mock_config[ROBOT_KEYS.ROBOT])

        self.assertEqual(reader.getIP(), "192.168.0.101")
        self.assertEqual(reader.getWifi(), "MyWifi")
        self.assertEqual(reader.getUser(), "robotuser")
        self.assertEqual(reader.getPassword(), "robotpass")

    @patch.object(BostonDynamicsConfigReader, "load_config")
    def test_missing_robot_section(self, mock_load_config):
        mock_load_config.return_value = {}
        reader = BostonDynamicsConfigReader()

        self.assertIsNone(reader.getIP())
        self.assertIsNone(reader.getWifi())
        self.assertIsNone(reader.getUser())
        self.assertIsNone(reader.getPassword())

    @patch.object(BostonDynamicsConfigReader, "load_config")
    def test_partial_robot_config(self, mock_load_config):
        mock_load_config.return_value = {ROBOT_KEYS.ROBOT: {ROBOT_KEYS.IP: "10.0.0.1"}}
        reader = BostonDynamicsConfigReader()

        self.assertEqual(reader.getIP(), "10.0.0.1")
        self.assertIsNone(reader.getWifi())
        self.assertIsNone(reader.getUser())
        self.assertIsNone(reader.getPassword())

    @patch.object(BostonDynamicsConfigReader, "load_config")
    def test_boston_edge_none_robot_section(self, mock_load_config):
        mock_load_config.return_value = {ROBOT_KEYS.ROBOT: None}
        reader = BostonDynamicsConfigReader()
        self.assertIsNone(reader.getIP())
        self.assertIsNone(reader.getWifi())
        self.assertIsNone(reader.getUser())
        self.assertIsNone(reader.getPassword())

    @patch.object(BostonDynamicsConfigReader, "load_config")
    def test_boston_edge_wrong_type_robot_section(self, mock_load_config):
        mock_load_config.return_value = {
            ROBOT_KEYS.ROBOT: ["list", "instead", "of", "dict"]
        }
        reader = BostonDynamicsConfigReader()
        self.assertIsNone(reader.getIP())
        self.assertIsNone(reader.getWifi())
        self.assertIsNone(reader.getUser())
        self.assertIsNone(reader.getPassword())
