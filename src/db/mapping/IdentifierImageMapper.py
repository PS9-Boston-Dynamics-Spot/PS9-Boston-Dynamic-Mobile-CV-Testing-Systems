from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class IdentifierImageDTO:

    image_data: bytes
    id: int
    name: str
    format: str
    content_type: str
    bucket: str
    size: int
    compressed: int
    compression_method: Optional[str] = None
    created_at: str

    def __post_init__(self):

        not_null_fields = [
            "id",
            "image_data",
            "name",
            "format",
            "content_type",
            "bucket",
            "size",
            "compressed",
            "created_at",
        ]

        for field_name in not_null_fields:
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Field '{field_name}' must not be None")

        if not isinstance(self.image_data, bytes):
            raise TypeError("'image_data' must be bytes")

        if not isinstance(self.id, int):
            raise TypeError("'id' must be an integer")

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

        if not isinstance(self.compressed, int):
            raise TypeError("'compressed' must be a boolean")

        if (
            not isinstance(self.compression_method, str)
            and self.compression_method is not None
        ):
            raise TypeError("'compression_method' must be a string")

        if not isinstance(self.created_at, str):
            raise TypeError("'created_at' must be a string")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class IdentifierImageMapper:

    def map_image(
        self,
        image_data: bytes,
        id: int,
        name: str,
        bucket: str,
        created_at: str,
        format: str,
        content_type: str,
        size: int,
        compressed: int,
        compression_method: Optional[str] = None,
    ) -> IdentifierImageDTO:

        dto = IdentifierImageDTO(
            image_data=image_data,
            id=id,
            name=name,
            format=format,
            bucket=bucket,
            size=size,
            compressed=compressed,
            compression_method=compression_method,
            content_type=content_type,
            created_at=created_at,
        )

        return dto
