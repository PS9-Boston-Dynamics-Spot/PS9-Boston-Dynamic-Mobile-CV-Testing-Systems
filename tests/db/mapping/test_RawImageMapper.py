import unittest
from unittest.mock import patch

from db.mapping.input.RawImageMapper import RawImageDTO, RawImageMapper


class TestRawImageDTO(unittest.TestCase):

    def setUp(self):
        self.valid_kwargs = {
            "image_data": b"fake-bytes",
            "name": "test.png",
            "format": "PNG",  # wird später lowercase
            "content_type": "image/png",
            "bucket": "test-bucket",
            "size": 1234,
            "compressed": False,
            "compression_method": None,
        }

    def test_valid_creation_and_format_normalization(self):
        dto = RawImageDTO(**self.valid_kwargs)
        self.assertEqual(dto.format, "png")

    def test_to_dict(self):
        dto = RawImageDTO(**self.valid_kwargs)
        d = dto.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["name"], "test.png")
        self.assertEqual(d["format"], "png")

    def test_not_null_fields(self):
        required = ["image_data", "name", "format", "bucket", "size", "content_type"]
        for field in required:
            with self.subTest(field=field):
                kwargs = self.valid_kwargs.copy()
                kwargs[field] = None
                with self.assertRaises(ValueError):
                    RawImageDTO(**kwargs)

    def test_type_validation(self):
        # image_data must be bytes
        kw = self.valid_kwargs.copy()
        kw["image_data"] = "not-bytes"
        with self.assertRaises(TypeError):
            RawImageDTO(**kw)

        # size must be int
        kw = self.valid_kwargs.copy()
        kw["size"] = "1234"
        with self.assertRaises(TypeError):
            RawImageDTO(**kw)

        # compressed must be bool
        kw = self.valid_kwargs.copy()
        kw["compressed"] = "false"
        with self.assertRaises(TypeError):
            RawImageDTO(**kw)

        # compression_method must be str or None
        kw = self.valid_kwargs.copy()
        kw["compression_method"] = 123
        with self.assertRaises(TypeError):
            RawImageDTO(**kw)


class TestRawImageMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = RawImageMapper()
        self.base_kwargs = {
            "image_data": b"imgbytes",
            "name": "image",
            "bucket": "bucket",
        }

    @patch("db.mapping.RawImageMapper.MapperHelper.get_bytes_length")
    @patch("db.mapping.RawImageMapper.MapperHelper.guess_content_type")
    @patch("db.mapping.RawImageMapper.MapperHelper.guess_file_extension")
    def test_map_image_uses_mapperhelper(
        self,
        mock_guess_ext,
        mock_guess_type,
        mock_get_len,
    ):
        mock_guess_ext.return_value = "jpg"
        mock_guess_type.return_value = "image/jpeg"
        mock_get_len.return_value = 999

        dto = self.mapper.map_image(**self.base_kwargs)

        mock_guess_ext.assert_called_once_with(b"imgbytes")
        mock_guess_type.assert_called_once_with(b"imgbytes")
        mock_get_len.assert_called_once_with(b"imgbytes")

        self.assertEqual(dto.format, "jpg")
        self.assertEqual(dto.content_type, "image/jpeg")
        self.assertEqual(dto.size, 999)

    @patch("db.mapping.RawImageMapper.MapperHelper.get_bytes_length")
    @patch("db.mapping.RawImageMapper.MapperHelper.guess_content_type")
    @patch("db.mapping.RawImageMapper.MapperHelper.guess_file_extension")
    def test_map_image_uses_explicit_values(
        self,
        mock_guess_ext,
        mock_guess_type,
        mock_get_len,
    ):
        dto = self.mapper.map_image(
            **self.base_kwargs,
            format="png",
            content_type="image/png",
            size=123,
            compressed=True,
            compression_method="lz4",
        )

        mock_guess_ext.assert_not_called()
        mock_guess_type.assert_not_called()
        mock_get_len.assert_not_called()

        self.assertEqual(dto.format, "png")
        self.assertEqual(dto.content_type, "image/png")
        self.assertEqual(dto.size, 123)
        self.assertTrue(dto.compressed)
        self.assertEqual(dto.compression_method, "lz4")


if __name__ == "__main__":
    unittest.main()
