#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
from ultralytics import YOLO

COCO_CLASS_TO_CONTAINER = {
    "book": "paper",
    "bottle": "plastic",
    "wine glass": "glass",
    "apple": "residual",
    "banana": "residual",
    "broccoli": "residual",
    "cake": "residual",
    "carrot": "residual",
    "donut": "residual",
    "hot dog": "residual",
    "orange": "residual",
    "pizza": "residual",
    "sandwich": "residual",
}


class YoloDetectorNode:
    def __init__(self):
        rospy.init_node("yolo_detector_node", anonymous=True)

        self.bridge = CvBridge()
        self.model_path = rospy.get_param("~model_path", "yolov8n.pt")
        self.model = YOLO(self.model_path)
        self.confidence_threshold = float(rospy.get_param("~confidence_threshold", 0.25))

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
        rospy.loginfo("Confidence threshold: %.2f", self.confidence_threshold)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            rospy.logerr("Error converting image: %s", e)
            return

        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        annotated_frame = results[0].plot()
        self._draw_container_mapping(annotated_frame, results[0])

        cv2.imshow("YOLO detections", annotated_frame)
        cv2.waitKey(1)

    def _draw_container_mapping(self, frame, result):
        rows = []
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = result.names[class_id]
            container = COCO_CLASS_TO_CONTAINER.get(label)
            if container is not None:
                rows.append(f"{label} -> {container}")

        for index, row in enumerate(rows[:8]):
            y = 28 + (index * 24)
            cv2.putText(frame, row, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


if __name__ == "__main__":
    try:
        node = YoloDetectorNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
