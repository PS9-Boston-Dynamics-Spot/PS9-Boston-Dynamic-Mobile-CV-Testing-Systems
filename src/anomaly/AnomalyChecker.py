from credentials.manager.UnifiedCredentialsManager import UnifiedCredentialsManager
from common.typing.Typing import Tuple, Optional


class AnomalyChecker:
    def __init__(self):
        self._unified_credentials_manager = UnifiedCredentialsManager()

    def is_anomaly(
        self,
        value_to_check: float,
        aruco_id: Optional[int] = None,
        allow_missing: bool = False,
    ) -> Tuple[float, bool]:
        score_function = self._unified_credentials_manager.getScoreFunction(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        safe_range = self._unified_credentials_manager.getSafeRange(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        uncertain_range = self._unified_credentials_manager.getUncertainRange(
            aruco_id=aruco_id, allow_missing=allow_missing
        )
        anomaly_range = self._unified_credentials_manager.getAnomalyRange(
            aruco_id=aruco_id, allow_missing=allow_missing
        )

        score = score_function(value_to_check)

        if score >= safe_range:
            return score, False
        elif score >= uncertain_range and score < safe_range:
            return score, False
        elif score >= anomaly_range and score < uncertain_range:
            return score, True
        else:
            return score, True
