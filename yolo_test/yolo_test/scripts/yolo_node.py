#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
from ultralytics import YOLO


class YoloDetectorNode:
    def __init__(self):
        rospy.init_node("yolo_detector_node", anonymous=True)

        self.bridge = CvBridge()
        self.model_path = rospy.get_param("~model_path", "yolov8n.pt")
        self.model = YOLO(self.model_path)

        self.image_topic = rospy.get_param("~image_topic", "/camera/image")

        rospy.Subscriber(
            self.image_topic,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

        rospy.loginfo("YOLO detector node started")
        rospy.loginfo("Listening to: %s", self.image_topic)
        rospy.loginfo("Using model: %s", self.model_path)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            rospy.logerr("Error converting image: %s", e)
            return

        results = self.model(frame, verbose=False)
        annotated_frame = results[0].plot()

        cv2.imshow("YOLO detections", annotated_frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    try:
        node = YoloDetectorNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
