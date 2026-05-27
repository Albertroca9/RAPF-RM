from dataclasses import dataclass, field
from enum import Enum

from .detections import DetectedObject
from .taxonomy import SafetyClass


class RobotState(str, Enum):
    EXPLORE = "explore"
    TRACK_TRASH = "track_trash"
    APPROACH = "approach"
    PICK = "pick"
    NAVIGATE_TO_BIN = "navigate_to_bin"
    DROP = "drop"
    AVOID_BLOCKED = "avoid_blocked"
    ERROR = "error"


@dataclass(frozen=True)
class RobotEvent:
    detections: list[DetectedObject] = field(default_factory=list)
    gripper_has_object: bool = False
    at_bin: bool = False
    drop_complete: bool = False


@dataclass(frozen=True)
class RobotDecision:
    state: RobotState
    command: str
    target: DetectedObject | None = None
    target_bin: str | None = None
    reason: str | None = None


class WasteBehaviorStateMachine:
    def __init__(self, approach_distance_m: float = 0.6, person_safety_distance_m: float = 1.2):
        self.state = RobotState.EXPLORE
        self.approach_distance_m = approach_distance_m
        self.person_safety_distance_m = person_safety_distance_m
        self.current_target: DetectedObject | None = None
        self.current_bin: str | None = None

    def handle(self, event: RobotEvent) -> RobotDecision:
        blocking_person = self._blocking_person(event.detections)
        if blocking_person is not None:
            self.state = RobotState.AVOID_BLOCKED
            return RobotDecision(
                state=self.state,
                command="stop_wait",
                target=blocking_person,
                reason="person_in_safety_zone",
            )

        if self.state == RobotState.PICK and event.gripper_has_object:
            self.state = RobotState.NAVIGATE_TO_BIN
            return RobotDecision(state=self.state, command="go_to_bin", target_bin=self.current_bin)

        if self.state == RobotState.NAVIGATE_TO_BIN and event.at_bin:
            self.state = RobotState.DROP
            return RobotDecision(state=self.state, command="open_gripper", target_bin=self.current_bin)

        if self.state == RobotState.DROP and event.drop_complete:
            self.current_target = None
            self.current_bin = None
            self.state = RobotState.EXPLORE
            return RobotDecision(state=self.state, command="explore")

        target = self._nearest_actionable_trash(event.detections)
        if target is None:
            self.state = RobotState.EXPLORE
            return RobotDecision(state=self.state, command="explore")

        self.current_target = target
        self.current_bin = target.container
        distance = target.position.distance() if target.position else float("inf")
        if distance <= self.approach_distance_m:
            self.state = RobotState.PICK
            return RobotDecision(state=self.state, command="close_gripper", target=target, target_bin=target.container)

        self.state = RobotState.TRACK_TRASH
        return RobotDecision(state=self.state, command="track_target", target=target, target_bin=target.container)

    def _blocking_person(self, detections: list[DetectedObject]) -> DetectedObject | None:
        for detection in detections:
            if detection.safety_class != SafetyClass.PERSON:
                continue
            if detection.position is None or detection.position.distance() <= self.person_safety_distance_m:
                return detection
        return None

    @staticmethod
    def _nearest_actionable_trash(detections: list[DetectedObject]) -> DetectedObject | None:
        candidates = [detection for detection in detections if detection.is_actionable_trash]
        if not candidates:
            return None
        return min(candidates, key=lambda detection: detection.position.distance())

