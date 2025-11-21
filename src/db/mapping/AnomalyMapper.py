from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class AnomalyDTO:

    analyzed_image_id: int
    detected_value: float
    comparative_value: float
    is_anomaly: bool
    node_id: str

    def __post_init__(self):
        not_null_fields = [
            "analyzed_image_id",
            "detected_value",
            "comparative_value",
            "node_id",
        ]

        for field_name in not_null_fields:
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Field '{field_name}' must not be None")

        if not isinstance(self.analyzed_image_id, int):
            raise TypeError("'analyzed_image_id' must be an integer")

        if not isinstance(self.detected_value, float):
            raise TypeError("'detected_value' must be a float")

        if not isinstance(self.comparative_value, float):
            raise TypeError("'comparative_value' must be a float")

        if not isinstance(self.is_anomaly, bool):
            raise TypeError("'is_anomaly' must be a boolean")

        if not isinstance(self.node_id, str):
            raise TypeError("'node_id' must be a string")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class AnomalyMapper:

    def map_anomaly(
        self,
        analyzed_image_id: int,
        detected_value: float,
        comparative_value: float,
        is_anomaly: bool,
        node_id: str,
    ) -> AnomalyDTO:

        dto = AnomalyDTO(
            analyzed_image_id=analyzed_image_id,
            detected_value=detected_value,
            comparative_value=comparative_value,
            is_anomaly=is_anomaly,
            node_id=node_id,
        )

        return dto
