cmake_minimum_required(VERSION 3.0.2)
project(recycling_world)

find_package(catkin REQUIRED)

catkin_package()

# Instal·la tots els directoris del paquet
install(DIRECTORY launch worlds rviz maps
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  OPTIONAL
)
