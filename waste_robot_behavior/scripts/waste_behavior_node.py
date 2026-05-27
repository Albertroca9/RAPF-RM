#!/usr/bin/env python3
import json

import rospy
from std_msgs.msg import String

from waste_robot_behavior.behavior import RobotEvent, WasteBehaviorStateMachine
from waste_robot_behavior.detections import DetectedObject, Position3D
from waste_robot_behavior.taxonomy import SafetyClass


class WasteBehaviorNode:
    def __init__(self):
        rospy.init_node("waste_behavior_node", anonymous=False)
        self.machine = WasteBehaviorStateMachine(
            approach_distance_m=float(rospy.get_param("~approach_distance_m", 0.6)),
            person_safety_distance_m=float(rospy.get_param("~person_safety_distance_m", 1.2)),
        )
        self.last_detections = []
        self.publisher = rospy.Publisher("~decision", String, queue_size=10)
        rospy.Subscriber(rospy.get_param("~detections_topic", "/yolo_rgbd_detector_node/detections"), String, self._detections_cb)
        rospy.Subscriber(rospy.get_param("~feedback_topic", "~feedback"), String, self._feedback_cb)
        rospy.loginfo("Waste behavior state machine ready")

    def _detections_cb(self, msg):
        self.last_detections = [_parse_detection(item) for item in json.loads(msg.data)]
        self._publish_decision(RobotEvent(detections=self.last_detections))

    def _feedback_cb(self, msg):
        feedback = json.loads(msg.data)
        self._publish_decision(
            RobotEvent(
                detections=self.last_detections,
                gripper_has_object=bool(feedback.get("gripper_has_object", False)),
                at_bin=bool(feedback.get("at_bin", False)),
                drop_complete=bool(feedback.get("drop_complete", False)),
            )
        )

    def _publish_decision(self, event):
        decision = self.machine.handle(event)
        self.publisher.publish(String(data=json.dumps(_decision_to_dict(decision))))


def _parse_detection(item):
    position_data = item.get("position")
    position = None if position_data is None else Position3D(**position_data)
    safety_class = item.get("safety_class")
    return DetectedObject(
        label=item["label"],
        confidence=float(item["confidence"]),
        container=item.get("container"),
        safety_class=None if safety_class is None else SafetyClass(safety_class),
        position=position,
    )


def _decision_to_dict(decision):
    return {
        "state": decision.state.value,
        "command": decision.command,
        "target_bin": decision.target_bin,
        "reason": decision.reason,
        "target": None
        if decision.target is None
        else {
            "label": decision.target.label,
            "confidence": decision.target.confidence,
            "container": decision.target.container,
            "safety_class": decision.target.safety_class.value if decision.target.safety_class else None,
            "position": None if decision.target.position is None else decision.target.position.__dict__,
        },
    }


if __name__ == "__main__":
    try:
        WasteBehaviorNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
