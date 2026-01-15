from dataclasses import dataclass, field
from common.imports.Typing import Optional, Tuple, Generator
from db.mapping.input.RawImageMapper import RawImageMapper
from db.mapping.input.AnalyzedImageMapper import AnalyzedImageMapper
from db.mapping.input.AnomalyMapper import AnomalyMapper
from credentials.manager.SettingsManager import SettingsManager
from anomaly.AnomalyChecker import AnomalyChecker
from cvision.analog.AnalogGaugeReader import AnalogGaugeReader
from cvision.analog.AnalogGaugeCropper import AnalogGaugeCropper
from cvision.aruco.ArUcoIDExtractor import ArUcoIDExtraktor
from db.dal.DataAccessLayer import DataAccessLayer
from cvision.digital.DigitalCropper import YoloDisplayCropper
from cvision.digital.DigitalValueReader import EasyOcrDisplayValueReader


@dataclass
class Initializer:

    raw_image_mapper: RawImageMapper = field(default_factory=RawImageMapper)
    analyzed_image_mapper: AnalyzedImageMapper = field(
        default_factory=AnalyzedImageMapper
    )
    anomaly_mapper: AnomalyMapper = field(default_factory=AnomalyMapper)
    settings_manager: SettingsManager = field(default_factory=SettingsManager)
    aruco_extractor: ArUcoIDExtraktor = field(default_factory=ArUcoIDExtraktor)
    anomaly_checker: AnomalyChecker = field(default_factory=AnomalyChecker)
    analog_gauge_cropper: AnalogGaugeCropper = field(default_factory=AnalogGaugeCropper)
    digital_sensor_cropper: YoloDisplayCropper = field(
        default_factory=YoloDisplayCropper
    )


initializer = Initializer()
services = initializer


def safe_analyzed_image(
    dal: DataAccessLayer,
    image_bytes: bytes,
    raw_image_id: int,
    sensor_type: str,
    opcua_node_id: str,
    aruco_id: int,
    detected_value: float,
    unit: str,
    category: str,
) -> int:

    dto_analyzed_image = services.analyzed_image_mapper.map_image(
        image_data=image_bytes,
        raw_image_id=raw_image_id,
        sensor_type=sensor_type,
        opcua_node_id=opcua_node_id,
        aruco_id=aruco_id,
        value=detected_value,
        unit=unit,
        category=category,
    )
    analyzed_image_id = dal.insert_analyzed_image(
        anaylzed_image_with_metadata=dto_analyzed_image
    )

    return analyzed_image_id


def process_analog_image(
    dal: DataAccessLayer,
    image_bytes: bytes,
    raw_image_id: int,
    opcua_node_id: str,
    aruco_id: Optional[int] = None,
    category_name: Optional[str] = "pressure",
) -> Tuple[int, float]:

    cropped_analog_gauge_image = services.analog_gauge_cropper.process(img=image_bytes)
    analog_unit = services.settings_manager.getUnit(
        aruco_id=aruco_id, category_name=category_name
    )

    value_tolerance = services.settings_manager.getValueTolerance(
        aruco_id=aruco_id, category_name=category_name
    )
    real_value = 0.13  # dal.get_value_from_opcua_node(opcua_node_id=opcua_node_id)
    lower_bound = real_value * (1 - value_tolerance)
    upper_bound = real_value * (1 + value_tolerance)

    with AnalogGaugeReader(
        img=cropped_analog_gauge_image, category=category_name
    ) as analog_gauge_reader:
        center_x, center_y, radius = analog_gauge_reader.calibrate()
        detected_value = analog_gauge_reader.get_current_value(
            x=center_x, y=center_y, r=radius
        )

        if detected_value == -1:
            print("Debug: no value detected, using fallback value:", real_value)
            detected_value = real_value

        if not (lower_bound <= detected_value <= upper_bound):
            print(
                "Debug: detected value is out of tolerance range, using real value",
                detected_value,
                real_value,
            )
            detected_value = real_value

        analyzed_image_id = safe_analyzed_image(
            dal=dal,
            image_bytes=cropped_analog_gauge_image,
            raw_image_id=raw_image_id,
            sensor_type="analog",
            opcua_node_id=opcua_node_id,
            aruco_id=aruco_id,
            detected_value=detected_value,
            unit=analog_unit,
            category=category_name,
        )

        for idx, img_bytes in enumerate(analog_gauge_reader.get_images_log()):

            analyzed_image_id = safe_analyzed_image(
                dal=dal,
                image_bytes=img_bytes,
                raw_image_id=raw_image_id,
                sensor_type="analog",
                opcua_node_id=opcua_node_id,
                aruco_id=aruco_id,
                detected_value=detected_value,
                unit=analog_unit,
                category=category_name,
            )

    return analyzed_image_id, detected_value


def check_anomaly(
    dal: DataAccessLayer,
    analyzed_image_id: int,
    detected_value: float,
    category_name: str,
    aruco_id: Optional[int] = None,
) -> bool:

    anomaly_score, is_anomaly = services.anomaly_checker.is_anomaly(
        value_to_check=detected_value, aruco_id=aruco_id, category_name=category_name
    )
    print(anomaly_score, is_anomaly)

    parameters = services.settings_manager.getParametersForAnomalyMapper(
        aruco_id=aruco_id, category_name=category_name
    )

    score_function_str = services.settings_manager.getScoreFunctionStr(
        aruco_id=aruco_id, category_name=category_name
    )

    anomaly_dto = services.anomaly_mapper.map_anomaly(
        analyzed_image_id=analyzed_image_id,
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score,
        used_funtion=score_function_str,
        **parameters,
    )

    dal.insert_anomaly(anomaly_with_metadata=anomaly_dto)

    return is_anomaly


def handle_anomaly(is_anomaly: bool) -> None:
    if is_anomaly:
        print("❗Anomaly detected❗")
        # TODO: send alarm???
    else:
        print("✅No anomaly detected✅")
        # TODO: continue to next machine)


def process_digital_image(
    dal: DataAccessLayer,
    image_bytes: bytes,
    raw_image_id: int,
    opcua_node_id: str,
    aruco_id: Optional[int] = None,
) -> Generator[int, float, str]:
    reader = EasyOcrDisplayValueReader(languages=["en", "de"], gpu=False, verbose=True)

    cropped_digital_images = services.digital_sensor_cropper.crop_from_bytes(
        raw_image_bytes=image_bytes
    )

    for cropped_digital_image in cropped_digital_images:

        result = reader.read_from_crop_bytes(
            crop_jpg_bytes=cropped_digital_image.crop_bytes
        )

        # Select value and unit based on display_type, fallback to config unit if OCR unit is None
        config_unit = services.settings_manager.getUnit(
            aruco_id=aruco_id, category_name=result.display_type
        )
        if result.display_type == "tempdisplay":
            detected_value = result.temperature
            unit = result.temperature_unit or config_unit
            ocr_confidence = result.ocr_confidence_temp

        # Always print debug info
        print("[MAIN] RESULT")
        print(" display_type:", result.display_type)
        print(" temperature value:", result.temperature)
        print(" temperature unit:", result.temperature_unit or config_unit)
        print(" temperature ocr_confidence:", result.ocr_confidence_temp)
        print(" humidity value:", result.humidity)
        print(" humidity unit:", result.humidity_unit or config_unit)
        print(" humidity ocr_confidence:", result.ocr_confidence_hum)
        print(" ofen value:", result.ofen_value)
        print(" ofen unit:", result.ofen_unit or config_unit)
        print(" ofen ocr_confidence:", result.ocr_confidence_ofen)
        print(" title_text:", result.title_text)
        print(" title_raw:", result.title_raw)
        print(" raw_text_temp:", result.raw_text_temp)
        print(" raw_text_hum:", result.raw_text_hum)
        print(" raw_text_ofen:", result.raw_text_ofen)

        # For tempdisplay, yield both temperature and humidity as separate results
        if result.display_type == "tempdisplay":
            # Temperature
            if result.temperature is not None:
                analyzed_image_id = safe_analyzed_image(
                    dal=dal,
                    image_bytes=cropped_digital_image.crop_bytes,
                    raw_image_id=raw_image_id,
                    sensor_type="tempdisplay",
                    opcua_node_id=opcua_node_id,
                    aruco_id=aruco_id,
                    detected_value=result.temperature,
                    unit=result.temperature_unit or config_unit,
                    category="tempdisplay",
                )
                yield analyzed_image_id, result.temperature, "tempdisplay"
            # Humidity
            if result.humidity is not None:
                analyzed_image_id = safe_analyzed_image(
                    dal=dal,
                    image_bytes=cropped_digital_image.crop_bytes,
                    raw_image_id=raw_image_id,
                    sensor_type="humidity",
                    opcua_node_id=opcua_node_id,
                    aruco_id=aruco_id,
                    detected_value=result.humidity,
                    unit=result.humidity_unit or "%",
                    category="humidity",
                )
                yield analyzed_image_id, result.humidity, "humidity"
        elif result.display_type == "ofen":
            if result.ofen_value is not None:
                analyzed_image_id = safe_analyzed_image(
                    dal=dal,
                    image_bytes=cropped_digital_image.crop_bytes,
                    raw_image_id=raw_image_id,
                    sensor_type="ofen",
                    opcua_node_id=opcua_node_id,
                    aruco_id=aruco_id,
                    detected_value=result.ofen_value,
                    unit=result.ofen_unit or config_unit,
                    category="ofen",
                )
                yield analyzed_image_id, result.ofen_value, "ofen"
        else:
            # fallback: yield whatever was detected
            if result.temperature is not None:
                analyzed_image_id = safe_analyzed_image(
                    dal=dal,
                    image_bytes=cropped_digital_image.crop_bytes,
                    raw_image_id=raw_image_id,
                    sensor_type=result.display_type,
                    opcua_node_id=opcua_node_id,
                    aruco_id=aruco_id,
                    detected_value=result.temperature,
                    unit=result.temperature_unit or config_unit,
                    category=result.display_type,
                )
                yield analyzed_image_id, result.temperature, result.display_type
