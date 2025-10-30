from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import imghdr


@dataclass
class RawImageDTO:

    image_data: bytes
    name: str
    format: str
    content_type: str
    bucket: str
    size: int
    compressed: bool = False
    compression_method: Optional[str] = None

    def __post_init__(self):
        not_null_fields = [
            "image_data",
            "name",
            "format",
            "bucket",
            "size",
            "content_type",
        ]

        for field_name in not_null_fields:
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Field '{field_name}' must not be None")

        if not isinstance(self.image_data, bytes):
            raise TypeError("'image_data' must be bytes")

        if not isinstance(self.format, str):
            raise TypeError("'format' must be a string")

        if not isinstance(self.bucket, str):
            raise TypeError("'bucket' must be a string")

        if not isinstance(self.size, int):
            raise TypeError("'size' must be an integer")

        if not isinstance(self.content_type, str):
            raise TypeError("'content_type' must be a string")

        self.format = self.format.lower()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d


class RawImageMapper:

    def map_image(
        self,
        image_data: bytes,
        name: str,
        bucket: str,
        format: Optional[str] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        compressed: bool = False,
        compression_method: Optional[str] = None,
    ) -> RawImageDTO:

        format = format or self.guess_file_extension(image_data)
        content_type = content_type or self.guess_content_type(image_data)
        size = size or self.get_bytes_length(image_data)

        dto = RawImageDTO(
            image_data=image_data,
            name=name,
            format=format,
            bucket=bucket,
            size=size,
            compressed=compressed,
            compression_method=compression_method,
            content_type=content_type,
        )

        return dto

    @staticmethod
    def get_bytes_length(payload: bytes) -> int:
        return len(payload)

    @staticmethod
    def guess_content_type(image_data: bytes) -> str:
        if image_data:
            detected = imghdr.what(None, h=image_data)
            if detected in {"jpeg", "jpg"}:
                return "image/jpeg"
            elif detected == "png":
                return "image/png"
            elif detected == "bmp":
                return "image/bmp"
            elif detected == "tiff":
                return "image/tiff"
            else:
                return "application/octet-stream"

        return "application/octet-stream"

    @staticmethod
    def guess_file_extension(image_data: bytes) -> str:
        if image_data:
            detected = imghdr.what(None, h=image_data)
            if detected in {"jpeg", "jpg"}:
                return "jpg"
            elif detected == "png":
                return "png"
            elif detected == "bmp":
                return "bmp"
            elif detected == "tiff":
                return "tiff"
            else:
                return "bin"

        return "bin"
