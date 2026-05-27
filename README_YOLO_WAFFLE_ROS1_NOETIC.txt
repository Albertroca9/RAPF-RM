README - Prueba de YOLOv8n con cámara del Waffle en ROS Noetic
================================================================

Objetivo
--------
Este documento explica cómo replicar desde cero la prueba básica de YOLO con el robot Waffle/TurtleBot usando ROS1 Noetic.

La idea es:

    Robot/Waffle publica la cámara en ROS
            ↓
    Ordenador del laboratorio recibe /camera/image
            ↓
    Ordenador ejecuta YOLOv8n
            ↓
    Se abre una ventana con detecciones en tiempo real

De momento esto solo sirve para probar si YOLO detecta objetos correctamente. No incluye todavía navegación, pinza, basura ni clasificación por contenedor.


Datos importantes del entorno
-----------------------------
Robot/Waffle / ROS master:

    10.10.73.229

Ordenador del laboratorio:

    El que tenga el usuario actual, por ejemplo:
    alumne@c5s203pc202

ROS usado:

    ROS1 Noetic

Tópico de cámara usado:

    /camera/image

Modelo YOLO usado:

    yolov8n.pt

Importante:

    YOLO se ejecuta en el ordenador del laboratorio, no en el robot.
    El robot solamente publica la imagen de la cámara.


1. Abrir una terminal nueva y configurar ROS
--------------------------------------------
Ejecutar en el ordenador del laboratorio:

    source /opt/ros/noetic/setup.bash
    export ROS_MASTER_URI=http://10.10.73.229:11311
    export ROS_IP=$(hostname -I | awk '{print $1}')
    unset ROS_HOSTNAME

Comprobar configuración:

    echo $ROS_MASTER_URI
    echo $ROS_IP
    echo $ROS_HOSTNAME

Resultado esperado:

    http://10.10.73.229:11311
    10.10.73.xxx

La tercera línea, la de ROS_HOSTNAME, debería quedar vacía.

Notas importantes:

    ROS_MASTER_URI debe apuntar al robot.
    ROS_IP debe ser la IP del ordenador, no la del robot.
    No usar ROS_HOSTNAME=localhost si el robot está en otra máquina.


2. Comprobar que el ordenador ve los tópicos del robot
------------------------------------------------------
Ejecutar:

    rostopic list

Filtrar los tópicos de cámara:

    rostopic list | grep camera

Deberían aparecer tópicos parecidos a estos:

    /camera/camera_info
    /camera/image
    /camera/image/compressed

Comprobar el tipo del tópico de imagen:

    rostopic type /camera/image

Resultado esperado:

    sensor_msgs/Image

Comprobar frecuencia de imagen:

    rostopic hz /camera/image

Si imprime una frecuencia media, la imagen está llegando correctamente.


3. Comprobar visualmente la cámara
----------------------------------
Ejecutar:

    rqt_image_view

Seleccionar el tópico:

    /camera/image

Si se ve la imagen de la cámara del robot, la parte de red/cámara está bien.

No continuar con YOLO hasta que esto funcione.


4. Crear el workspace y el paquete desde cero
---------------------------------------------
Ejecutar:

    cd ~
    mkdir -p catkin_ws/src
    cd ~/catkin_ws/src
    catkin_create_pkg yolo_test rospy sensor_msgs cv_bridge std_msgs

Crear la carpeta de scripts:

    cd ~/catkin_ws/src/yolo_test
    mkdir -p scripts
    cd scripts
    touch yolo_node.py
    chmod +x yolo_node.py

La estructura debería quedar así:

    ~/catkin_ws/
    └── src/
        └── yolo_test/
            ├── CMakeLists.txt
            ├── package.xml
            └── scripts/
                └── yolo_node.py


5. Instalar dependencias de Python
----------------------------------
Primero instalar pip si no está instalado:

    sudo apt update
    sudo apt install python3-pip -y

Si apt da un error 404 al instalar paquetes, ejecutar primero:

    sudo apt update

Y volver a probar:

    sudo apt install python3-pip -y

Instalar Ultralytics YOLO y OpenCV:

    python3 -m pip install --user -U ultralytics opencv-python

Comprobar que YOLO funciona:

    python3 -c "from ultralytics import YOLO; print('YOLO funciona')"

Resultado esperado:

    YOLO funciona

Si aparece este error:

    ModuleNotFoundError: No module named 'ultralytics'

significa que falta instalar Ultralytics o que se ha instalado en otro Python.
Volver a ejecutar:

    python3 -m pip install --user -U ultralytics opencv-python


6. Crear el nodo YOLO
---------------------
Abrir el archivo:

    nano ~/catkin_ws/src/yolo_test/scripts/yolo_node.py

Pegar este código completo:

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
        self.model = YOLO("yolov8n.pt")

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

Guardar en nano:

    CTRL + O
    ENTER
    CTRL + X

Asegurar permisos de ejecución:

    chmod +x ~/catkin_ws/src/yolo_test/scripts/yolo_node.py

Importante:

    La primera línea del archivo debe ser exactamente:

        #!/usr/bin/env python3

    No puede haber líneas en blanco ni espacios antes de esa línea.


7. Compilar el workspace
------------------------
Ejecutar:

    cd ~/catkin_ws
    catkin_make
    source devel/setup.bash

Si no hay errores, el paquete ya está listo.


8. Ejecutar YOLO con la cámara del robot
----------------------------------------
Antes de lanzar el nodo, configurar de nuevo la red por si la terminal es nueva:

    source /opt/ros/noetic/setup.bash
    source ~/catkin_ws/devel/setup.bash
    export ROS_MASTER_URI=http://10.10.73.229:11311
    export ROS_IP=$(hostname -I | awk '{print $1}')
    unset ROS_HOSTNAME

Ejecutar el nodo:

    rosrun yolo_test yolo_node.py _image_topic:=/camera/image

La primera vez puede aparecer algo como:

    Downloading yolov8n.pt...

Eso es normal. El modelo se descarga automáticamente.

Resultado esperado en terminal:

    [INFO] YOLO detector node started
    [INFO] Listening to: /camera/image

También debería abrirse una ventana llamada:

    YOLO detections

En esa ventana se ve la imagen de la cámara del robot con cajas de detección.


9. Objetos recomendados para probar
-----------------------------------
Para comprobar que YOLO detecta bien, usar objetos que el modelo preentrenado ya conoce:

    persona
    botella
    silla
    mochila
    móvil
    libro
    taza
    plátano
    manzana
    naranja

No probar todavía residuos raros, porque yolov8n.pt está preentrenado para detectar objetos generales, no categorías específicas de basura.

Ejemplos de detecciones esperadas:

    person 0.85
    bottle 0.72
    chair 0.66
    cell phone 0.58


10. Qué significa yolov8n.pt
----------------------------
yolov8n.pt es un modelo YOLOv8 nano.

Eso significa:

    Es ligero.
    Está preentrenado.
    Ya detecta objetos generales.
    No está especializado en residuos.

No significa que sea un zip comprimido. La n significa nano, una versión pequeña del modelo.

Para el proyecto de basura, la idea futura será:

    YOLO detecta el objeto
            ↓
    Otro nodo o función decide el contenedor
            ↓
    El robot navega hacia el contenedor correspondiente

Ejemplo futuro:

    bottle  -> contenedor amarillo o verde, según color/material
    banana  -> orgánico
    book    -> azul


11. Problemas frecuentes
------------------------

Problema 1: no aparece /camera/image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprobar:

    rostopic list | grep camera

Si no aparece nada, el nodo de cámara del robot no está lanzado o no se está conectado al ROS master correcto.

Comprobar:

    echo $ROS_MASTER_URI

Debe ser:

    http://10.10.73.229:11311


Problema 2: se ve cámara en rqt_image_view pero YOLO no abre ventana
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprobar que se ejecuta desde una sesión gráfica, no desde SSH sin display:

    echo $DISPLAY

Si no sale nada, OpenCV no podrá abrir cv2.imshow().


Problema 3: warning de localhost
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Si aparece:

    attempted to connect to non-local host [...] from a node launched with ROS_HOSTNAME=localhost

Ejecutar:

    unset ROS_HOSTNAME
    export ROS_IP=$(hostname -I | awk '{print $1}')

Y volver a lanzar el nodo:

    rosrun yolo_test yolo_node.py _image_topic:=/camera/image

Si ROS_HOSTNAME=localhost está guardado en algún archivo, buscarlo con:

    grep -R "ROS_HOSTNAME\|ROS_IP\|ROS_MASTER_URI" ~/.bashrc ~/.profile ~/.bash_aliases ~/.zshrc 2>/dev/null

Normalmente estará en:

    ~/.bashrc

Editar:

    nano ~/.bashrc

Evitar esta configuración cuando el robot está en otra máquina:

    export ROS_HOSTNAME=localhost

Usar en su lugar:

    export ROS_MASTER_URI=http://10.10.73.229:11311
    export ROS_IP=$(hostname -I | awk '{print $1}')
    unset ROS_HOSTNAME


Problema 4: ModuleNotFoundError: No module named 'ultralytics'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Instalar:

    python3 -m pip install --user -U ultralytics opencv-python

Comprobar:

    python3 -c "from ultralytics import YOLO; print('YOLO funciona')"


Problema 5: pip no existe
~~~~~~~~~~~~~~~~~~~~~~~~~
Instalar:

    sudo apt update
    sudo apt install python3-pip -y

Si antes salían errores 404, hacer primero:

    sudo apt update


Problema 6: error raro de rosrun con "Success"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Puede pasar si el script no está bien preparado como ejecutable.

Comprobar:

    head -n 5 ~/catkin_ws/src/yolo_test/scripts/yolo_node.py
    ls -l ~/catkin_ws/src/yolo_test/scripts/yolo_node.py

La primera línea debe ser:

    #!/usr/bin/env python3

Y el archivo debe tener permiso de ejecución:

    chmod +x ~/catkin_ws/src/yolo_test/scripts/yolo_node.py


12. Comandos rápidos para repetir en una sesión nueva
-----------------------------------------------------
Si ya está todo instalado y solo quieres volver a probar YOLO otro día:

    source /opt/ros/noetic/setup.bash
    source ~/catkin_ws/devel/setup.bash
    export ROS_MASTER_URI=http://10.10.73.229:11311
    export ROS_IP=$(hostname -I | awk '{print $1}')
    unset ROS_HOSTNAME

    rostopic list | grep camera
    rqt_image_view

    rosrun yolo_test yolo_node.py _image_topic:=/camera/image


13. Siguiente paso del proyecto
-------------------------------
Cuando la detección ya funcione, el siguiente paso será modificar el nodo para que además de mostrar cajas publique las detecciones en un tópico ROS.

Por ejemplo:

    /detected_objects

Y luego se podrá hacer una lógica como:

    bottle  -> yellow_bin
    banana  -> organic_bin
    book    -> blue_bin

Pero eso será el siguiente bloque. Primero esta prueba sirve solo para validar YOLO + cámara.
