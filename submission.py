"""
Competition instructions:
Please do not change anything else but fill out the to-do sections.
"""

import atexit
import json
import math
import os
from collections import deque
from functools import reduce
from typing import Dict, List, Optional, Tuple

import numpy as np
import roar_py_interface

from LateralController import LatController
from section_config_21 import SECTION_CONFIG, apply_steer_multiplier
from ThrottleController import ThrottleController

# from scipy.interpolate import interp1d


useDebug = False
useDebugPrinting = False
debugData = {}


def dist_to_waypoint(location, waypoint: roar_py_interface.RoarPyWaypoint):
    return np.linalg.norm(location[:2] - waypoint.location[:2])


def filter_waypoints(
    location: np.ndarray,
    current_idx: int,
    waypoints: List[roar_py_interface.RoarPyWaypoint],
) -> int:
    for i in range(current_idx, len(waypoints) + current_idx):
        if dist_to_waypoint(location, waypoints[i % len(waypoints)]) < 3:
            return i % len(waypoints)
    return current_idx


def findClosestIndex(location, waypoints: List[roar_py_interface.RoarPyWaypoint]):
    lowestDist = 100
    closestInd = 0
    for i in range(0, len(waypoints)):
        dist = dist_to_waypoint(location, waypoints[i % len(waypoints)])
        if dist < lowestDist:
            lowestDist = dist
            closestInd = i
    return closestInd % len(waypoints)


@atexit.register
def saveDebugData():
    if useDebug:
        print("Saving debug data")
        jsonData = json.dumps(debugData, indent=4)
        with open(
            f"{os.path.dirname(__file__)}\\debugData\\debugData.json", "w+"
        ) as outfile:
            outfile.write(jsonData)
        print("Debug Data Saved")


class RoarCompetitionSolution:
    def __init__(
        self,
        maneuverable_waypoints: List[roar_py_interface.RoarPyWaypoint],
        vehicle: roar_py_interface.RoarPyActor,
        camera_sensor: roar_py_interface.RoarPyCameraSensor = None,
        location_sensor: roar_py_interface.RoarPyLocationInWorldSensor = None,
        velocity_sensor: roar_py_interface.RoarPyVelocimeterSensor = None,
        rpy_sensor: roar_py_interface.RoarPyRollPitchYawSensor = None,
        occupancy_map_sensor: roar_py_interface.RoarPyOccupancyMapSensor = None,
        collision_sensor: roar_py_interface.RoarPyCollisionSensor = None,
    ) -> None:
        self.maneuverable_waypoints = maneuverable_waypoints
        self.vehicle = vehicle
        self.camera_sensor = camera_sensor
        self.location_sensor = location_sensor
        self.velocity_sensor = velocity_sensor
        self.rpy_sensor = rpy_sensor
        self.occupancy_map_sensor = occupancy_map_sensor
        self.collision_sensor = collision_sensor
        self.lat_controller = LatController()
        self.throttle_controller = ThrottleController()
        self.section_indeces = []
        self.num_ticks = 0
        self.section_start_ticks = 0
        self.current_section = 0
        self.lapNum = 1

        self.prev_steer = 0.0
        self.last_lookahead_idx_16 = None

    async def initialize(self) -> None:
        # NOTE waypoints are changed through this line
        self.maneuverable_waypoints = (
            roar_py_interface.RoarPyWaypoint.load_waypoint_list(
                np.load(f"{os.path.dirname(__file__)}\\waypoints\\waypointsPrimary.npz")
            )[35:]
        )

        sectionLocations = [
            [
                -283.79998779296875,
                391.6999816894531,
            ],  # Section 0 - chicane (avg speed: 295.9 km/h, avg friction: 1.39)
            [
                -319.3346252441406,
                510.0881652832031,
            ],  # Section 1 - chicane (avg speed: 299.2 km/h, avg friction: 2.33)
            [
                -321.09136962890625,
                622.216552734375,
            ],  # Section 2 - chicane (avg speed: 288.4 km/h, avg friction: 2.64)
            [
                -273.2111511230469,
                737.3875732421875,
            ],  # Section 3 - chicane (avg speed: 299.7 km/h, avg friction: 2.40)
            [
                -196.5764617919922,
                817.513671875,
            ],  # Section 4 - chicane (avg speed: 296.4 km/h, avg friction: 2.17)
            [
                -6.26312255859375,
                880.831787109375,
            ],  # Section 5 - chicane (avg speed: 300.0 km/h, avg friction: 1.27)
            [
                293.6314697265625,
                910.001220703125,
            ],  # Section 6 - chicane (avg speed: 205.5 km/h, avg friction: 3.28)
            [
                415.163818359375,
                1001.20458984375,
            ],  # Section 7 - chicane (avg speed: 300.0 km/h, avg friction: 0.68)
            [
                597.3222045898438,
                1067.930419921875,
            ],  # Section 8 - chicane (avg speed: 235.6 km/h, avg friction: 3.15)
            [
                746.5614013671875,
                996.1705322265625,
            ],  # Section 9 - chicane (avg speed: 300.0 km/h, avg friction: 1.19)
            [
                773.0881958007812,
                797.8821411132812,
            ],  # Section 10 - chicane (avg speed: 232.6 km/h, avg friction: 3.21)
            [
                713.7614135742188,
                699.0301513671875,
            ],  # Section 11 - chicane (avg speed: 300.0 km/h, avg friction: 0.87)
            [
                502.9869689941406,
                577.037109375,
            ],  # Section 12 - chicane (avg speed: 299.7 km/h, avg friction: 1.10)
            [
                12.214154243469238,
                134.254638671875,
            ],  # Section 13 - chicane (avg speed: 240.5 km/h, avg friction: 2.89)
            [
                -12.016829490661621,
                34.56936264038086,
            ],  # Section 14 - chicane (avg speed: 222.7 km/h, avg friction: 3.18)
            [
                -71.82583618164062,
                -83.7726821899414,
            ],  # Section 15 - chicane (avg speed: 284.1 km/h, avg friction: 2.19)
            [-107.604003906, -880.179688],  # Section 16
            [
                -259.32183837890625,
                -1048.1566162109375,
            ],  # Section 17 - chicane (avg speed: 276.2 km/h, avg friction: 2.95)
            [
                -341.6862487792969,
                -937.5551147460938,
            ],  # Section 18 - chicane (avg speed: 299.8 km/h, avg friction: 1.17)
            [
                -348.8890686035156,
                -98.31,
            ],  # Section 19 - chicane (avg speed: 157.2 km/h, avg friction: 3.29)
            [
                -339.8890686035156,
                278.5424499511719,
            ],  # Section 20 - chicane (avg speed: 157.2 km/h, avg friction: 3.29)
        ]

        for i in sectionLocations:
            self.section_indeces.append(
                findClosestIndex(i, self.maneuverable_waypoints)
            )

        print(f"True total length: {len(self.maneuverable_waypoints) * 3}")
        print(f"1 lap length: {len(self.maneuverable_waypoints)}")
        print(f"Section indexes: {self.section_indeces}")
        print("\nLap 1\n")

        # Receive location, rotation and velocity data
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()

        self.current_waypoint_idx = 0
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location, self.current_waypoint_idx, self.maneuverable_waypoints
        )

    async def step(self) -> None:
        """
        This function is called every world step.
        Note: You should not call receive_observation() on any sensor here, instead use get_last_observation() to get the last received observation.
        You can do whatever you want here, including apply_action() to the vehicle.
        """
        self.num_ticks += 1

        # Receive location, rotation and velocity data
        vehicle_location = self.location_sensor.get_last_gym_observation()
        vehicle_rotation = self.rpy_sensor.get_last_gym_observation()
        vehicle_velocity = self.velocity_sensor.get_last_gym_observation()
        vehicle_velocity_norm = np.linalg.norm(vehicle_velocity)
        physical_speed_kmh = vehicle_velocity_norm * 3.6

        # Find the waypoint closest to the vehicle
        self.current_waypoint_idx = filter_waypoints(
            vehicle_location, self.current_waypoint_idx, self.maneuverable_waypoints
        )

        # compute and print section timing
        for i, section_ind in enumerate(self.section_indeces):
            if (
                abs(self.current_waypoint_idx - section_ind) <= 2
                and i != self.current_section
            ):
                print(f"Section {i}: {self.num_ticks - self.section_start_ticks} ticks")
                self.section_start_ticks = self.num_ticks
                self.current_section = i

                # When we ENTER section 16, reset its smoothing state
                if self.current_section == 16:
                    self.last_lookahead_idx_16 = None
                    if hasattr(self, "_prev_target_loc_16"):
                        del self._prev_target_loc_16

                if self.current_section == 0 and self.lapNum != 3:
                    self.lapNum += 1
                    print(f"\nLap {self.lapNum}\n")

        nextWaypointIndex = self.get_lookahead_index(physical_speed_kmh)
        waypoint_to_follow = self.next_waypoint_smooth(physical_speed_kmh)

        # Pure pursuit controller to steer the vehicle
        steer_control = self.lat_controller.run(
            vehicle_location, vehicle_rotation, waypoint_to_follow
        )

        # Custom controller to control the vehicle's speed
        waypoints_for_throttle = (self.maneuverable_waypoints * 2)[
            nextWaypointIndex : nextWaypointIndex + 300
        ]

        speed_for_throttle = physical_speed_kmh
        if self.current_section == 16:
            speed_for_throttle = physical_speed_kmh * 1  # or 1.3, tune here
            print(
                f" the steeering control is {steer_control}, the spped {physical_speed_kmh} and the speed for throttle {speed_for_throttle}"
            )

        throttle, brake, gear = self.throttle_controller.run(
            waypoints_for_throttle,
            vehicle_location,
            speed_for_throttle,
            self.current_section,
        )

        if self.current_section in (16, 17):
            # Safer steering gain for the hairpin:
            # less gain at high speed, more at low speed
            if physical_speed_kmh > 160:
                base_steer_mult = 0.9
            elif physical_speed_kmh > 110:
                base_steer_mult = 1.0
            elif physical_speed_kmh > 70:
                base_steer_mult = 1.2
            else:
                base_steer_mult = 1.4

        elif self.current_section == 20:
            # More authority turning into this final chicane
            if physical_speed_kmh > 170:
                base_steer_mult = 1.4
            elif physical_speed_kmh > 130:
                base_steer_mult = 1.25
            elif physical_speed_kmh > 90:
                base_steer_mult = 1.1
            elif physical_speed_kmh > 60:
                base_steer_mult = 1.0
            else:
                base_steer_mult = 1.0

        else:
            base_steer_mult = round((physical_speed_kmh + 0.001) / 120, 3)

        steerMultiplier = apply_steer_multiplier(base_steer_mult, self.current_section)

        raw_steer = float(np.clip(steer_control * steerMultiplier, -1, 1))

        # initialize on first tick if needed
        if self.num_ticks == 1:
            self.prev_steer = raw_steer

        if self.current_section == 16:
            # Max change in steer per tick – tune 0.04–0.08 if needed
            max_delta = 0.12
            lower = self.prev_steer - max_delta
            upper = self.prev_steer + max_delta
            smooth_steer = float(np.clip(raw_steer, lower, upper))
        elif self.current_section == 18:
            # Smaller allowed change per tick – softens that last snap
            max_delta = 0.01  # try 0.06–0.10 range
            lower = self.prev_steer - max_delta
            upper = self.prev_steer + max_delta
            smooth_steer = float(np.clip(raw_steer, lower, upper))
        elif self.current_section in (19, 20):
            # Smaller allowed change per tick – softens that last snap
            max_delta = 0.06  # try 0.06–0.10 range
            lower = self.prev_steer - max_delta
            upper = self.prev_steer + max_delta
            smooth_steer = float(np.clip(raw_steer, lower, upper))
        else:
            smooth_steer = raw_steer

        self.prev_steer = smooth_steer
        control = {
            "throttle": np.clip(throttle, 0, 1),
            "steer": smooth_steer,
            "brake": np.clip(brake, 0, 1),
            "hand_brake": 0,
            "reverse": 0,
            "target_gear": gear,  # Gears do not appear to have an impact on speed
        }

        # more control the of steer
        if self.current_section == 16:
            # Needs more authority – it's understeering into the outside wall.
            if physical_speed_kmh > 200:
                max_steer = 0.30  # was 0.30
            elif physical_speed_kmh > 150:
                max_steer = 0.40  # was 0.40
            elif physical_speed_kmh > 100:
                max_steer = 0.55  # was 0.55
            else:
                max_steer = 0.65
            control["steer"] = np.clip(control["steer"], -max_steer, max_steer)

        elif self.current_section == 17:
            # Keep 17 tighter, it's slower there
            if physical_speed_kmh > 150:
                max_steer = 0.45
            elif physical_speed_kmh > 100:
                max_steer = 0.60
            else:
                max_steer = 0.80

            control["steer"] = np.clip(control["steer"], -max_steer, max_steer)
        elif self.current_section == 19:
            # FIX: Increase max steer to allow the car to turn enough at speed.
            # The previous limits (0.40/0.45) caused massive understeer into the left wall.
            if physical_speed_kmh > 150:
                max_steer = 0.45  # WAS 0.40 -> Much more authority now
            elif physical_speed_kmh > 80:
                max_steer = 0.45  # WAS 0.45
            else:
                max_steer = 0.65  # WAS 0.65 (Allow max steer at low speed)

            control["steer"] = np.clip(control["steer"], -max_steer, max_steer)

            control["steer"] = np.clip(control["steer"], -max_steer, max_steer)

        if useDebug:
            debugData[self.num_ticks] = {}
            debugData[self.num_ticks]["loc"] = [
                round(vehicle_location[0].item(), 3),
                round(vehicle_location[1].item(), 3),
            ]
            debugData[self.num_ticks]["throttle"] = round(float(control["throttle"]), 3)
            debugData[self.num_ticks]["brake"] = round(float(control["brake"]), 3)
            debugData[self.num_ticks]["steer"] = round(float(control["steer"]), 10)
            debugData[self.num_ticks]["speed"] = round(physical_speed_kmh, 3)
            debugData[self.num_ticks]["lap"] = self.lapNum

            if useDebugPrinting and self.num_ticks % 5 == 0:
                print(
                    f"- Target waypoint: ({waypoint_to_follow.location[0]:.2f}, {waypoint_to_follow.location[1]:.2f}) index {nextWaypointIndex} \n\
Current location: ({vehicle_location[0]:.2f}, {vehicle_location[1]:.2f}) index {self.current_waypoint_idx} section {self.current_section} \n\
Distance to target waypoint: {math.sqrt((waypoint_to_follow.location[0] - vehicle_location[0]) ** 2 + (waypoint_to_follow.location[1] - vehicle_location[1]) ** 2):.3f}\n"
                )

                print(
                    f"--- Speed: {physical_speed_kmh:.2f} kph \n\
Throttle: {control['throttle']:.3f} \n\
Brake: {control['brake']:.3f} \n\
Steer: {control['steer']:.10f} \n"
                )

        await self.vehicle.apply_action(control)
        return control

    def get_lookahead_index(self, speed):
        """
        Adds the lookahead waypoint to the current waypoint and normalizes it so that the value does not go out of bounds
        """
        num_waypoints = self.get_lookahead_value(speed)
        return (self.current_waypoint_idx + num_waypoints) % len(
            self.maneuverable_waypoints
        )

    def get_lookahead_value(self, speed: float) -> int:
        """
        Returns the number of waypoints to look ahead based on the speed.
        Special-case section 19 for a shorter lookahead into the sharp turn.
        """
        # Section-specific tuning for 19
        if self.current_section == 20:
            # Keep lookahead short so we hug the corner
            if speed > 160:
                return 4
            elif speed > 120:
                return 4
            elif speed > 80:
                return 4
            else:
                return 1

        # Default mapping used everywhere else
        speed_to_lookahead_dict = {
            90: 9,
            110: 11,
            130: 14,
            160: 18,
            180: 22,
            200: 26,
            250: 30,
            300: 35,
        }

        for speed_upper_bound, num_points in speed_to_lookahead_dict.items():
            if speed < speed_upper_bound:
                return num_points

        # Fallback
        return 8

    # The idea and code for averaging points is from smooth_waypoint_following_local_planner.py (Summer 2023)
    def next_waypoint_smooth(self, current_speed: float):
        """
        Choose the next waypoint with some section-specific smoothing.

        - Section 16: custom tight lookahead + temporal smoothing (hairpin).
        - Sections 19–20: always use averaged/smoothed path via average_point().
        - Section 17: plain lookahead (no extra smoothing).
        - Default: original behavior – smooth when fast, raw when slow.
        """
        base_lookahead = self.get_lookahead_value(current_speed)
        N = len(self.maneuverable_waypoints)

        # ----- SECTION 16: special tight hairpin logic -----
        if self.current_section == 16:
            # Local lookahead tuned for the hairpin
            local_lookahead = base_lookahead
            if current_speed > 140:
                local_lookahead = max(10, int(base_lookahead * 0.8))
            elif current_speed > 80:
                local_lookahead = max(8, int(base_lookahead * 0.9))
            else:
                local_lookahead = max(6, int(base_lookahead * 1.0))

            # Base index
            default_idx = (self.current_waypoint_idx + local_lookahead) % N

            # Limit index jump per tick to avoid target “teleporting”
            if self.last_lookahead_idx_16 is not None:
                prev_idx = self.last_lookahead_idx_16

                # Signed difference on the circular track
                diff = (default_idx - prev_idx + N) % N
                if diff > N / 2:
                    diff -= N
                # Clamp jump
                diff = int(np.clip(diff, -2, 2))
                default_idx = (prev_idx + diff + N) % N

            self.last_lookahead_idx_16 = default_idx

            wp = self.maneuverable_waypoints[default_idx]
            new_loc = wp.location

            # Temporal smoothing of the target location
            prev_loc = getattr(self, "_prev_target_loc_16", new_loc)
            alpha = 0.15  # 0 = fully old, 1 = fully new
            blended_loc = (1 - alpha) * prev_loc + alpha * new_loc
            self._prev_target_loc_16 = blended_loc

            return roar_py_interface.RoarPyWaypoint(
                location=blended_loc,
                roll_pitch_yaw=wp.roll_pitch_yaw,
                lane_width=wp.lane_width,
            )

        # If we are not in section 16, reset its smoothing state
        self.last_lookahead_idx_16 = None

        if self.current_section in (19, 20):
            return self.average_point(current_speed)

        # ----- SECTION 17: simple, no extra smoothing -----
        if self.current_section == 17:
            idx = self.get_lookahead_index(current_speed)
            return self.maneuverable_waypoints[idx]

            # ----- SECTION 0: always use smoothing -----
        if self.current_section == 0:
            return self.average_point(current_speed)

        # ----- DEFAULT BEHAVIOR -----
        # At higher speed: smoothed trajectory via average_point()
        # At low speed: just follow the raw lookahead waypoint.
        if 70 < current_speed < 300:
            return self.average_point(current_speed)
        else:
            idx = self.get_lookahead_index(current_speed)
            return self.maneuverable_waypoints[idx]

    def average_point(self, current_speed):
        lookahead_value = self.get_lookahead_value(current_speed)
        default_lookahead_idx = self.get_lookahead_index(current_speed)

        # Get section-specific smoothing parameters
        smoothing_config = SECTION_CONFIG.get(self.current_section, {}).get(
            "waypoint_smoothing", {}
        )

        # Calculate next_waypoint_index
        offset = smoothing_config.get("offset")
        if offset is None:
            next_waypoint_index = (self.current_waypoint_idx + 18) % len(
                self.maneuverable_waypoints
            )
        elif offset < 0:
            # Negative offset: closer lookahead
            next_waypoint_index = (default_lookahead_idx - abs(offset)) % len(
                self.maneuverable_waypoints
            )
        else:
            next_waypoint_index = (self.current_waypoint_idx + offset) % len(
                self.maneuverable_waypoints
            )

        # Calculate num_points
        num_points = smoothing_config.get("num_points")
        if num_points is None:
            num_points = lookahead_value * 2
        elif isinstance(num_points, float):
            # Multiplier
            num_points = round(lookahead_value * num_points)

        max_shift_distance = smoothing_config.get("max_shift", 2.0)

        # Handle edge case: if num_points is 0 or negative, use default
        if num_points <= 0:
            num_points = lookahead_value * 2
            next_waypoint_index = default_lookahead_idx

        start_index_for_avg = (next_waypoint_index - (num_points // 2)) % len(
            self.maneuverable_waypoints
        )

        next_waypoint = self.maneuverable_waypoints[next_waypoint_index]
        next_location = next_waypoint.location

        sample_points = [
            (start_index_for_avg + i) % len(self.maneuverable_waypoints)
            for i in range(0, num_points)
        ]
        if num_points > 3:
            location_sum = reduce(
                lambda x, y: x + y,
                (self.maneuverable_waypoints[i].location for i in sample_points),
            )
            num_points = len(sample_points)
            new_location = location_sum / num_points
            shift_distance = np.linalg.norm(next_location - new_location)

            if shift_distance > max_shift_distance:
                uv = (new_location - next_location) / shift_distance
                new_location = next_location + uv * max_shift_distance

            target_waypoint = roar_py_interface.RoarPyWaypoint(
                location=new_location,
                roll_pitch_yaw=np.ndarray([0, 0, 0]),
                lane_width=0.0,
            )
        else:
            target_waypoint = self.maneuverable_waypoints[next_waypoint_index]

        return target_waypoint
