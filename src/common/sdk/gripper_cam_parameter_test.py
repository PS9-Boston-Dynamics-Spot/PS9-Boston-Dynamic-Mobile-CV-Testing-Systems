import sys
import time

from google.protobuf import wrappers_pb2

# Importieren Sie die notwendigen Komponenten aus dem Boston Dynamics SDK
import bosdyn.client
import bosdyn.client.util
from bosdyn.api import gripper_camera_param_pb2, header_pb2
from bosdyn.client.gripper_camera_param import GripperCameraParamClient

# Annahme: Diese Funktion ist in Ihrem Projekt verfügbar
# from . import get_gripper_camera_params 

def set_high_res_auto_params(robot: bosdyn.client.robot.Robot):
    """
    Setzt die höchste Auflösung (4208x3120) und aktiviert alle Auto-Modi 
    (Auto-Exposure, Auto-Focus, Auto-White-Balance) für die Greiferkamera.

    Args:
        robot: Die bereits authentifizierte Roboter-Instanz.
    """
    print("--- Starte Greiferkamera-Setup: 4K (4208x3120) und AUTO-Modi ---")
    
    # 1. Client initialisieren
    try:
        gripper_camera_param_client = robot.ensure_client(
            GripperCameraParamClient.default_service_name
        )
    except Exception as e:
        print(f"Fehler beim Erstellen des GripperCameraParamClient: {e}")
        return False

    # 2. Parameter festlegen (Hardcoded für 4K und AUTO)
    
    # Höchste verfügbare Auflösung (4208x3120)
    camera_mode = gripper_camera_param_pb2.GripperCameraParams.MODE_4208_3120
    print(f"Setze Auflösung auf: 4208x3120")

    # Auto-Fokus aktivieren
    auto_focus = wrappers_pb2.BoolValue(value=True)
    print("Aktiviere Auto-Fokus")

    # Auto-Exposure (Belichtung) aktivieren
    auto_exposure = wrappers_pb2.BoolValue(value=True)
    print("Aktiviere Auto-Belichtung")

    # Auto-White-Balance (Weißabgleich) aktivieren
    white_balance_temperature_auto = wrappers_pb2.BoolValue(value=True)
    print("Aktiviere Auto-Weißabgleich")

    # HDR-Modus auf Auto setzen (optional, kann aber helfen)
    hdr = gripper_camera_param_pb2.HDR_AUTO
    print("Setze HDR-Modus auf Auto")
    
    # 3. Das GripperCameraParams-Objekt erstellen
    params = gripper_camera_param_pb2.GripperCameraParams(
        camera_mode=camera_mode,
        focus_auto=auto_focus,
        exposure_auto=auto_exposure,
        white_balance_temperature_auto=white_balance_temperature_auto,
        hdr=hdr
        # Andere nicht spezifizierte Parameter bleiben auf None und werden ignoriert
    )

    request = gripper_camera_param_pb2.GripperCameraParamRequest(params=params)
    
    # 4. Request senden
    try:
        response = gripper_camera_param_client.set_camera_params(request)
        print('Anforderung zum Setzen der Parameter gesendet.')

        if response.header.error and response.header.error.code != header_pb2.CommonError.CODE_OK:
            print('FEHLER beim Setzen der Parameter:')
            print(response.header.error)
            return False

        # 5. Aktualisierte Einstellungen vom Roboter abfragen (optional, zur Bestätigung)
        time.sleep(3) # Wartezeit, damit der Roboter die Einstellungen übernimmt
        print('Frage Roboter nach aktuellen Einstellungen ab...')

        get_request = gripper_camera_param_pb2.GripperCameraGetParamRequest()
        get_response = gripper_camera_param_client.get_camera_params(get_request)
        
        # Hier müssten Sie die Ausgabe der Parameter in Ihrem Stil implementieren.
        # Wenn Sie die Funktion `print_response_from_robot` aus dem Beispiel nutzen,
        # müssten Sie diese importieren oder hier implementieren.
        # print_response_from_robot(get_response) 
        
        print(f"Aktuelle Auflösung des Roboters: {get_response.params.camera_mode}")
        print("Setup abgeschlossen.")
        return True

    except Exception as e:
        print(f"Kritischer Fehler bei der Kommunikation mit dem Roboter: {e}")
        return False

# 6. Beispiel für die Nutzung (fügen Sie dies in Ihre Haupt-Roboter-Routine ein)
# def main_robot_routine(options):
#     # ... Authentifizierung und Roboter-Erstellung
#     # robot = sdk.create_robot(options.hostname)
#     # bosdyn.client.util.authenticate(robot)
# 
#     # set_high_res_auto_params(robot)
# 
#     # ... Starten Sie dann Ihre eigentliche Bildaufnahme-Routine