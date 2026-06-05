README - Firmware OpenCR para TurtleBot3 Waffle + OpenMANIPULATOR-X
=======================================================================

OBJETIVO
--------
Este TXT sirve SOLO por si cambias de TurtleBot3 Waffle o si vuelve a pasar que la pinza no se mueve
porque el robot no escucha los topics del manipulador.

NO hay que repetir este proceso cada sesión si la pinza ya funciona.

El firmware se graba en la placa OpenCR del robot. No es como hacer 'source' o 'export':
queda guardado aunque apagues el robot, cierres terminales o reinicies.


CUANDO NO TOCAR FIRMWARE
------------------------
NO subas firmware si al comprobar:

    rostopic info /gripper_position

sale algo parecido a:

    Subscribers:
     * /turtlebot3_core

En ese caso, el robot ya escucha la pinza. Solo tienes que lanzar los nodos normales.


CUANDO PUEDE HACER FALTA
------------------------
Puede hacer falta subir firmware si:

1. Cambias de Waffle.
2. Otro grupo/profesor ha dejado la OpenCR con firmware de TurtleBot3 Waffle normal.
3. La base, cámara y láser funcionan, pero la pinza no se mueve.
4. Al mirar:

       rostopic info /gripper_position

   sale:

       Subscribers: None

5. También puede fallar:

       rostopic info /joint_trajectory_point

   y salir:

       Subscribers: None

Eso significa que el PC genera órdenes para brazo/pinza, pero el robot no las escucha.


SINTOMA QUE TUVIMOS
-------------------
Antes de arreglarlo, pasaba esto:

    /gripper_position
    Publishers:
     * /turtlebot3_manipulation_bringup
    Subscribers: None

Y también:

    /joint_trajectory_point
    Publishers:
     * /turtlebot3_manipulation_bringup
    Subscribers: None

Con eso, aunque ejecutes comandos de abrir/cerrar pinza, la pinza no se mueve porque la OpenCR no está escuchando esos topics.


QUE HACE ESTE PROCESO
---------------------
Este proceso cambia el firmware de la placa OpenCR.

El firmware correcto para TurtleBot3 Waffle + OpenMANIPULATOR-X en ROS Noetic es:

    om_with_tb3_noetic

Esto hace que el nodo /turtlebot3_core del robot escuche también los topics del manipulador:

    /gripper_position
    /joint_trajectory_point

Después de hacerlo bien, la pinza puede abrir/cerrar.


IMPORTANTE - RIESGOS
--------------------
Esto SI toca el robot.

No es instalar un paquete en Ubuntu. Es actualizar el firmware de la OpenCR.

Riesgos:
- No cortar alimentación durante el update.
- No desconectar USB/OpenCR durante el update.
- No usar un modelo de firmware equivocado.
- Dejar el brazo/pinza libre, sin dedos cerca, porque puede moverse al reiniciar.
- Hacerlo solo si realmente el subscriber no aparece.

Si el robot ya funciona, NO repetir por rutina.


PASOS PARA SUBIR FIRMWARE
=========================

0. Antes de empezar
-------------------
Para los launches que estén corriendo:

En el PC:
    CTRL + C en turtlebot3_manipulation_bringup
    CTRL + C en move_group si estaba abierto
    CTRL + C en la GUI si estaba abierta

En el robot:
    CTRL + C en turtlebot3_robot.launch

Deja la pinza y el brazo libres, sin objetos ni dedos cerca.


1. En el robot/SBC
------------------
Estos comandos se hacen en el robot, normalmente en la terminal:

    ubuntu@ubuntu:~$

Comprobar OpenCR:

    ls -l /dev/ttyACM0

Debe salir algo como:

    /dev/ttyACM0


2. Configurar variables manualmente
-----------------------------------
Ejecutar uno por uno:

    cd ~

    export OPENCR_PORT=/dev/ttyACM0

    export OPENCR_MODEL=om_with_tb3_noetic


3. Descargar firmware oficial
-----------------------------
Ejecutar:

    rm -rf ./opencr_update ./opencr_update.tar.bz2

    wget https://github.com/ROBOTIS-GIT/OpenCR-Binaries/raw/master/turtlebot3/ROS1/latest/opencr_update.tar.bz2

    tar -xvf opencr_update.tar.bz2

    cd ./opencr_update


4. Subir firmware a OpenCR
--------------------------
IMPORTANTE: antes de este comando, brazo y pinza libres.

Ejecutar:

    ./update.sh $OPENCR_PORT $OPENCR_MODEL.opencr

Esperar a que acabe. No desconectar nada durante el proceso.

Debe terminar sin errores. Puede salir algo parecido a:

    jump_to_fw


5. Relanzar robot
=================

En el robot/SBC:

    source ~/.bashrc
    export TURTLEBOT3_MODEL=waffle
    export ROS_MASTER_URI=http://IP_DEL_PC:11311
    export ROS_IP=IP_DEL_ROBOT

Ejemplo usado en laboratorio:

    export ROS_MASTER_URI=http://10.10.73.179:11311
    export ROS_IP=10.10.73.222

Luego:

    roslaunch turtlebot3_bringup turtlebot3_robot.launch


6. Relanzar bringup del manipulador en el PC
--------------------------------------------
En el PC:

    source /opt/ros/noetic/setup.bash
    source ~/catkin_ws/devel/setup.bash
    export TURTLEBOT3_MODEL=waffle

Si usas IPs manuales:

    export ROS_MASTER_URI=http://IP_DEL_PC:11311
    export ROS_IP=IP_DEL_PC

Ejemplo:

    export ROS_MASTER_URI=http://10.10.73.179:11311
    export ROS_IP=10.10.73.179

Luego:

    roslaunch turtlebot3_manipulation_bringup turtlebot3_manipulation_bringup.launch


7. Comprobacion clave
=====================

En el PC:

    rostopic info /gripper_position

Tiene que salir:

    Subscribers:
     * /turtlebot3_core

Y también:

    rostopic info /joint_trajectory_point

Tiene que salir:

    Subscribers:
     * /turtlebot3_core


8. Probar pinza
===============

Prueba directa:

    rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [0.010]"

Luego:

    rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [-0.010]"

También puedes probar:

    rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [0.015]"

    rostopic pub -1 /gripper_position std_msgs/Float64MultiArray "data: [-0.015]"

No uses valores grandes tipo 1.0 o -1.0.


9. Regla final
==============
Si /gripper_position tiene subscriber /turtlebot3_core, NO tocar firmware.

Si /gripper_position sale con Subscribers: None, y la base/cámara/láser funcionan,
entonces probablemente esa Waffle no tiene cargado el firmware de manipulación.

En ese caso, repetir este TXT manualmente.
