from dataclasses import dataclass, asdict
from common.imports.Typing import Any, Dict
from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager


@dataclass
class OPCUADTO:

    image_data: bytes

    def __post_init__(self):

        not_null_fields = [
            "image_data",
        ]

        self.format = self.format.lower()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class RawImageMapper:

    @staticmethod
    def map_image(

    ) -> OPCUADTO:

        

        dto = OPCUADTO(

        )

        return dto
