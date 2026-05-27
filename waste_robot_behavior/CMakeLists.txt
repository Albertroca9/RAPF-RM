cmake_minimum_required(VERSION 3.0.2)
project(waste_robot_behavior)

find_package(catkin REQUIRED COMPONENTS
  cv_bridge
  geometry_msgs
  rospy
  sensor_msgs
  std_msgs
)

catkin_python_setup()

catkin_package()

catkin_install_python(PROGRAMS
  scripts/mock_robot_io_node.py
  scripts/waste_behavior_node.py
  scripts/yolo_rgbd_detector_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
