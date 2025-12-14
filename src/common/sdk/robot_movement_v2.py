import argparse

import os
import sys
import time
import datetime

from google.protobuf import wrappers_pb2

import bosdyn.client.util
from bosdyn.api import robot_state_pb2, image_pb2, gripper_camera_param_pb2, header_pb2
from bosdyn.api.graph_nav import graph_nav_pb2, map_pb2, nav_pb2
from bosdyn.client.exceptions import ResponseError
from bosdyn.client.frame_helpers import get_odom_tform_body
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive, ResourceAlreadyClaimedError
from bosdyn.client.power import PowerClient, power_on_motors, safe_power_off_motors
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.robot_state import RobotStateClient


from bosdyn.client.image import ImageClient, build_image_request
from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive
from bosdyn.client.docking import DockingClient
from bosdyn.client.gripper_camera_param import GripperCameraParamClient



from dotenv import load_dotenv
load_dotenv()


class RobotController:
    """Zentrale Verwaltung aller Robot-Clients und Power-/TimeSync-Handling."""

    def __init__(self, robot):
        self.robot = robot

        # Force trigger timesync
        self.robot.time_sync.wait_for_sync()

        # Clients erstellen
        self.power_client: PowerClient = robot.ensure_client(PowerClient.default_service_name)
        self.state_client: RobotStateClient = robot.ensure_client(RobotStateClient.default_service_name)
        self.command_client: RobotCommandClient = robot.ensure_client(RobotCommandClient.default_service_name)
        self.graph_nav_client: GraphNavClient = robot.ensure_client(GraphNavClient.default_service_name)
        self.lease_client: LeaseClient = robot.ensure_client(LeaseClient.default_service_name)
        self.estop_client: EstopClient = robot.ensure_client(EstopClient.default_service_name)
        
        self.image_client: ImageClient = robot.ensure_client(ImageClient.default_service_name)

        self.state_client: RobotStateClient = robot.ensure_client(RobotStateClient.default_service_name)

        self.dock_client: DockingClient = robot.ensure_client(DockingClient.default_service_name)

        self.gripper_camera_param_client: GripperCameraParamClient = robot.ensure_client(GripperCameraParamClient.default_service_name)

        # Power-State merken
        power_state = self.state_client.get_robot_state().power_state
        self._started_powered_on = (power_state.motor_power_state == power_state.STATE_ON)
        self._powered_on = self._started_powered_on

    #Not working        
    def dock(self, dock_id: int, timeout_sec: int = 60):

        """Führt einen vollständigen Docking-Vorgang an der angegebenen Dock-ID aus."""

        print(f"[Dock] Starte Docking-Vorgang zu Dock-ID {dock_id}...")

        # 1. Sicherstellen, dass Spot steht
        print("[Dock] Stelle sicher, dass der Roboter steht...")
        blocking_stand(self.command_client)

        # 2. Dock-Befehl senden
        print("[Dock] Sende Dock-Command...")
        self.dock_client.dock(dock_id)

        # 3. Auf Abschluss warten
        print("[Dock] Warte auf Docking-Abschluss...")
        result = self.dock_client.block_until_complete(timeout_sec=timeout_sec)

        print(f"[Dock] Docking abgeschlossen: {result}")
        return result

    def toggle_power(self, should_power_on):
        """Power the robot on/off dependent on the current power state."""
        is_powered_on = self.check_is_powered_on()
        if not is_powered_on and should_power_on:
            # Power on the robot up before navigating when it is in a powered-off state.
            power_on_motors(self.power_client)
            motors_on = False
            while not motors_on:
                future = self.state_client.get_robot_state_async()
                state_response = future.result(
                    timeout=10)  # 10 second timeout for waiting for the state response.
                if state_response.power_state.motor_power_state == robot_state_pb2.PowerState.STATE_ON:
                    motors_on = True
                else:
                    # Motors are not yet fully powered on.
                    time.sleep(.25)
        elif is_powered_on and not should_power_on:
            # Safe power off (robot will sit then power down) when it is in a
            # powered-on state.
            safe_power_off_motors(self.command_client, self.state_client)
        else:
            # Return the current power state without change.
            return is_powered_on
        # Update the locally stored power state.
        self.check_is_powered_on()
        return self._powered_on

    def check_is_powered_on(self):
        """Determine if the robot is powered on or off."""
        power_state = self.state_client.get_robot_state().power_state
        self._powered_on = (power_state.motor_power_state == power_state.STATE_ON)
        return self._powered_on

    def maybe_save_image(self, image, path):
        """Try to save image, if client has correct deps."""
        try:
            import io

            from PIL import Image
        except ImportError:
            print('Missing dependencies. Can\'t save image.')
            return

        # Format: YYYYMMDD_HHmmss (z.B. 20251201_172530)
        now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        name = 'spot-img-' + now_str + '.png'
        
        # Bestimme den vollständigen Pfad
        if path is not None and os.path.isdir(path):
            full_path = os.path.join(path, name)
            print(f'Saving image to specified directory: {full_path}')
        else:
            # Fallback auf das aktuelle Arbeitsverzeichnis (CWD), wenn kein oder ungültiger Pfad
            full_path = name
            print(f'Saving image to working directory as {full_path}')

        try:
            image = Image.open(io.BytesIO(image.data))
            image.save(full_path)
        except Exception as exc:
            
            print('Exception thrown saving image. %r', exc)

    
    def set_high_res_auto_params(self):
        """
        Setzt die höchste Auflösung (4208x3120) und aktiviert alle Auto-Modi 
        (Auto-Exposure, Auto-Focus, Auto-White-Balance) für die Greiferkamera.
        """
        print("--- Starte Greiferkamera-Setup: 4K (4208x3120) und AUTO-Modi ---")
        
        # 1. Client initialisieren
        try:
            gripper_camera_param_client = self.robot.ensure_client(
                GripperCameraParamClient.default_service_name
            )
        except Exception as e:
            print(f"Fehler beim Erstellen des GripperCameraParamClient: {e}")
            return False

        # 2. Parameter festlegen (Hardcoded für 4K und AUTO)
        camera_mode = gripper_camera_param_pb2.GripperCameraParams.MODE_4096_2160
        print(f"Setze Auflösung auf: 4096x2160")

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

        except Exception as e:
            print(f"Kritischer Fehler bei der Kommunikation mit dem Roboter bei Gripper Cam Paramater einstellung: {e}")
            return False

class EstopNoGui():
    """Provides a software estop without a GUI.

    To use this estop, create an instance of the EstopNoGui class and use the stop() and allow()
    functions programmatically.
    """

    def __init__(self, client, name=None):
        timeout_sec=5
        # Force server to set up a single endpoint system
        ep = EstopEndpoint(client, name, timeout_sec)
        ep.force_simple_setup()

        # Begin periodic check-in between keep-alive and robot
        self.estop_keep_alive = EstopKeepAlive(ep)

        # Release the estop
        self.estop_keep_alive.allow()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanly shut down estop on exit."""
        self.estop_keep_alive.end_periodic_check_in()

    def stop(self):
        self.estop_keep_alive.stop()

    def allow(self):
        self.estop_keep_alive.allow()

    def settle_then_cut(self):
        self.estop_keep_alive.settle_then_cut()

class GraphNavInterface(object):
    #-GNU
    def id_to_short_code(self, id):
        """Convert a unique id to a 2 letter short code."""
        tokens = id.split('-')
        if len(tokens) > 2:
            return f'{tokens[0][0]}{tokens[1][0]}'
        return None
    #-GNU
    def find_unique_waypoint_id(self, short_code, graph, name_to_id):
        """Convert either a 2 letter short code or an annotation name into the associated unique id."""
        if graph is None:
            print(
                'Please list the waypoints in the map before trying to navigate to a specific one (Option #4).'
            )
            return

        if len(short_code) != 2:
            # Not a short code, check if it is an annotation name (instead of the waypoint id).
            if short_code in name_to_id:
                # Short code is a waypoint's annotation name. Check if it is paired with a unique waypoint id.
                if name_to_id[short_code] is not None:
                    # Has an associated waypoint id!
                    return name_to_id[short_code]
                else:
                    print(
                        f'The waypoint name {short_code} is used for multiple different unique waypoints. Please use '
                        f'the waypoint id.')
                    return None
            # Also not a waypoint annotation name, so we will operate under the assumption that it is a
            # unique waypoint id.
            return short_code

        ret = short_code
        for waypoint in graph.waypoints:
            if short_code == self.id_to_short_code(waypoint.id):
                if ret != short_code:
                    return short_code  # Multiple waypoints with same short code.
                ret = waypoint.id
        return ret

    def __init__(self, robot_controller: RobotController, upload_path):
        self.use_gps=False

        self.rc = robot_controller
        self._robot = robot_controller.robot

        # Store the most recent knowledge of the state of the robot based on rpc calls.
        self._current_graph = None
        self._current_edges = dict()  #maps to_waypoint to list(from_waypoint)
        self._current_waypoint_snapshots = dict()  # maps id to waypoint snapshot
        self._current_edge_snapshots = dict()  # maps id to edge snapshot
        self._current_annotation_name_to_wp_id = dict()

        # Filepath for uploading a saved graph's and snapshots too.
        if upload_path[-1] == '/':
            self._upload_filepath = upload_path[:-1]
        else:
            self._upload_filepath = upload_path

        try:
            self._upload_graph_and_snapshots()
        except Exception as e:
            print(f"Fehler beim Hochladen des Graphen: {e}")
            raise

    def _get_localization_state(self, *args):
        """Get the current localization and state of the robot."""
        state = self.rc.graph_nav_client.get_localization_state(request_gps_state=self.use_gps)
        print(f'Got localization: \n{state.localization}')
        odom_tform_body = get_odom_tform_body(state.robot_kinematics.transforms_snapshot)
        print(f'Got robot state in kinematic odometry frame: \n{odom_tform_body}')
        if self.use_gps:
            print(f'GPS info:\n{state.gps}')

    def _set_initial_localization_fiducial(self, *args):
        """Trigger localization when near a fiducial."""
        robot_state = self.rc.state_client.get_robot_state()
        current_odom_tform_body = get_odom_tform_body(
            robot_state.kinematic_state.transforms_snapshot).to_proto()
        # Create an empty instance for initial localization since we are asking it to localize
        # based on the nearest fiducial.
        localization = nav_pb2.Localization()
        self.rc.graph_nav_client.set_localization(initial_guess_localization=localization,
                                                ko_tform_body=current_odom_tform_body)

    def _clear_graph_and_cache(self, *args):
        """Clear the state of the map on the robot, removing all waypoints and edges. Also clears the disk cache."""
        return self.rc.graph_nav_client.clear_graph_and_cache()
    #
    def _upload_graph_and_snapshots(self, *args):
        """Upload the graph and snapshots to the robot."""
        print('Loading the graph from disk into local storage...')
        with open(self._upload_filepath + '/graph', 'rb') as graph_file:
            # Load the graph from disk.
            data = graph_file.read()
            self._current_graph = map_pb2.Graph()
            self._current_graph.ParseFromString(data)
            print(
                f'Loaded graph has {len(self._current_graph.waypoints)} waypoints and {len(self._current_graph.edges)} edges'
            )
        for waypoint in self._current_graph.waypoints:
            # Load the waypoint snapshots from disk.
            with open(f'{self._upload_filepath}/waypoint_snapshots/{waypoint.snapshot_id}',
                      'rb') as snapshot_file:
                waypoint_snapshot = map_pb2.WaypointSnapshot()
                waypoint_snapshot.ParseFromString(snapshot_file.read())
                self._current_waypoint_snapshots[waypoint_snapshot.id] = waypoint_snapshot
        for edge in self._current_graph.edges:
            if len(edge.snapshot_id) == 0:
                continue
            # Load the edge snapshots from disk.
            with open(f'{self._upload_filepath}/edge_snapshots/{edge.snapshot_id}',
                      'rb') as snapshot_file:
                edge_snapshot = map_pb2.EdgeSnapshot()
                edge_snapshot.ParseFromString(snapshot_file.read())
                self._current_edge_snapshots[edge_snapshot.id] = edge_snapshot
        # Upload the graph to the robot.
        print('Uploading the graph and snapshots to the robot...')
        true_if_empty = not len(self._current_graph.anchoring.anchors)
        response = self.rc.graph_nav_client.upload_graph(graph=self._current_graph,
                                                       generate_new_anchoring=true_if_empty)
        # Upload the snapshots to the robot.
        for snapshot_id in response.unknown_waypoint_snapshot_ids:
            waypoint_snapshot = self._current_waypoint_snapshots[snapshot_id]
            self.rc.graph_nav_client.upload_waypoint_snapshot(waypoint_snapshot)
            print(f'Uploaded {waypoint_snapshot.id}')
        for snapshot_id in response.unknown_edge_snapshot_ids:
            edge_snapshot = self._current_edge_snapshots[snapshot_id]
            self.rc.graph_nav_client.upload_edge_snapshot(edge_snapshot)
            print(f'Uploaded {edge_snapshot.id}')

        # The upload is complete! Check that the robot is localized to the graph,
        # and if it is not, prompt the user to localize the robot before attempting
        # any navigation commands.
        localization_state = self.rc.graph_nav_client.get_localization_state()
        if not localization_state.localization.waypoint_id:
            # The robot is not localized to the newly uploaded graph.
            print('\n')
            print(
                'Upload complete! The robot is currently not localized to the map; please localize'
                ' the robot using commands (2) or (3) before attempting a navigation command.')
    #
    def _navigate_to(self, *args):
        """Navigate to a specific waypoint."""
        # Take the first argument as the destination waypoint.
        if len(args) < 1:
            # If no waypoint id is given as input, then return without requesting navigation.
            print('No waypoint provided as a destination for navigate to.')
            return

        destination_waypoint = self.find_unique_waypoint_id(
            args[0][0], self._current_graph, self._current_annotation_name_to_wp_id)
        if not destination_waypoint:
            # Failed to find the appropriate unique waypoint id for the navigation command.
            return
        if not self.rc.toggle_power(should_power_on=True):
            print('Failed to power on the robot, and cannot complete navigate to request.')
            return

        nav_to_cmd_id = None
        # Navigate to the destination waypoint.
        is_finished = False
        while not is_finished:
            # Issue the navigation command about twice a second such that it is easy to terminate the
            # navigation command (with estop or killing the program).
            try:
                nav_to_cmd_id = self.rc.graph_nav_client.navigate_to(destination_waypoint, 1.0,
                                                                   command_id=nav_to_cmd_id)
            except ResponseError as e:
                print(f'Error while navigating {e}')
                break
            time.sleep(.5)  # Sleep for half a second to allow for command execution.
            # Poll the robot for feedback to determine if the navigation command is complete. Then sit
            # the robot down once it is finished.
            is_finished = self._check_success(nav_to_cmd_id)

        # # Power off the robot if appropriate.
        # if self.rc._powered_on and not self.rc._started_powered_on:
        #     #self.rc.toggle_power(should_power_on=False)
        #     print("Lege hin") 
        
        return is_finished
    #-
    def _match_edge(self, current_edges, waypoint1, waypoint2):
        """Find an edge in the graph that is between two waypoint ids."""
        # Return the correct edge id as soon as it's found.
        for edge_to_id in current_edges:
            for edge_from_id in current_edges[edge_to_id]:
                if (waypoint1 == edge_to_id) and (waypoint2 == edge_from_id):
                    # This edge matches the pair of waypoints! Add it the edge list and continue.
                    return map_pb2.Edge.Id(from_waypoint=waypoint2, to_waypoint=waypoint1)
                elif (waypoint2 == edge_to_id) and (waypoint1 == edge_from_id):
                    # This edge matches the pair of waypoints! Add it the edge list and continue.
                    return map_pb2.Edge.Id(from_waypoint=waypoint1, to_waypoint=waypoint2)
        return None
    #-
    def _navigate_route(self, *args):
        """Navigate through a specific route of waypoints."""
        if len(args) < 1 or len(args[0]) < 1:
            # If no waypoint ids are given as input, then return without requesting navigation.
            print('No waypoints provided for navigate route.')
            return
        waypoint_ids = list(args[0])

        resolved_waypoint_ids = []
        for i in range(len(waypoint_ids)):
            resolved_id = self.find_unique_waypoint_id(
                waypoint_ids[i], self._current_graph, self._current_annotation_name_to_wp_id)
            if not resolved_id:
                # Failed to find the unique waypoint id.
                print(f"Fehler: Waypoint-ID für '{waypoint_ids[i]}' konnte nicht aufgelöst werden.")
                return False  # Navigation wird abgebrochen
            resolved_waypoint_ids.append(resolved_id)
            
        waypoint_ids = resolved_waypoint_ids
        edge_ids_list = []
        all_edges_found = True
        # Attempt to find edges in the current graph that match the ordered waypoint pairs.
        # These are necessary to create a valid route.
        for i in range(len(waypoint_ids) - 1):
            start_wp = waypoint_ids[i]
            end_wp = waypoint_ids[i + 1]
            edge_id = self._match_edge(self._current_edges, start_wp, end_wp)
            if edge_id is not None:
                edge_ids_list.append(edge_id)
            else:
                all_edges_found = False
                print(f'Failed to find an edge between waypoints: {start_wp} and {end_wp}')
                print(
                    'List the graph\'s waypoints and edges to ensure pairs of waypoints has an edge.'
                )
                break

        if all_edges_found:
            if not self.rc.toggle_power(should_power_on=True):
                print('Failed to power on the robot, and cannot complete navigate route request.')
                return

            # Navigate a specific route.
            route = self.rc.graph_nav_client.build_route(waypoint_ids, edge_ids_list)
            is_finished = False
            while not is_finished:
                # Issue the route command about twice a second such that it is easy to terminate the
                # navigation command (with estop or killing the program).
                nav_route_command_id = self.rc.graph_nav_client.navigate_route(
                    route, cmd_duration=1.0)
                time.sleep(.5)  # Sleep for half a second to allow for command execution.
                # Poll the robot for feedback to determine if the route is complete. Then sit
                # the robot down once it is finished.
                is_finished = self._check_success(nav_route_command_id)

            # Power off the robot if appropriate.
            if self.rc._powered_on and not self.rc._started_powered_on:
                # Sit the robot down + power off after the navigation command is complete.
                self.rc.toggle_power(should_power_on=False)
    #
    def _check_success(self, command_id=-1):
        """Use a navigation command id to get feedback from the robot and sit when command succeeds."""
        if command_id == -1:
            # No command, so we have no status to check.
            return False
        status = self.rc.graph_nav_client.navigation_feedback(command_id)
        if status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_REACHED_GOAL:
            # Successfully completed the navigation commands!
            return True
        elif status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_LOST:
            print('Robot got lost when navigating the route, the robot will now sit down.')
            return True
        elif status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_STUCK:
            print('Robot got stuck when navigating the route, the robot will now sit down.')
            return True
        elif status.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_ROBOT_IMPAIRED:
            print('Robot is impaired.')
            return True
        else:
            # Navigation command is not complete yet.
            return False


def main():

    parser = argparse.ArgumentParser(
        description="Spot Navigation Script with Arm and Camera Functionality"
    )
    parser.add_argument('-u', '--upload-filepath',
                        help='Full filepath to graph and snapshots to be uploaded.', required=True)
    bosdyn.client.util.add_base_arguments(parser)
    options = parser.parse_args()



    # Setup and authenticate the robot.
    sdk = bosdyn.client.create_standard_sdk('SeminarClient')
    robot = sdk.create_robot(options.hostname)
    bosdyn.client.util.authenticate(robot)

    # --- RobotController erzeugen ---
    rc = RobotController(robot)

    # Create nogui estop
    #estop_nogui = EstopNoGui(rc.estop_client, 'Estop NoGUI')
    #estop_nogui.allow()

    # Initialize GraphNavInterface
    navigation = GraphNavInterface(rc, options.upload_filepath)

    try:
        # Acquire lease
        with LeaseKeepAlive(rc.lease_client, must_acquire=True, return_at_exit=True):

            try:
                print("Power on...")
                rc.toggle_power(should_power_on=True)
                print("Powered on")
                

                print("Commanding robot to stand...")
                blocking_stand(rc.command_client)
                print("Robot standing.")
                time.sleep(3)
                robot_state = rc.state_client.get_robot_state()

                # # Navigation zu Waypoint
                print("Setze Location")
                navigation._set_initial_localization_fiducial()
                print("Gehe zu Location")

                
                is_finished = navigation._navigate_to(["inured-boxer-mCIfZdF867i3wEbkV+5syg=="])  # default
                
                if is_finished:
                    print("Waypoint erreicht: Starte Arm- und Greifer-Sequenz")

                    # 1. Arm ausklappen / bereit machen
                    print("Arm wird ausgeklappt...")
                    command = RobotCommandBuilder.arm_ready_command()


                    # Get robot pose in vision frame from robot state (we want to send commands in vision
                    # frame relative to where the robot stands now)
                    robot_state = rc.state_client.get_robot_state()

                    # 3. Arm bewegen (z.B. hochheben oder vorziehen)
                    print("Arm wird leicht nach vorne oben bewegt...")

                    x = 0.12727655470371246
                    y = -0.20078209042549133
                    z = 0.76679253578186035

                    qx = 0.28279393911361694
                    qy = 0.32262614369392395
                    qz = -0.64903956651687622
                    qw = 0.62824171781539917

                    command = RobotCommandBuilder.arm_pose_command(
                        x, y, z,
                        qw, qx, qy, qz,
                        'body',
                        seconds=3.0
                    )
                    rc.command_client.robot_command(command)
                    time.sleep(3)

                    # 4. Greifer öffnen (z.B. wieder loslassen)
                    print("Greifer öffnet...")
                    command = RobotCommandBuilder.claw_gripper_open_command()
                    rc.command_client.robot_command(command)
                    time.sleep(14)

                    # Bild aufnehmen
                    
                    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # 1. Absoluten Pfad des Skript-Ordners bestimmen
                    OUTPUT_DIR = os.path.join(SCRIPT_DIR, "spot_bilder") # 2. Zielordner definieren (z.B. ein Unterordner "spot_bilder")
                    
                    print(f"Bilder werden in folgendem Ordner gespeichert: {OUTPUT_DIR}")
                    try:
                        os.makedirs(OUTPUT_DIR, exist_ok=True)
                    except Exception as e:
                            print(f"WARNUNG: Konnte Zielordner nicht erstellen. Verwende Standard-Speicherort. Fehler: {e}")
                            OUTPUT_DIR = None # Setze auf None, um Fallback-Logik in maybe_save_image zu nutzen

                    rc.set_high_res_auto_params()
                    for i in range(2):
                        image_request = build_image_request(
                            'hand_color_image',
                            quality_percent=100,  # Maximum quality
                            image_format=image_pb2.Image.FORMAT_PNG,
                            resize_ratio=1.0  # No downsampling
                        )

                        # Request the image
                        image_response = rc.image_client.get_image([image_request])[0]

                        rc.maybe_save_image(image_response.shot.image, path=OUTPUT_DIR)
                        print("Bild erfolgreich gespeichert")
                        time.sleep(6)


                    time.sleep(4)


                    print("Greiferschließen...")
                    command = RobotCommandBuilder.claw_gripper_close_command()
                    rc.command_client.robot_command(command)
                    time.sleep(2)


                    # 5. Arm wieder verstauen
                    print("Arm wird verstaut...")
                    command = RobotCommandBuilder.arm_stow_command()
                    rc.command_client.robot_command(command)
                    time.sleep(3)
                    print("Arm-Sequenz erfolgreich abgeschlossen")
                    # -----------------------------

                #navigation._navigate_to(["fated-filly-uqC9P0DnwIVkUcjNIqMXHg=="]) # waypoint 3 wieder zurück irgendwo hin

                return True

            except Exception as exc:
                #estop_nogui.stop()
                print(exc)
                print('main run error.')
                return False

    except ResourceAlreadyClaimedError:
        # estop_nogui.stop()
        print(
            'The robot\'s lease is currently in use. Check for a tablet connection or try again in a few seconds.'
        )
        return False

    # estop_nogui.stop()

if __name__ == '__main__':
    if not main():
        sys.exit(1)