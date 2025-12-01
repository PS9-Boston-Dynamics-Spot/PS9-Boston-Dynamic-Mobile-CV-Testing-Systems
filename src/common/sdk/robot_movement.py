
import argparse
import logging
import math
import os
import sys
import time
import traceback


from PIL import Image
import io

import google.protobuf.timestamp_pb2
import grpc

import bosdyn.client.channel
import bosdyn.client.util
from bosdyn.api import geometry_pb2, power_pb2, robot_state_pb2, arm_command_pb2, image_pb2
from bosdyn.api.gps import gps_pb2
from bosdyn.api.graph_nav import graph_nav_pb2, map_pb2, nav_pb2
from bosdyn.client.exceptions import ResponseError
from bosdyn.client.frame_helpers import get_odom_tform_body
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive, ResourceAlreadyClaimedError
from bosdyn.client.math_helpers import Quat, SE3Pose
from bosdyn.client.power import PowerClient, power_on_motors, safe_power_off_motors
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
from bosdyn.client.robot_state import RobotStateClient

# Für Armsteuerung
from bosdyn.client.manipulation_api_client import ManipulationApiClient



# Für Armbewegung nach oben
from bosdyn.api.spot import robot_command_pb2
from bosdyn.client.math_helpers import SE3Pose, Quat
import time

# Für Foto
from bosdyn.client.image import ImageClient
from bosdyn.client.image import build_image_request

from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive

from bosdyn.api import basic_command_pb2

from bosdyn.client.robot_command import CommandFailedErrorWithFeedback
from bosdyn.client.exceptions import TimedOutError
from bosdyn.client.robot_command import CommandTimedOutError

from bosdyn.client.docking import DockingClient


from bosdyn.client.frame_helpers import VISION_FRAME_NAME, get_vision_tform_body




import sys


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


        # Power-State merken
        power_state = self.state_client.get_robot_state().power_state
        self._started_powered_on = (power_state.motor_power_state == power_state.STATE_ON)
        self._powered_on = self._started_powered_on

            
    def dock(self, dock_id: int, timeout_sec: int = 60):

        """Führt einen vollständigen Docking-Vorgang an der angegebenen Dock-ID aus."""

        print(f"[Dock] Starte Docking-Vorgang zu Dock-ID {dock_id}...")

        # 1. Sicherstellen, dass Spot steht
        print("[Dock] Stelle sicher, dass der Roboter steht...")
        self.blocking_stand()

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
    
    def blocking_command(self, command, check_status_fn, end_time_secs=None, timeout_sec=10,
                     update_frequency=1.0):
        """Helper function which uses the RobotCommandService to execute the given command.

        Blocks until check_status_fn return true, or raises an exception if the command times out or fails.
        This helper checks the main full_body/synchronized command status (RobotCommandFeedbackStatus), but
        the caller should check the status of the specific commands (stand, stow, selfright, etc.) in the callback.

        Args:
            command_client: RobotCommand client.
            command: The robot command to issue to the robot.
            check_status_fn: A callback that accepts RobotCommandFeedbackResponse and returns True when the
                            correct statuses are achieved for the specific requested command and throws
                            CommandFailedErrorWithFeedback if an error state occurs.
            end_time_sec: The local end time of the command (will be converted to robot time)
            timeout_sec: Timeout for the rpc in seconds.
            update_frequency: Update frequency for the command in Hz.

        Raises:
            CommandFailedErrorWithFeedback: Command feedback from robot is not STATUS_PROCESSING.
            bosdyn.client.robot_command.CommandTimedOutError: Command took longer than provided
                timeout.
        """

        def raise_not_processing(command_id, feedback_status, response):
            raise CommandFailedErrorWithFeedback(
                'Command (ID {}) no longer processing ({})'.format(
                    command_id,
                    basic_command_pb2.RobotCommandFeedbackStatus.Status.Name(feedback_status)),
                response)

        start_time = time.time()
        end_time = start_time + timeout_sec
        update_time = 1.0 / update_frequency

        command_id = self.command_client.robot_command(command, timeout=timeout_sec,
                                                end_time_secs=end_time_secs)

        now = time.time()
        while now < end_time:
            time_until_timeout = end_time - now
            rpc_timeout = max(time_until_timeout, 1)
            start_call_time = time.time()
            try:
                response = self.command_client.robot_command_feedback(command_id, timeout=rpc_timeout)
            except TimedOutError:
                # Excuse the TimedOutError and let the while check bail us out if we're out of time.
                pass
            else:
                # Check the high level robot command status'
                if response.feedback.HasField("full_body_feedback"):
                    full_body_status = response.feedback.full_body_feedback.status
                    if full_body_status != basic_command_pb2.RobotCommandFeedbackStatus.STATUS_PROCESSING:
                        raise_not_processing(command_id, full_body_status, response)
                elif response.feedback.HasField("synchronized_feedback"):
                    synchro_fb = response.feedback.synchronized_feedback
                    # Mobility Feedback
                    if synchro_fb.HasField("mobility_command_feedback"):
                        mob_status = synchro_fb.mobility_command_feedback.status
                        if mob_status != basic_command_pb2.RobotCommandFeedbackStatus.STATUS_PROCESSING:
                            raise_not_processing(command_id, mob_status, response)
                    # Arm Feedback
                    if synchro_fb.HasField("arm_command_feedback"):
                        arm_status = synchro_fb.arm_command_feedback.status
                        if arm_status != basic_command_pb2.RobotCommandFeedbackStatus.STATUS_PROCESSING:
                            raise_not_processing(command_id, arm_status, response)
                    # Gripper Feedback
                    if synchro_fb.HasField("gripper_command_feedback"):
                        gripper_status = synchro_fb.gripper_command_feedback.status
                        if gripper_status != basic_command_pb2.RobotCommandFeedbackStatus.STATUS_PROCESSING:
                            raise_not_processing(command_id, gripper_status, response)
                else:
                    raise CommandFailedErrorWithFeedback(
                        'Command (ID {}) has neither full body nor synchronized feedback'.format(
                            command_id), response)

                # Check low level command specific status'
                if check_status_fn(response):
                    return

            delta_t = time.time() - start_call_time
            time.sleep(max(min(delta_t, update_time), 0.0))
            now = time.time()

        raise CommandTimedOutError(
            "Took longer than {:.1f} seconds to execute the command.".format(now - start_time))


    def blocking_stand(self, timeout_sec=10, update_frequency=1.0, params=None):
        """Helper function which uses the RobotCommandService to stand.

        Blocks until robot is standing, or raises an exception if the command times out or fails.

        Args:
            command_client: RobotCommand client.
            timeout_sec: Timeout for the command in seconds.
            update_frequency: Update frequency for the command in Hz.
            params(spot.MobilityParams): Spot specific parameters for mobility commands to optionally set say body_height

        Raises:
            CommandFailedErrorWithFeedback: Command feedback from robot is not STATUS_PROCESSING.
            bosdyn.client.robot_command.CommandTimedOutError: Command took longer than provided
                timeout.
        """

        def check_stand_status(response):
            status = response.feedback.synchronized_feedback.mobility_command_feedback.stand_feedback.status
            return status == basic_command_pb2.StandCommand.Feedback.STATUS_IS_STANDING

        stand_command = RobotCommandBuilder.synchro_stand_command(params=params)
        self.blocking_command(stand_command, check_stand_status, timeout_sec=timeout_sec,
                        update_frequency=update_frequency)


    def blocking_sit(self, timeout_sec=10, update_frequency=1.0):
        """Helper function which uses the RobotCommandService to sit.

        Blocks until robot is sitting, or raises an exception if the command times out or fails.

        Args:
            command_client: RobotCommand client.
            timeout_sec: Timeout for the command in seconds.
            update_frequency: Update frequency for the command in Hz.

        Raises:
            CommandFailedErrorWithFeedback: Command feedback from robot is not STATUS_PROCESSING.
            bosdyn.client.robot_command.CommandTimedOutError: Command took longer than provided
                timeout.
        """

        def check_sit_status(response):
            status = response.feedback.synchronized_feedback.mobility_command_feedback.sit_feedback.status
            return status == basic_command_pb2.SitCommand.Feedback.STATUS_IS_SITTING

        sit_command = RobotCommandBuilder.synchro_sit_command()
        self.blocking_command(sit_command, check_sit_status, timeout_sec=timeout_sec,
                        update_frequency=update_frequency)




    ############################################

    
    def block_until_arm_arrives(self, cmd_id, timeout_sec=None):
        """Helper that blocks until the arm achieves a finishing state for the specific arm command.

        This helper will block and check the feedback for ArmCartesianCommand, GazeCommand,
        ArmJointMoveCommand, NamedArmPositionsCommand, and ArmImpedanceCommand.

        Args:
            command_client: robot command client, used to request feedback
            cmd_id: command ID returned by the robot when the arm movement command was sent.
            timeout_sec: optional number of seconds after which we'll return no matter what
                        the robot's state is.

        Return values:
            True if successfully got to the end of the trajectory, False if the arm stalled or
            the move was canceled (the arm failed to reach the goal). See the proto definitions in
            arm_command.proto for more information about why a trajectory would succeed or fail.
        """
        if timeout_sec is not None:
            start_time = time.time()
            end_time = start_time + timeout_sec
            now = time.time()

        while timeout_sec is None or now < end_time:
            feedback_resp = self.command_client.robot_command_feedback(cmd_id)
            arm_feedback = feedback_resp.feedback.synchronized_feedback.arm_command_feedback

            if arm_feedback.HasField("arm_cartesian_feedback"):
                if arm_feedback.arm_cartesian_feedback.status == arm_command_pb2.ArmCartesianCommand.Feedback.STATUS_TRAJECTORY_COMPLETE:
                    return True
                elif arm_feedback.arm_cartesian_feedback.status == arm_command_pb2.ArmCartesianCommand.Feedback.STATUS_TRAJECTORY_STALLED or feedback_resp.feedback.synchronized_feedback.arm_command_feedback.arm_cartesian_feedback.status == arm_command_pb2.ArmCartesianCommand.Feedback.STATUS_TRAJECTORY_CANCELLED:
                    return False
            elif arm_feedback.HasField("arm_gaze_feedback"):
                if arm_feedback.arm_gaze_feedback.status == arm_command_pb2.GazeCommand.Feedback.STATUS_TRAJECTORY_COMPLETE:
                    return True
                elif arm_feedback.arm_gaze_feedback.status == arm_command_pb2.GazeCommand.Feedback.STATUS_TOOL_TRAJECTORY_STALLED:
                    return False
            elif arm_feedback.HasField("arm_joint_move_feedback"):
                if arm_feedback.arm_joint_move_feedback.status == arm_command_pb2.ArmJointMoveCommand.Feedback.STATUS_COMPLETE:
                    return True
                elif arm_feedback.arm_joint_move_feedback.status == arm_command_pb2.ArmJointMoveCommand.Feedback.STATUS_STALLED:
                    return False
            elif arm_feedback.HasField("named_arm_position_feedback"):
                if arm_feedback.named_arm_position_feedback.status == arm_command_pb2.NamedArmPositionsCommand.Feedback.STATUS_COMPLETE:
                    return True
                elif arm_feedback.named_arm_position_feedback.status == arm_command_pb2.NamedArmPositionsCommand.Feedback.STATUS_STALLED_HOLDING_ITEM:
                    return False
            elif arm_feedback.HasField("arm_impedance_feedback"):
                if arm_feedback.arm_impedance_feedback.status == arm_command_pb2.ArmImpedanceCommand.Feedback.STATUS_TRAJECTORY_COMPLETE:
                    return True
                elif arm_feedback.arm_impedance_feedback.status == arm_command_pb2.ArmImpedanceCommand.Feedback.STATUS_TRAJECTORY_STALLED:
                    return False

            time.sleep(0.1)
            now = time.time()
        return False

    
    # Neu: Arm auf Höhe x bewegen
    def move_arm_to_height(self, height_meters: float):
        """Bewegt den Arm auf eine gewünschte Höhe in Metern."""
        cmd = RobotCommandBuilder.arm_pose_command(arm_name='left',
                                                   pose=SE3Pose(z=height_meters))
        self.command_client(cmd)

    # Neu: Arm schließen
    def close_gripper(self):
        """Schließt den Greifer."""
        cmd = RobotCommandBuilder.gripper_close_command()
        self.command_client(cmd)


    def maybe_save_image(self, image, path):
        """Try to save image, if client has correct deps."""
        try:
            import io

            from PIL import Image
        except ImportError:
            print('Missing dependencies. Can\'t save image.')
            return
        name = 'hello-spot-img.jpg'
        print(len(image.shot.image.data), 'bytes received')
        if path is not None and os.path.exists(path):
            path = os.path.join(os.getcwd(), path)
            name = os.path.join(path, name)
            print('Saving image to: %s', name)
        else:
            print('Saving image to working directory as %s', name)

        try:
            image = Image.open(io.BytesIO(image.data))
            image.save(name)
        except Exception as exc:
            
            print('Exception thrown saving image. %r', exc)



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
    
    
    
    """Graph nav utility functions"""


    def id_to_short_code(self, id):
        """Convert a unique id to a 2 letter short code."""
        tokens = id.split('-')
        if len(tokens) > 2:
            return f'{tokens[0][0]}{tokens[1][0]}'
        return None


    def pretty_print_waypoints(self, waypoint_id, waypoint_name, short_code_to_count, localization_id):
        short_code = self.id_to_short_code(waypoint_id)
        if short_code is None or short_code_to_count[short_code] != 1:
            short_code = '  '  # If the short code is not valid/unique, don't show it.

        waypoint_symbol = '->' if localization_id == waypoint_id else '  '
        print(
            f'{waypoint_symbol} Waypoint name: {waypoint_name} id: {waypoint_id} short code: {short_code}'
        )


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


    def update_waypoints_and_edges(self, graph, localization_id, do_print=True):
        """Update and print waypoint ids and edge ids."""
        name_to_id = dict()
        edges = dict()

        short_code_to_count = {}
        waypoint_to_timestamp = []
        for waypoint in graph.waypoints:
            # Determine the timestamp that this waypoint was created at.
            timestamp = -1.0
            try:
                timestamp = waypoint.annotations.creation_time.seconds + waypoint.annotations.creation_time.nanos / 1e9
            except:
                # Must be operating on an older graph nav map, since the creation_time is not
                # available within the waypoint annotations message.
                pass
            waypoint_to_timestamp.append((waypoint.id, timestamp, waypoint.annotations.name))

            # Determine how many waypoints have the same short code.
            short_code = self.id_to_short_code(waypoint.id)
            if short_code not in short_code_to_count:
                short_code_to_count[short_code] = 0
            short_code_to_count[short_code] += 1

            # Add the annotation name/id into the current dictionary.
            waypoint_name = waypoint.annotations.name
            if waypoint_name:
                if waypoint_name in name_to_id:
                    # Waypoint name is used for multiple different waypoints, so set the waypoint id
                    # in this dictionary to None to avoid confusion between two different waypoints.
                    name_to_id[waypoint_name] = None
                else:
                    # First time we have seen this waypoint annotation name. Add it into the dictionary
                    # with the respective waypoint unique id.
                    name_to_id[waypoint_name] = waypoint.id

        # Sort the set of waypoints by their creation timestamp. If the creation timestamp is unavailable,
        # fallback to sorting by annotation name.
        waypoint_to_timestamp = sorted(waypoint_to_timestamp, key=lambda x: (x[1], x[2]))

        # Print out the waypoints name, id, and short code in an ordered sorted by the timestamp from
        # when the waypoint was created.
        if do_print:
            print(f'{len(graph.waypoints):d} waypoints:')
            for waypoint in waypoint_to_timestamp:
                pretty_print_waypoints(waypoint[0], waypoint[2], short_code_to_count, localization_id)

        for edge in graph.edges:
            if edge.id.to_waypoint in edges:
                if edge.id.from_waypoint not in edges[edge.id.to_waypoint]:
                    edges[edge.id.to_waypoint].append(edge.id.from_waypoint)
            else:
                edges[edge.id.to_waypoint] = [edge.id.from_waypoint]
            if do_print:
                print(f'(Edge) from waypoint {edge.id.from_waypoint} to waypoint {edge.id.to_waypoint} '
                    f'(cost {edge.annotations.cost.value})')

        return name_to_id, edges


    def sort_waypoints_chrono(graph):
        """Sort waypoints by time created."""
        waypoint_to_timestamp = []
        for waypoint in graph.waypoints:
            # Determine the timestamp that this waypoint was created at.
            timestamp = -1.0
            try:
                timestamp = waypoint.annotations.creation_time.seconds + waypoint.annotations.creation_time.nanos / 1e9
            except:
                # Must be operating on an older graph nav map, since the creation_time is not
                # available within the waypoint annotations message.
                pass
            waypoint_to_timestamp.append((waypoint.id, timestamp, waypoint.annotations.name))

        # Sort the set of waypoints by their creation timestamp. If the creation timestamp is unavailable,
        # fallback to sorting by annotation name.
        waypoint_to_timestamp = sorted(waypoint_to_timestamp, key=lambda x: (x[1], x[2]))

        return waypoint_to_timestamp

        
    
    
    
    
    
    
    """GraphNav service command line interface."""

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



    def _set_initial_localization_waypoint(self, *args):
        """Trigger localization to a waypoint."""
        # Take the first argument as the localization waypoint.
        if len(args) < 1:
            # If no waypoint id is given as input, then return without initializing.
            print('No waypoint specified to initialize to.')
            return
        destination_waypoint = self.find_unique_waypoint_id(
            args[0][0], self._current_graph, self._current_annotation_name_to_wp_id)
        if not destination_waypoint:
            # Failed to find the unique waypoint id.
            return

        robot_state = self.rc.state_client.get_robot_state()
        current_odom_tform_body = get_odom_tform_body(
            robot_state.kinematic_state.transforms_snapshot).to_proto()
        # Create an initial localization to the specified waypoint as the identity.
        localization = nav_pb2.Localization()
        localization.waypoint_id = destination_waypoint
        localization.waypoint_tform_body.rotation.w = 1.0
        self.rc.graph_nav_client.set_localization(
            initial_guess_localization=localization,
            # It's hard to get the pose perfect, search +/-20 deg and +/-20cm (0.2m).
            max_distance=0.2,
            max_yaw=20.0 * math.pi / 180.0,
            fiducial_init=graph_nav_pb2.SetLocalizationRequest.FIDUCIAL_INIT_NO_FIDUCIAL,
            ko_tform_body=current_odom_tform_body)

    def _list_graph_waypoint_and_edge_ids(self, *args):
        """List the waypoint ids and edge ids of the graph currently on the robot."""

        # Download current graph
        graph = self.rc.graph_nav_client.download_graph()
        if graph is None:
            print('Empty graph.')
            return
        self._current_graph = graph

        localization_id = self.rc.graph_nav_client.get_localization_state().localization.waypoint_id

        # Update and print waypoints and edges
        self._current_annotation_name_to_wp_id, self._current_edges = self.update_waypoints_and_edges(
            graph, localization_id)

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

    def _navigate_to_anchor(self, *args):
        """Navigate to a pose in seed frame, using anchors."""
        # The following options are accepted for arguments: [x, y], [x, y, yaw], [x, y, z, yaw],
        # [x, y, z, qw, qx, qy, qz].
        # When a value for z is not specified, we use the current z height.
        # When only yaw is specified, the quaternion is constructed from the yaw.
        # When yaw is not specified, an identity quaternion is used.

        if len(args) < 1 or len(args[0]) not in [2, 3, 4, 7]:
            print('Invalid arguments supplied.')
            return

        seed_T_goal = SE3Pose(float(args[0][0]), float(args[0][1]), 0.0, Quat())

        if len(args[0]) in [4, 7]:
            seed_T_goal.z = float(args[0][2])
        else:
            localization_state = self.rc.graph_nav_client.get_localization_state()
            if not localization_state.localization.waypoint_id:
                print('Robot not localized')
                return
            seed_T_goal.z = localization_state.localization.seed_tform_body.position.z

        if len(args[0]) == 3:
            seed_T_goal.rot = Quat.from_yaw(float(args[0][2]))
        elif len(args[0]) == 4:
            seed_T_goal.rot = Quat.from_yaw(float(args[0][3]))
        elif len(args[0]) == 7:
            seed_T_goal.rot = Quat(w=float(args[0][3]), x=float(args[0][4]), y=float(args[0][5]),
                                   z=float(args[0][6]))

        if not self.rc.toggle_power(should_power_on=True):
            print('Failed to power on the robot, and cannot complete navigate to request.')
            return

        nav_to_cmd_id = None
        # Navigate to the destination.
        is_finished = False
        while not is_finished:
            # Issue the navigation command about twice a second such that it is easy to terminate the
            # navigation command (with estop or killing the program).
            try:
                nav_to_cmd_id = self.rc.graph_nav_client.navigate_to_anchor(
                    seed_T_goal.to_proto(), 1.0, command_id=nav_to_cmd_id)
            except ResponseError as e:
                print(f'Error while navigating {e}')
                break
            time.sleep(.5)  # Sleep for half a second to allow for command execution.
            # Poll the robot for feedback to determine if the navigation command is complete. Then sit
            # the robot down once it is finished.
            is_finished = self._check_success(nav_to_cmd_id)

        # Power off the robot if appropriate.
        if self.rc._powered_on and not self.rc._started_powered_on:
            # Sit the robot down + power off after the navigation command is complete.
            self.rc.toggle_power(should_power_on=False)

    def _navigate_to_gps_coords(self, *args):
        """Navigates to GPS coordinates using the NavigateToAnchor RPC from arguments.
           The arguments are directly captured from keyboard input."""
        coords = self._parse_gps_goal_from_args(args[0])
        if not coords:
            return
        self._navigate_to_parsed_gps_coords(coords[0], coords[1], coords[2])

    def _parse_gps_goal_from_args(self, list_of_strings: list):
        """ This function first parses the input from cin, which is passed in an argument.
         The following options are accepted for arguments:
         [latitude_degrees, longitude_degrees], [latitude_degrees, longitude_degrees, yaw_around_up_radians]
         Returns a tuple of latitude, longitude and yaw (where yaw is possibly None).
        """
        if len(list_of_strings) not in [2, 3]:
            print('Invalid arguments supplied.')
            return None

        latitude = float(list_of_strings[0])
        longitude = longitude = float(list_of_strings[1])
        yaw = None
        if len(list_of_strings) == 3:
            yaw = float(list_of_strings[2])
        return (latitude, longitude, yaw)

    def _navigate_to_parsed_gps_coords(self, latitude_degrees, longitude_degrees,
                                       yaw_around_up_radians=None):
        """Navigates to GPS coordinates using the NavigateToAnchor RPC."""
        llh = gps_pb2.LLH(latitude=latitude_degrees, longitude=longitude_degrees, height=0.0)
        gps_params = graph_nav_pb2.GPSNavigationParams(goal_llh=llh)
        if yaw_around_up_radians:
            gps_params.goal_yaw.value = yaw_around_up_radians

        if not self.rc.toggle_power(should_power_on=True):
            print('Failed to power on the robot, and cannot complete navigate to request.')
            return

        nav_to_cmd_id = None
        # Navigate to the destination.
        is_finished = False
        while not is_finished:
            # Issue the navigation command about twice a second such that it is easy to terminate the
            # navigation command (with estop or killing the program).
            try:
                nav_to_cmd_id = self.rc.graph_nav_client.navigate_to_anchor(
                    SE3Pose.from_identity().to_proto(), 1.0, command_id=nav_to_cmd_id,
                    gps_navigation_params=gps_params)
            except ResponseError as e:
                print(f'Error while navigating {e}')
                break
            time.sleep(.5)  # Sleep for half a second to allow for command execution.
            # Poll the robot for feedback to determine if the navigation command is complete. Then sit
            # the robot down once it is finished.
            is_finished = self._check_success(nav_to_cmd_id)

        # Power off the robot if appropriate.
        if self.rc._powered_on and not self.rc._started_powered_on:
            # Sit the robot down + power off after the navigation command is complete.
            self.rc.toggle_power(should_power_on=False)

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

        # Power off the robot if appropriate.
        if self.rc._powered_on and not self.rc._started_powered_on:
            #self.rc.toggle_power(should_power_on=False)
            print("Lege hin")
        # Neu hinzufügen: Rückgabewert True/False für erfolgreiche Navigation
        return self._check_success(nav_to_cmd_id)

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
    """Run the command-line interface with GraphNav navigation and arm/gripper control."""

    parser = argparse.ArgumentParser(
        description="Spot navigiert automatisch mit GraphNav und E-Stop GUI"
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
                rc.blocking_stand()
                print("Robot standing.")
                time.sleep(3)
                robot_state = rc.state_client.get_robot_state()

                # Navigation zu Waypoint
                print("Setze Location")
                navigation._set_initial_localization_fiducial()
                print("Gehe zu Location")
                navigation._navigate_to(["fated-filly-uqC9P0DnwIVkUcjNIqMXHg=="]) # waypoint 3
                navigation._navigate_to(["fringy-hyla-nlBmspSxRbmgsIwQXeE.iQ=="])  # waypoint 17
                # navigation._navigate_to(["soiled-lapdog-fPT7RjQ+8okX+FN9gHbFSg=="])  # waypoint 2
                navigation._navigate_to(["fated-filly-uqC9P0DnwIVkUcjNIqMXHg=="]) # waypoint 3
                # Prüfen, ob Waypoint erreicht wurde
                nav_state = navigation._check_success()
                
                
                
                # Wir setzen reached zum test mal auf true

                #Funktioniert so nicht
                # reached = nav_state if isinstance(nav_state, bool) else True
                reached = False

                #Funktioniert so nicht
                #print("Starte Navigation der Route")
                # Definieren Sie die Route als Liste von Waypoint-Namen/IDs
                #waypoint_route = [
                #     "fringy-hyla-nlBmspSxRbmgsIwQXeE.iQ==",
                #     "pulpy-oryx-t4DKvizO9AxYUnF9VdcHPA==",
                #     "snuffed-giant-ne3n2OhXIGj.qckq4DsUTw==",
                #     "nifty-canine-JpIqR470bflH8VGAxXVwbg==",
                #     "pudgy-larva-V2DpDr.8zc3kp6hd6of6jg==",
                #     "manic-poodle-g45pwx1WO21S5cdyZ4YnUQ==",
                #     "ferned-cuscus-zhY2vevTJdyiYi6t6ki8tg==",
                #     "tinpot-raven-ayB1AFAv+DPCU4mfiFg.cw==",
                #     "bared-anole-D7tcRCPS16tvo8O8JgDN8w==",
                #     "broke-cod-BzH47.UlGW9XTkSovzVgfQ==",
                #     "six-yak-eXnqD2F5SPqQLLMgTEAGEA==",
                #     "must-crow-7qJx3biOfsnVCoqP.NkzYg==", # Weiterer Waypoint (Edge von six-yak)
                #     "yelled-pincer-yvVnucpX.9sRSMDZDXC3Zg==", # Weiterer Waypoint (Edge von must-crow)
                #     "soiled-lapdog-fPT7RjQ+8okX+FN9gHbFSg=="
                # ]
                # Führen Sie die Routennavigation durch und speichern Sie das Ergebnis
                #reached = navigation._navigate_route(waypoint_route)




                
                if reached:
                    print("Letzter Waypoint erreicht – starte Docking…")

                    #  Dock-ID 
                    DOCK_ID = 520      

                    try:
                        rc.dock(DOCK_ID)
                        print("Docking erfolgreich!")
                    except Exception as e:
                        print(f"Docking fehlgeschlagen: {e}")
                else:
                    print("Waypoint NICHT erreicht – Docking wird abgebrochen.")


                if 1==2:
                    print("Waypoint erreicht: Starte Arm- und Greifer-Sequenz")

                    # -----------------------------
                    # 1. Arm ausklappen / bereit machen
                    print("Arm wird ausgeklappt...")
                    command = RobotCommandBuilder.arm_ready_command()
                    unstow_command_id = rc.command_client.robot_command(command)

                    # Wait until the stow command is successful.
                    rc.block_until_arm_arrives(unstow_command_id, 3.0)

                    # Get robot pose in vision frame from robot state (we want to send commands in vision
                    # frame relative to where the robot stands now)
                    robot_state = rc.state_client.get_robot_state()
                    vision_T_body = get_vision_tform_body(robot_state.kinematic_state.transforms_snapshot)


                    time.sleep(3)  # Warten, damit Spot die Armbewegung abschließt


                    # 3. Arm bewegen (z.B. hochheben oder vorziehen)
                    print("Arm wird leicht nach vorne oben bewegt...")

                    # Beispiel: etwas vor den Roboter (x=0.6m), mittig (y=0), leicht angehoben (z=0.4m)
                    x, y, z = 0.6, 0.0, 0.4

                    # Keine Drehung (Einheitsquaternion)
                    qw, qx, qy, qz = 1.0, 0.0, 0.0, 0.0

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
                    time.sleep(2)

                    # Bild aufnehmen
                    # Ein einzelnes Bild abrufen
                    # Quelle: Handkamera im Greifarm
                    HAND_CAMERA_SOURCE = 'hand_color_image'

                    #Alt
                    # 1. Bild einmalig vom Roboter abrufen
                    #image_response = rc.image_client.get_image_from_sources([HAND_CAMERA_SOURCE])[0]

                    

                    image_request = build_image_request(
                        'hand_color_image',
                        quality_percent=100,  # Maximum quality
                        image_format=image_pb2.Image.FORMAT_JPEG,
                        resize_ratio=1.0  # No downsampling
                    )

                    # Request the image
                    image_response = rc.image_client.get_image([image_request])[0]
                    
                    rc.maybe_save_image(image_response.shot.image, path=None)

                    print("Bild erfolgreich gespeichert")


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

                return True

            except Exception as exc:  # pylint: disable=broad-except
                #estop_nogui.stop()
                print(exc)
                print('main run error.')
                return False

    except ResourceAlreadyClaimedError:
        #estop_nogui.stop()
        print(
            'The robot\'s lease is currently in use. Check for a tablet connection or try again in a few seconds.'
        )
        return False

    #estop_nogui.stop()



if __name__ == '__main__':
    if not main():
        sys.exit(1)