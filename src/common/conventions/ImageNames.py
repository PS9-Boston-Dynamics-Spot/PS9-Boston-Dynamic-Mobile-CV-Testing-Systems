import uuid
import json


class ImageNames:
    @staticmethod
    def from_dict(data: dict) -> str:
        """Deterministische UUID aus DTO-Dict erzeugen."""
        json_str = json.dumps(data, sort_keys=True)
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, json_str))
