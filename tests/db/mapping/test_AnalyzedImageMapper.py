import unittest
from unittest.mock import patch

from db.mapping.input.AnalyzedImageMapper import AnalyzedImageDTO, AnalyzedImageMapper


class TestAnalyzedImageDTO(unittest.TestCase):

    def setUp(self):
        self.valid_kwargs = {
            "image_data": b"fake-image-bytes",
            "raw_image_id": 1,
            "name": "test_image",
            "format": "PNG",  # wird zu "png" normalisiert
            "content_type": "image/png",
            "bucket": "test-bucket",
            "size": 1234,
            "sensor_type": "camera",
            "category": "test-category",
            "quality": 0.95,
            "value": 42.0,
            "unit": "score",
            "compressed": False,
            "compression_method": None,
        }

    def test_valid_creation_and_format_normalization(self):
        dto = AnalyzedImageDTO(**self.valid_kwargs)

        # kein Fehler, Feldwerte korrekt
        self.assertEqual(dto.name, "test_image")
        # Format soll klein geschrieben werden
        self.assertEqual(dto.format, "png")

    def test_to_dict_returns_all_fields(self):
        dto = AnalyzedImageDTO(**self.valid_kwargs)
        d = dto.to_dict()

        self.assertIsInstance(d, dict)
        # ein paar Stichproben
        self.assertEqual(d["name"], "test_image")
        self.assertEqual(d["format"], "png")
        self.assertEqual(d["raw_image_id"], 1)
        self.assertEqual(d["compressed"], False)

    def test_not_null_fields_must_not_be_none(self):
        not_null_fields = [
            "image_data",
            "raw_image_id",
            "name",
            "format",
            "bucket",
            "size",
            "content_type",
            "sensor_type",
            "category",
            "quality",
            "value",
            "unit",
        ]

        for field_name in not_null_fields:
            with self.subTest(field=field_name):
                kwargs = self.valid_kwargs.copy()
                kwargs[field_name] = None

                with self.assertRaises(ValueError):
                    AnalyzedImageDTO(**kwargs)

    def test_type_validation_for_some_fields(self):
        # image_data muss bytes sein
        kwargs = self.valid_kwargs.copy()
        kwargs["image_data"] = "not-bytes"
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)

        # raw_image_id muss int sein
        kwargs = self.valid_kwargs.copy()
        kwargs["raw_image_id"] = "1"
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)

        # size muss int sein
        kwargs = self.valid_kwargs.copy()
        kwargs["size"] = 12.34
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)

        # quality muss float sein
        kwargs = self.valid_kwargs.copy()
        kwargs["quality"] = 1  # int
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)

        # value muss float sein
        kwargs = self.valid_kwargs.copy()
        kwargs["value"] = 10  # int
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)

        # compressed muss bool sein
        kwargs = self.valid_kwargs.copy()
        kwargs["compressed"] = "false"
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)

        # compression_method darf entweder None oder str sein
        kwargs = self.valid_kwargs.copy()
        kwargs["compression_method"] = 123
        with self.assertRaises(TypeError):
            AnalyzedImageDTO(**kwargs)


class TestAnalyzedImageMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = AnalyzedImageMapper()
        self.image_data = b"image-bytes"
        self.base_kwargs = {
            "image_data": self.image_data,
            "raw_image_id": 1,
            "name": "mapped_image",
            "bucket": "test-bucket",
            "sensor_type": "camera",
            "category": "test-category",
            "quality": 0.9,
            "value": 100.0,
            "unit": "EUR",
        }

    @patch("db.mapping.AnalyzedImageMapper.MapperHelper.get_bytes_length")
    @patch("db.mapping.AnalyzedImageMapper.MapperHelper.guess_content_type")
    @patch("db.mapping.AnalyzedImageMapper.MapperHelper.guess_file_extension")
    def test_map_image_uses_mapperhelper_when_optional_params_missing(
        self,
        mock_guess_file_extension,
        mock_guess_content_type,
        mock_get_bytes_length,
    ):
        mock_guess_file_extension.return_value = "jpg"
        mock_guess_content_type.return_value = "image/jpeg"
        mock_get_bytes_length.return_value = 999

        dto = self.mapper.map_image(**self.base_kwargs)

        # MapperHelper-Funktionen müssen aufgerufen worden sein
        mock_guess_file_extension.assert_called_once_with(self.image_data)
        mock_guess_content_type.assert_called_once_with(self.image_data)
        mock_get_bytes_length.assert_called_once_with(self.image_data)

        # DTO enthält die zurückgegebenen Werte
        self.assertEqual(dto.format, "jpg")
        self.assertEqual(dto.content_type, "image/jpeg")
        self.assertEqual(dto.size, 999)

    @patch("db.mapping.AnalyzedImageMapper.MapperHelper.get_bytes_length")
    @patch("db.mapping.AnalyzedImageMapper.MapperHelper.guess_content_type")
    @patch("db.mapping.AnalyzedImageMapper.MapperHelper.guess_file_extension")
    def test_map_image_uses_explicit_values_if_provided(
        self,
        mock_guess_file_extension,
        mock_guess_content_type,
        mock_get_bytes_length,
    ):
        # explizite Werte übergeben
        dto = self.mapper.map_image(
            **self.base_kwargs,
            format="png",
            content_type="image/png",
            size=1234,
            compressed=True,
            compression_method="lz4",
        )

        # MapperHelper darf in diesem Fall nicht benutzt werden
        mock_guess_file_extension.assert_not_called()
        mock_guess_content_type.assert_not_called()
        mock_get_bytes_length.assert_not_called()

        # DTO muss exakt die expliziten Werte enthalten
        self.assertEqual(dto.format, "png")
        self.assertEqual(dto.content_type, "image/png")
        self.assertEqual(dto.size, 1234)
        self.assertTrue(dto.compressed)
        self.assertEqual(dto.compression_method, "lz4")

        # und der Rest der Werte sollte auch stimmen
        self.assertEqual(dto.raw_image_id, 1)
        self.assertEqual(dto.bucket, "test-bucket")
        self.assertEqual(dto.sensor_type, "camera")
        self.assertEqual(dto.category, "test-category")
        self.assertEqual(dto.quality, 0.9)
        self.assertEqual(dto.value, 100.0)
        self.assertEqual(dto.unit, "EUR")


if __name__ == "__main__":
    unittest.main()
