README - Arranque seguro TurtleBot3 Waffle + OpenMANIPULATOR-X + pinza
======================================================================

Objetivo
--------
Dejar por escrito el procedimiento que HA FUNCIONADO para arrancar el robot,
mantener cámara y láser activos, y poder abrir/cerrar la pinza.

Idea importante
---------------
NO hay que tocar configuraciones permanentes si no hace falta.
NO editar ~/.bashrc automáticamente.
NO ejecutar scripts de instalación enteros si el entorno ya está preparado.
NO hacer sudo apt upgrade.
NO flashear OpenCR cada vez.

El firmware de OpenCR, una vez subido correctamente, debería quedarse guardado
en la placa. Por tanto, normalmente cada sesión solo hay que repetir los sources,
exports y roslaunch. Solo habría que volver a actualizar firmware si el robot vuelve
a comportarse como TurtleBot3 Waffle normal y deja de escuchar /gripper_position.

IPs usadas en la sesión que funcionó
------------------------------------
Remote PC / ordenador laboratorio:
  10.10.73.179

Robot / Raspberry / SBC:
  10.10.73.222

ROS master:
  http://10.10.73.179:11311

Si otro día cambian las IPs, hay que sustituirlas en los comandos.

======================================================================
1. Arranque normal de cada sesión
======================================================================

TERMINAL 1 - Remote PC: roscore
-------------------------------
En el ordenador del laboratorio:

  source /opt/ros/noetic/setup.bash
  source ~/catkin_ws/devel/setup.bash
  export TURTLEBOT3_MODEL=waffle
  export ROS_MASTER_URI=http://10.10.73.179:11311
  export ROS_IP=10.10.73.179
  roscore

Dejar esta terminal abierta.


TERMINAL 2 - Robot/SBC: TurtleBot3 base, cámara y láser
-------------------------------------------------------
En el robot, usuario ubuntu:

  source ~/.bashrc
  source /opt/ros/noetic/setup.bash
  export TURTLEBOT3_MODEL=waffle
  export ROS_MASTER_URI=http://10.10.73.179:11311
  export ROS_IP=10.10.73.222
  roslaunch turtlebot3_bringup turtlebot3_robot.launch

Esto levanta:
  - turtlebot3_core
  - láser /scan
  - cámara /camera/image o similar
  - odometría /odom
  - ruedas /joint_states

Dejar esta terminal abierta.

Si alguna vez no encuentra turtlebot3_bringup después de hacer source /opt/ros/noetic/setup.bash,
probar:

  source ~/.bashrc

O buscar el workspace correcto:

  find ~ -name setup.bash | grep devel

Y hacer source del setup.bash que corresponda.


TERMINAL 3 - Remote PC: bringup del OpenMANIPULATOR
---------------------------------------------------
En el ordenador del laboratorio:

  source /opt/ros/noetic/setup.bash
  source ~/catkin_ws/devel/setup.bash
  export TURTLEBOT3_MODEL=waffle
  export ROS_MASTER_URI=http://10.10.73.179:11311
  export ROS_IP=10.10.73.179
  roslaunch turtlebot3_manipulation_bringup turtlebot3_manipulation_bringup.launch

Dejar esta terminal abierta.

Este nodo crea/controla topics como:
  - /arm_controller/follow_joint_trajectory/goal
  - /gripper_controller/follow_joint_trajectory/goal
  - /joint_trajectory_point
  - /gripper_position


TERMINAL 4 - Remote PC: MoveIt, si hace falta
---------------------------------------------
Solo si se va a usar MoveIt o GUI del manipulador.

En el ordenador del laboratorio:

  source /opt/ros/noetic/setup.bash
  source ~/catkin_ws/devel/setup.bash
  export TURTLEBOT3_MODEL=waffle
  export ROS_MASTER_URI=http://10.10.73.179:11311
  export ROS_IP=10.10.73.179
  export LD_LIBRARY_PATH=/opt/ros/noetic/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
  roslaunch turtlebot3_manipulation_moveit_config move_group.launch

Importante:
  El export LD_LIBRARY_PATH se pone manualmente en esta terminal para evitar errores con libfcl.so.0.6.
  No hace falta ponerlo permanente en ~/.bashrc.


TERMINAL 5 - Remote PC: GUI, si hace falta
------------------------------------------
Solo si se usa la GUI.

  source /opt/ros/noetic/setup.bash
  source ~/catkin_ws/devel/setup.bash
  export TURTLEBOT3_MODEL=waffle
  export ROS_MASTER_URI=http://10.10.73.179:11311
  export ROS_IP=10.10.73.179
  export LD_LIBRARY_PATH=/opt/ros/noetic/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
  roslaunch turtlebot3_manipulation_gui turtlebot3_manipulation_gui.launch

======================================================================
2. Comprobaciones antes de mover la pinza
======================================================================

En el Remote PC:

  rostopic info /gripper_position

Tiene que aparecer algo parecido a:

  Publishers:
   * /turtlebot3_manipulation_bringup

  Subscribers:
   * /turtlebot3_core

También comprobar:

  rostopic info /joint_trajectory_point

Tiene que aparecer como subscriber /turtlebot3_core.

Si /gripper_position o /joint_trajectory_point tienen:

  Subscribers: None

entonces el robot NO está escuchando órdenes de pinza/brazo. En ese caso, no tiene sentido insistir con comandos de abrir/cerrar: primero hay que revisar firmware/conexión/bringup.

======================================================================
3. Mover pinza directamente, sin paquete propio
======================================================================

Cuando /gripper_position tenga subscriber /turtlebot3_core, se puede probar:

Abrir/cambiar posición:

  rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [0.010]"

Cerrar/cambiar posición:

  rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [-0.010]"

Otra posición segura:

  rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [0.000]"

Valores seguros para probar:

  -0.015
  -0.010
  -0.005
   0.000
   0.005
   0.010
   0.015

No usar valores grandes tipo 1.0 o -1.0.

======================================================================
4. Crear paquete/nodo temporal para abrir/cerrar pinza
======================================================================

Esto se hace en el Remote PC. No toca el robot.
Solo crea un paquete dentro de ~/catkin_ws/src.

Crear paquete:

  source /opt/ros/noetic/setup.bash
  source ~/catkin_ws/devel/setup.bash
  export TURTLEBOT3_MODEL=waffle
  cd ~/catkin_ws/src
  catkin_create_pkg waffle_gripper_control rospy actionlib control_msgs trajectory_msgs
  cd waffle_gripper_control
  mkdir -p scripts
  nano scripts/gripper_cmd.py

Contenido de scripts/gripper_cmd.py:

#!/usr/bin/env python3

import sys
import rospy
import actionlib

from control_msgs.msg import FollowJointTrajectoryAction
from control_msgs.msg import FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectoryPoint


class GripperCommander:
    def __init__(self):
        rospy.init_node("waffle_gripper_commander")

        self.action_name = rospy.get_param(
            "~action_name",
            "/gripper_controller/follow_joint_trajectory"
        )

        self.joint_name = rospy.get_param("~joint_name", "gripper")
        self.open_position = rospy.get_param("~open_position", 0.010)
        self.close_position = rospy.get_param("~close_position", -0.010)
        self.duration = rospy.get_param("~duration", 1.0)

        rospy.loginfo("Action server: %s", self.action_name)
        rospy.loginfo("Joint de la pinza: %s", self.joint_name)

        self.client = actionlib.SimpleActionClient(
            self.action_name,
            FollowJointTrajectoryAction
        )

        rospy.loginfo("Esperando al controlador de la pinza...")

        if not self.client.wait_for_server(rospy.Duration(5.0)):
            rospy.logerr("No se encontró el action server de la pinza.")
            rospy.logerr("Comprueba: rostopic list | grep gripper")
            rospy.signal_shutdown("Sin action server")
            return

        rospy.loginfo("Controlador de pinza encontrado.")

    def send_position(self, position):
        goal = FollowJointTrajectoryGoal()
        goal.trajectory.header.stamp = rospy.Time.now()
        goal.trajectory.joint_names = [self.joint_name]

        point = JointTrajectoryPoint()
        point.positions = [position]
        point.velocities = [0.0]
        point.time_from_start = rospy.Duration(self.duration)

        goal.trajectory.points = [point]

        rospy.loginfo("Enviando posición %.4f a la pinza...", position)
        self.client.send_goal(goal)

        finished = self.client.wait_for_result(
            rospy.Duration(self.duration + 2.0)
        )

        if finished:
            rospy.loginfo("Movimiento enviado y finalizado.")
        else:
            rospy.logwarn("No se recibió resultado dentro del tiempo esperado.")

    def open(self):
        self.send_position(self.open_position)

    def close(self):
        self.send_position(self.close_position)


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  rosrun waffle_gripper_control gripper_cmd.py open")
        print("  rosrun waffle_gripper_control gripper_cmd.py close")
        print("  rosrun waffle_gripper_control gripper_cmd.py pos 0.005")
        return

    commander = GripperCommander()
    command = sys.argv[1].lower()

    if command == "open":
        commander.open()

    elif command == "close":
        commander.close()

    elif command == "pos":
        if len(sys.argv) < 3:
            rospy.logerr("Falta posición. Ejemplo: pos 0.005")
            return

        try:
            position = float(sys.argv[2])
        except ValueError:
            rospy.logerr("La posición debe ser un número.")
            return

        commander.send_position(position)

    else:
        rospy.logerr("Comando no reconocido. Usa open, close o pos.")


if __name__ == "__main__":
    main()

Guardar y dar permisos:

  chmod +x scripts/gripper_cmd.py

Compilar:

  cd ~/catkin_ws
  catkin_make
  source devel/setup.bash

Usar:

  rosrun waffle_gripper_control gripper_cmd.py open
  rosrun waffle_gripper_control gripper_cmd.py close
  rosrun waffle_gripper_control gripper_cmd.py pos 0.010
  rosrun waffle_gripper_control gripper_cmd.py pos -0.010

Si los valores open/close quedan invertidos, usar pos manualmente y cambiar open_position/close_position en el comando:

  rosrun waffle_gripper_control gripper_cmd.py open _open_position:=0.015
  rosrun waffle_gripper_control gripper_cmd.py close _close_position:=-0.015

======================================================================
5. Firmware OpenCR: SOLO si vuelve a no funcionar la pinza
======================================================================

NO repetir esto cada sesión.
El firmware queda guardado en la OpenCR.

Solo plantear este paso si ocurre otra vez esto:

  rostopic info /gripper_position

muestra:

  Subscribers: None

Y además turtlebot3_core solo se comporta como Waffle normal.

En ese caso, el firmware que funcionó para TurtleBot3 Waffle + OpenMANIPULATOR-X en ROS Noetic fue:

  om_with_tb3_noetic

Comandos manuales en el robot/SBC:

  cd ~
  export OPENCR_PORT=/dev/ttyACM0
  export OPENCR_MODEL=om_with_tb3_noetic
  rm -rf ./opencr_update ./opencr_update.tar.bz2
  wget https://github.com/ROBOTIS-GIT/OpenCR-Binaries/raw/master/turtlebot3/ROS1/latest/opencr_update.tar.bz2
  tar -xvf opencr_update.tar.bz2
  cd ./opencr_update

Antes del update:
  - Dejar el brazo libre.
  - No poner dedos cerca de la pinza.
  - No cortar alimentación.
  - No desconectar USB.
  - Confirmar que OpenCR está en /dev/ttyACM0.

Actualizar:

  ./update.sh $OPENCR_PORT $OPENCR_MODEL.opencr

Después, relanzar:

  roslaunch turtlebot3_bringup turtlebot3_robot.launch

Y comprobar:

  rostopic info /gripper_position

Debe aparecer:

  Subscribers:
   * /turtlebot3_core

======================================================================
6. Diagnóstico rápido de fallos
======================================================================

Ver si cámara existe:

  rostopic list | grep camera

Ver si láser existe:

  rostopic list | grep scan
  rostopic hz /scan

Ver si pinza escucha:

  rostopic info /gripper_position

Ver si brazo/controladores existen:

  rostopic list | grep -E "gripper|arm|joint_trajectory"

Ver joint states:

  rostopic echo -n 1 /joint_states

Si /joint_states solo muestra ruedas, pero /gripper_position tiene subscriber /turtlebot3_core,
la pinza puede funcionar igualmente por /gripper_position.

Si /gripper_position no tiene subscriber, la pinza no se moverá por ROS.

======================================================================
7. Recordatorio final
======================================================================

Proceso normal cada sesión:
  1. roscore en PC.
  2. turtlebot3_robot.launch en robot.
  3. turtlebot3_manipulation_bringup.launch en PC.
  4. Comprobar /gripper_position.
  5. Mover pinza con rostopic pub o con gripper_cmd.py.
  6. Lanzar MoveIt/GUI solo si hace falta.

No repetir firmware si ya funciona.
No tocar ~/.bashrc si no hace falta.
No ejecutar el script grande de instalación salvo que el PC esté borrado y haya que reinstalar todo desde cero.
