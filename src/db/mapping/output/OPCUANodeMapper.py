from dataclasses import dataclass, asdict
from common.imports.Typing import Any, Dict


@dataclass
class OPCUADTO:

    value: float

    def __post_init__(self):

        not_null_fields = [
            "value",
        ]

        if not isinstance(self.value, float):
            raise TypeError("'value' must be a float")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class OPCUANodeMapper:

    @staticmethod
    def map_image(
        value: float
    ) -> OPCUADTO:

        dto = OPCUADTO(
            value=value
        )

        return dto