import unittest
import tempfile
from pathlib import Path
import yaml
from configs.loader.ConfigLoader import ConfigLoader
from configs.exceptions.ConfigLoadError import ConfigLoadError
from configs.exceptions.ConfigNotFound import ConfigNotFound
from configs.exceptions.ConfigParseError import ConfigParseError


class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        self.loader = ConfigLoader()

    def test_load_valid_config(self):
        config_data = {"key": "value", "number": 42}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.safe_dump(config_data, tmp)
            tmp_path = tmp.name

        try:
            result = self.loader.load_config(tmp_path)
            self.assertEqual(result, config_data)
        finally:
            Path(tmp_path).unlink()

    def test_file_not_found(self):
        with self.assertRaises(ConfigNotFound):
            self.loader.load_config("non_existing_file.yaml")

    def test_invalid_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("::: this is invalid YAML :::")
            tmp_path = tmp.name

        try:
            with self.assertRaises(ConfigLoadError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_yaml_not_dict(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.safe_dump(["a", "b", "c"], tmp)
            tmp_path = tmp.name

        try:
            with self.assertRaises(ConfigParseError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_empty_yaml_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with self.assertRaises(ConfigParseError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_yaml_with_null_root(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("null")
            tmp_path = tmp.name
        try:
            with self.assertRaises(ConfigParseError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_yaml_with_string_root(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("just a string")
            tmp_path = tmp.name
        try:
            with self.assertRaises(ConfigParseError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_yaml_with_number_root(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("12345")
            tmp_path = tmp.name
        try:
            with self.assertRaises(ConfigParseError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_yaml_invalid_utf8(self):
        # Not valid UTF-8 bytes
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".yaml", delete=False
        ) as tmp:
            tmp.write(b"\xff\xfe\xfd")
            tmp_path = tmp.name
        try:
            with self.assertRaises(ConfigLoadError):
                self.loader.load_config(tmp_path)
        finally:
            Path(tmp_path).unlink()
