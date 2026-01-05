from credentials.manager.SettingsManager import SettingsManager
from common.imports.Typing import Tuple, Optional


class AnomalyChecker:
    def __init__(self):
        self._settings_manager = SettingsManager()

    def is_anomaly(
        self,
        value_to_check: float,
        category_name: str,
        aruco_id: Optional[int] = None,
    ) -> Tuple[float, bool]:
        score_function = self._settings_manager.getScoreFunction(
            aruco_id=aruco_id, category_name=category_name
        )
        safe_range = self._settings_manager.getSafeRange(
            aruco_id=aruco_id, category_name=category_name
        )
        uncertain_range = self._settings_manager.getUncertainRange(
            aruco_id=aruco_id, category_name=category_name
        )
        anomaly_range = self._settings_manager.getAnomalyRange(
            aruco_id=aruco_id, category_name=category_name
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
