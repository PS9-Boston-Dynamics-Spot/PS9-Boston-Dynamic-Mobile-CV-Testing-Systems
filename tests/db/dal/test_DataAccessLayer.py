import unittest
from unittest.mock import patch

from db.dal.DataAccessLayer import DataAccessLayer
from db.dal.exceptions.DataAccessLayerError import DataAccessLayerError
from db.media.exceptions.MediaRepositoryError import MediaRepositoryError
from db.meta.exceptions.MetaRepositoryError import MetaRepositoryError
from db.mapping.RawImageMapper import RawImageDTO
from db.mapping.AnalyzedImageMapper import AnalyzedImageDTO


class TestDataAccessLayer(unittest.TestCase):

    # ---------- Hilfsdaten ----------

    def _raw_dto(self):
        image_data = b"\xff\xd8\xff\xdb"  # dummy jpeg header
        return RawImageDTO(
            bucket="raw-bucket",
            name="Mein Bild 1",
            format="jpg",
            image_data=image_data,
            content_type="image/jpeg",
            size=len(image_data),
        )

    def _analyzed_dto(self):
        image_data = b"\x89PNG\r\n"  # dummy png header
        return AnalyzedImageDTO(
            bucket="analyzed-bucket",
            name="Output XY",
            format="png",
            image_data=image_data,
            content_type="image/png",
            raw_image_id=1,
            size=len(image_data),
            sensor_type="camera",
            category="test-category",
            quality=1.0,
            value=42.0,
            unit="units",
        )

    # ---------- create_object_name ----------

    def test_create_object_name(self):
        dal = DataAccessLayer()
        got = dal.create_object_name(42, "Mein Bild 1", "jpg")
        self.assertEqual(got, "42_mein_bild_1.jpg")

    # ---------- insert_raw_image: Success ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_raw_image_success(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        media = MediaRepoMock.return_value

        meta.get_new_id_raw_images.return_value = 42
        meta.insert_raw_image_metadata.return_value = (42, "Mein Bild 1")

        dto = self._raw_dto()
        with DataAccessLayer() as dal:
            dal.insert_raw_image(dto)

        meta.get_new_id_raw_images.assert_called_once()
        meta.insert_raw_image_metadata.assert_called_once()
        media.put_media.assert_called_once()

    # ---------- insert_raw_image: Meta-Fehler ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_raw_image_meta_error(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        meta.get_new_id_raw_images.return_value = 1
        meta.insert_raw_image_metadata.side_effect = MetaRepositoryError("boom", 9999)

        dto = self._raw_dto()
        with self.assertRaises(DataAccessLayerError) as ctx:
            with DataAccessLayer() as dal:
                dal.insert_raw_image(dto)

        self.assertIn("1761502460", str(ctx.exception))

    # ---------- insert_raw_image: Media-Fehler ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_raw_image_media_error(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        media = MediaRepoMock.return_value

        meta.get_new_id_raw_images.return_value = 7
        meta.insert_raw_image_metadata.return_value = (7, "Foo")
        media.put_media.side_effect = MediaRepositoryError("write failed", 9999)

        dto = self._raw_dto()
        with self.assertRaises(DataAccessLayerError) as ctx:
            with DataAccessLayer() as dal:
                dal.insert_raw_image(dto)

        self.assertIn("1761502470", str(ctx.exception))

    # ---------- insert_raw_image: generischer Fehler ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_raw_image_generic_error(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        meta.get_new_id_raw_images.return_value = 9
        meta.insert_raw_image_metadata.side_effect = RuntimeError("unexpected")

        dto = self._raw_dto()
        with self.assertRaises(DataAccessLayerError) as ctx:
            with DataAccessLayer() as dal:
                dal.insert_raw_image(dto)

        self.assertIn("1761502480", str(ctx.exception))

    # ---------- insert_analyzed_image: Success ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_analyzed_image_success(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        media = MediaRepoMock.return_value

        meta.get_new_id_analyzed_images.return_value = 99
        meta.insert_analyzed_image_metadata.return_value = (99, "Output XY")

        dto = self._analyzed_dto()
        with DataAccessLayer() as dal:
            dal.insert_analyzed_image(dto)

        meta.get_new_id_analyzed_images.assert_called_once()
        meta.insert_analyzed_image_metadata.assert_called_once()
        media.put_media.assert_called_once()

    # ---------- insert_analyzed_image: Meta-Fehler ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_analyzed_image_meta_error(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        meta.get_new_id_analyzed_images.return_value = 1
        meta.insert_analyzed_image_metadata.side_effect = MetaRepositoryError(
            "meta fail", 9999
        )

        dto = self._analyzed_dto()
        with self.assertRaises(DataAccessLayerError) as ctx:
            with DataAccessLayer() as dal:
                dal.insert_analyzed_image(dto)

        self.assertIn("1761932730", str(ctx.exception))

    # ---------- insert_analyzed_image: Media-Fehler ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_analyzed_image_media_error(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        media = MediaRepoMock.return_value

        meta.get_new_id_analyzed_images.return_value = 5
        meta.insert_analyzed_image_metadata.return_value = (5, "Output XY")
        media.put_media.side_effect = MediaRepositoryError("media fail", 9999)

        dto = self._analyzed_dto()
        with self.assertRaises(DataAccessLayerError) as ctx:
            with DataAccessLayer() as dal:
                dal.insert_analyzed_image(dto)

        self.assertIn("1761932740", str(ctx.exception))

    # ---------- insert_analyzed_image: generischer Fehler ----------

    @patch("db.dal.DataAccessLayer.MediaRepository")
    @patch("db.dal.DataAccessLayer.MetaRepository")
    def test_insert_analyzed_image_generic_error(self, MetaRepoMock, MediaRepoMock):
        meta = MetaRepoMock.return_value
        meta.get_new_id_analyzed_images.return_value = 1
        meta.insert_analyzed_image_metadata.side_effect = ValueError("boom")

        dto = self._analyzed_dto()
        with self.assertRaises(DataAccessLayerError) as ctx:
            with DataAccessLayer() as dal:
                dal.insert_analyzed_image(dto)

        self.assertIn("1761932750", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
