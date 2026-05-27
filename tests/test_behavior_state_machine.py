import unittest

from waste_robot_behavior.behavior import RobotEvent, RobotState, WasteBehaviorStateMachine
from waste_robot_behavior.detections import DetectedObject, Position3D
from waste_robot_behavior.taxonomy import SafetyClass


class BehaviorStateMachineTest(unittest.TestCase):
    def test_selects_nearest_actionable_trash_detection(self):
        machine = WasteBehaviorStateMachine()
        far = DetectedObject(
            label="paper",
            container="paper_cardboard",
            confidence=0.9,
            position=Position3D(x=1.0, y=0.0, z=2.0),
        )
        near = DetectedObject(
            label="plastic bottle",
            container="plastic_metal_carton",
            confidence=0.8,
            position=Position3D(x=0.2, y=0.0, z=0.8),
        )

        decision = machine.handle(RobotEvent(detections=[far, near]))

        self.assertEqual(decision.state, RobotState.TRACK_TRASH)
        self.assertEqual(decision.target, near)
        self.assertEqual(decision.command, "track_target")

    def test_person_detection_blocks_motion_before_trash_tracking(self):
        machine = WasteBehaviorStateMachine()
        person = DetectedObject(
            label="person",
            safety_class=SafetyClass.PERSON,
            confidence=0.95,
            position=Position3D(x=0.1, y=0.0, z=0.7),
        )
        trash = DetectedObject(
            label="glass bottle",
            container="glass",
            confidence=0.9,
            position=Position3D(x=0.2, y=0.0, z=1.0),
        )

        decision = machine.handle(RobotEvent(detections=[trash, person]))

        self.assertEqual(decision.state, RobotState.AVOID_BLOCKED)
        self.assertEqual(decision.command, "stop_wait")
        self.assertEqual(decision.reason, "person_in_safety_zone")

    def test_state_progresses_through_pick_and_drop_with_mock_results(self):
        machine = WasteBehaviorStateMachine(approach_distance_m=0.45)
        trash = DetectedObject(
            label="banana peel",
            container="organic",
            confidence=0.9,
            position=Position3D(x=0.0, y=0.0, z=0.4),
        )

        decision = machine.handle(RobotEvent(detections=[trash]))
        self.assertEqual(decision.state, RobotState.PICK)
        self.assertEqual(decision.command, "close_gripper")

        decision = machine.handle(RobotEvent(gripper_has_object=True))
        self.assertEqual(decision.state, RobotState.NAVIGATE_TO_BIN)
        self.assertEqual(decision.command, "go_to_bin")
        self.assertEqual(decision.target_bin, "organic")

        decision = machine.handle(RobotEvent(at_bin=True))
        self.assertEqual(decision.state, RobotState.DROP)
        self.assertEqual(decision.command, "open_gripper")

        decision = machine.handle(RobotEvent(drop_complete=True))
        self.assertEqual(decision.state, RobotState.EXPLORE)
        self.assertEqual(decision.command, "explore")


if __name__ == "__main__":
    unittest.main()
