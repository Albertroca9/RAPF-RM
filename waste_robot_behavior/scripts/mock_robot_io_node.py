#!/usr/bin/env python3
import json

import rospy
from std_msgs.msg import String


class MockRobotIoNode:
    def __init__(self):
        rospy.init_node("mock_robot_io_node", anonymous=False)
        self.feedback_pub = rospy.Publisher(rospy.get_param("~feedback_topic", "/waste_behavior_node/feedback"), String, queue_size=10)
        rospy.Subscriber(rospy.get_param("~decision_topic", "/waste_behavior_node/decision"), String, self._decision_cb)
        rospy.loginfo("Mock robot IO ready")

    def _decision_cb(self, msg):
        decision = json.loads(msg.data)
        command = decision.get("command")
        feedback = {}
        if command == "close_gripper":
            feedback["gripper_has_object"] = True
        elif command == "go_to_bin":
            feedback["at_bin"] = True
        elif command == "open_gripper":
            feedback["drop_complete"] = True
        if feedback:
            self.feedback_pub.publish(String(data=json.dumps(feedback)))


if __name__ == "__main__":
    try:
        MockRobotIoNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
