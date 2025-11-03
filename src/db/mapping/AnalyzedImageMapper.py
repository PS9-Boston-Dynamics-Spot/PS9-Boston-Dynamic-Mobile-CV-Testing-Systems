from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
from db.mapping.MapperHelper import MapperHelper


@dataclass
class AnalyzedImageDTO:

    image_data: bytes
    raw_image_id: int
    name: str
    format: str
    content_type: str
    bucket: str
    size: int
    sensor_type: str
    category: str
    quality: float
    value: float
    unit: str
    compressed: bool = False
    compression_method: Optional[str] = None

    def __post_init__(self):
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
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Field '{field_name}' must not be None")

        if not isinstance(self.image_data, bytes):
            raise TypeError("'image_data' must be bytes")

        if not isinstance(self.raw_image_id, int):
            raise TypeError("'raw_image_id' must be an integer")

        if not isinstance(self.name, str):
            raise TypeError("'name' must be a string")

        if not isinstance(self.format, str):
            raise TypeError("'format' must be a string")

        if not isinstance(self.bucket, str):
            raise TypeError("'bucket' must be a string")

        if not isinstance(self.size, int):
            raise TypeError("'size' must be an integer")

        if not isinstance(self.content_type, str):
            raise TypeError("'content_type' must be a string")

        if not isinstance(self.compressed, bool):
            raise TypeError("'compressed' must be a boolean")

        if (
            not isinstance(self.compression_method, str)
            and self.compression_method is not None
        ):
            raise TypeError("'compression_method' must be a string")

        if not isinstance(self.sensor_type, str):
            raise TypeError("'sensor_type' must be a string")

        if not isinstance(self.category, str):
            raise TypeError("'category' must be a string")

        if not isinstance(self.quality, float):
            raise TypeError("'quality' must be a float")

        if not isinstance(self.value, float):
            raise TypeError("'value' must be a float")

        if not isinstance(self.unit, str):
            raise TypeError("'unit' must be a string")

        self.format = self.format.lower()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class AnalyzedImageMapper:

    def map_image(
        self,
        image_data: bytes,
        raw_image_id: int,
        name: str,
        bucket: str,
        sensor_type: str,
        category: str,
        quality: float,
        value: float,
        unit: str,
        format: Optional[str] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        compressed: bool = False,
        compression_method: Optional[str] = None,
    ) -> AnalyzedImageDTO:

        format = format or MapperHelper.guess_file_extension(image_data)
        content_type = content_type or MapperHelper.guess_content_type(image_data)
        size = size or MapperHelper.get_bytes_length(image_data)

        dto = AnalyzedImageDTO(
            image_data=image_data,
            raw_image_id=raw_image_id,
            name=name,
            format=format,
            bucket=bucket,
            size=size,
            compressed=compressed,
            compression_method=compression_method,
            content_type=content_type,
            sensor_type=sensor_type,
            category=category,
            quality=quality,
            value=value,
            unit=unit,
        )

        return dto
