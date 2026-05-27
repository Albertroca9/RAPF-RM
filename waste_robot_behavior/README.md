# waste_robot_behavior

ROS1 Noetic package for the TurtleBot3 Waffle waste-pickup behavior.

The package separates the project into testable Python logic and thin ROS nodes:

- `yolo_rgbd_detector_node.py`: RGB image + depth + camera info to JSON detections.
- `waste_behavior_node.py`: detections + mock feedback to high-level robot decisions.
- `mock_robot_io_node.py`: simulates gripper/navigation feedback for local behavior tests.
- `dataset/taco_to_yolo.py`: converts TACO COCO annotations into YOLO labels with the five project bins.

## Five Container Classes

The model-facing classes are:

1. `paper_cardboard`
2. `plastic_metal_carton`
3. `glass`
4. `organic`
5. `residual`

Objects not mapped to waste are not pickup targets. `person` is handled as a safety stop condition.

## Dataset Conversion

Download TACO annotations from the official dataset tooling, then run:

```bash
python3 -m waste_robot_behavior.dataset.taco_to_yolo \
  /path/to/TACO/data/annotations.json \
  /path/to/output/labels \
  --data-yaml /path/to/output/data.yaml
```

The generated YOLO labels use the class order from `config/yolo_data.yaml`.

## ROS Launch With Mocks

After adding this package to `~/catkin_ws/src` and building:

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
roslaunch waste_robot_behavior waste_behavior_mock.launch \
  image_topic:=/camera/image \
  depth_topic:=/camera/depth/image_raw \
  camera_info_topic:=/camera/camera_info \
  model_path:=/path/to/best.pt
```

The behavior output is published as JSON on:

```text
/waste_behavior_node/decision
```

The detector output is published as JSON on:

```text
/yolo_rgbd_detector_node/detections
```

This first integration does not command `move_base` or OpenMANIPULATOR directly. The mock node exists so the state machine can be tested while SLAM/navigation and gripper control are developed in parallel.
