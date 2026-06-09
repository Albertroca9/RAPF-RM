#!/usr/bin/env python3
import json

import cv2
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import String
from ultralytics import YOLO

from waste_robot_behavior.detections import DetectedObject
from waste_robot_behavior.geometry import BoundingBox, CameraIntrinsics, DepthEstimator
from waste_robot_behavior.taxonomy import DetectionClassMapper, SafetyClass


class YoloRgbdDetectorNode:
    def __init__(self):
        rospy.init_node("yolo_rgbd_detector_node", anonymous=False)
        self.bridge = CvBridge()
        self.mapper = DetectionClassMapper.default()
        self.model = YOLO(rospy.get_param("~model_path", "yolov8n.pt"))
        self.confidence_threshold = float(rospy.get_param("~confidence_threshold", 0.45))
        self.depth_scale = float(rospy.get_param("~depth_scale", 1.0))
        self.depth_image = None
        self.intrinsics = None

        self.publisher = rospy.Publisher("~detections", String, queue_size=10)
        rospy.Subscriber(rospy.get_param("~camera_info_topic", "/camera/camera_info"), CameraInfo, self._camera_info_cb)
        rospy.Subscriber(rospy.get_param("~depth_topic", "/camera/depth/image_raw"), Image, self._depth_cb, queue_size=1)
        rospy.Subscriber(rospy.get_param("~image_topic", "/camera/image"), Image, self._image_cb, queue_size=1, buff_size=2**24)

        rospy.loginfo("YOLO RGB-D detector ready")

    def _camera_info_cb(self, msg):
        self.intrinsics = CameraIntrinsics(fx=msg.K[0], fy=msg.K[4], cx=msg.K[2], cy=msg.K[5])

    def _depth_cb(self, msg):
        depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        self.depth_image = depth * self.depth_scale

    def _image_cb(self, msg):
        if self.depth_image is None or self.intrinsics is None:
            return
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        estimator = DepthEstimator(self.intrinsics)
        payload = []
        for result in self.model(frame, verbose=False):
            for box in result.boxes:
                confidence = float(box.conf[0])
                if confidence < self.confidence_threshold:
                    continue
                class_id = int(box.cls[0])
                label = result.names[class_id]
                xyxy = box.xyxy[0].tolist()
                bbox = BoundingBox(xmin=int(xyxy[0]), ymin=int(xyxy[1]), xmax=int(xyxy[2]), ymax=int(xyxy[3]))
                position = estimator.estimate(bbox, self.depth_image)
                payload.append(self._serialize_detection(label, confidence, position))
        self.publisher.publish(String(data=json.dumps(payload)))

    def _serialize_detection(self, label, confidence, position):
        container = self.mapper.map_runtime_container(label)
        if container is not None:
            detection = DetectedObject(label=label, confidence=confidence, container=container, position=position)
        else:
            detection = DetectedObject(
                label=label,
                confidence=confidence,
                safety_class=self.mapper.map_non_waste_label(label),
                position=position,
            )
        return {
            "label": detection.label,
            "confidence": detection.confidence,
            "container": detection.container,
            "safety_class": detection.safety_class.value if isinstance(detection.safety_class, SafetyClass) else None,
            "position": None if detection.position is None else detection.position.__dict__,
        }


if __name__ == "__main__":
    try:
        YoloRgbdDetectorNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
