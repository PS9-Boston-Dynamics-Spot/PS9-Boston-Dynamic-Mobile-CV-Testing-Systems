from dataclasses import dataclass, asdict
from common.imports.Typing import Any, Dict
import json


@dataclass
class AnomalyDTO:

    analyzed_image_id: int
    parameters: str
    is_anomaly: bool
    anomaly_score: float
    used_funtion: str

    def __post_init__(self):
        not_null_fields = [
            "analyzed_image_id",
            "is_anomaly",
            "anomaly_score",
        ]

        for field_name in not_null_fields:
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Field '{field_name}' must not be None")

        if not isinstance(self.analyzed_image_id, int):
            raise TypeError("'analyzed_image_id' must be an integer")

        if not isinstance(self.is_anomaly, bool):
            raise TypeError("'is_anomaly' must be a boolean")

        if not isinstance(self.anomaly_score, float):
            raise TypeError("'anomaly_score' must be a float")

        if not isinstance(self.parameters, str):
            raise TypeError("'parameters' must be a str")

        if not isinstance(self.used_funtion, str):
            raise TypeError("'used_funtion' must be a str")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class AnomalyMapper:

    @staticmethod
    def map_anomaly(
        analyzed_image_id: int,
        is_anomaly: bool,
        anomaly_score: float,
        used_funtion: str,
        **parameters,
    ) -> AnomalyDTO:

        parameters_json = json.dumps(parameters)

        dto = AnomalyDTO(
            analyzed_image_id=analyzed_image_id,
            parameters=parameters_json,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            used_funtion=used_funtion,
        )

        return dto
