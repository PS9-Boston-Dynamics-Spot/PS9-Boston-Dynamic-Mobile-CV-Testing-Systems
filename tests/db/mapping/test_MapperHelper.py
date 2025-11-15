import unittest
from unittest.mock import patch

from db.mapping.MapperHelper import MapperHelper


class TestMapperHelperGetBytesLength(unittest.TestCase):
    def test_get_bytes_length_returns_correct_length(self):
        payload = b"123456"
        result = MapperHelper.get_bytes_length(payload)
        self.assertEqual(result, 6)

    def test_get_bytes_length_empty_bytes(self):
        payload = b""
        result = MapperHelper.get_bytes_length(payload)
        self.assertEqual(result, 0)


class TestMapperHelperGuessContentType(unittest.TestCase):

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_content_type_jpeg(self, mock_what):
        mock_what.return_value = "jpeg"
        result = MapperHelper.guess_content_type(b"fake-bytes")
        self.assertEqual(result, "image/jpeg")
        mock_what.assert_called_once()

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_content_type_jpg(self, mock_what):
        mock_what.return_value = "jpg"
        result = MapperHelper.guess_content_type(b"fake-bytes")
        self.assertEqual(result, "image/jpeg")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_content_type_png(self, mock_what):
        mock_what.return_value = "png"
        result = MapperHelper.guess_content_type(b"fake-bytes")
        self.assertEqual(result, "image/png")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_content_type_bmp(self, mock_what):
        mock_what.return_value = "bmp"
        result = MapperHelper.guess_content_type(b"fake-bytes")
        self.assertEqual(result, "image/bmp")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_content_type_tiff(self, mock_what):
        mock_what.return_value = "tiff"
        result = MapperHelper.guess_content_type(b"fake-bytes")
        self.assertEqual(result, "image/tiff")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_content_type_unknown_type(self, mock_what):
        mock_what.return_value = "gif"
        result = MapperHelper.guess_content_type(b"fake-bytes")
        self.assertEqual(result, "application/octet-stream")

    def test_guess_content_type_empty_bytes(self):
        # imghdr.what wird hier gar nicht aufgerufen, weil image_data leer ist
        result = MapperHelper.guess_content_type(b"")
        self.assertEqual(result, "application/octet-stream")


class TestMapperHelperGuessFileExtension(unittest.TestCase):

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_file_extension_jpeg(self, mock_what):
        mock_what.return_value = "jpeg"
        result = MapperHelper.guess_file_extension(b"fake-bytes")
        self.assertEqual(result, "jpg")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_file_extension_jpg(self, mock_what):
        mock_what.return_value = "jpg"
        result = MapperHelper.guess_file_extension(b"fake-bytes")
        self.assertEqual(result, "jpg")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_file_extension_png(self, mock_what):
        mock_what.return_value = "png"
        result = MapperHelper.guess_file_extension(b"fake-bytes")
        self.assertEqual(result, "png")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_file_extension_bmp(self, mock_what):
        mock_what.return_value = "bmp"
        result = MapperHelper.guess_file_extension(b"fake-bytes")
        self.assertEqual(result, "bmp")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_file_extension_tiff(self, mock_what):
        mock_what.return_value = "tiff"
        result = MapperHelper.guess_file_extension(b"fake-bytes")
        self.assertEqual(result, "tiff")

    @patch("db.mapping.MapperHelper.imghdr.what")
    def test_guess_file_extension_unknown_type(self, mock_what):
        mock_what.return_value = "gif"
        result = MapperHelper.guess_file_extension(b"fake-bytes")
        self.assertEqual(result, "bin")

    def test_guess_file_extension_empty_bytes(self):
        result = MapperHelper.guess_file_extension(b"")
        self.assertEqual(result, "bin")


if __name__ == "__main__":
    unittest.main()
