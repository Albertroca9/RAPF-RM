README_LAB_ROS2_WAFFLE_BASURA

Proyecto ROS2 - Robot Waffle recolector de residuos por color

Este proyecto permite que un robot móvil tipo TurtleBot Waffle con pinza actúe como un pequeño camión de basura. El robot detecta el color dominante de un residuo mediante la cámara, decide a qué contenedor corresponde y ejecuta la misión de recogida y entrega.

El entorno de laboratorio usa ordenadores con memoria temporal, por lo que cada vez que se reinicia o se apaga el ordenador hay que volver a preparar el entorno.

IMPORTANTE:
- Antes de apagar el ordenador, hacer siempre git add, git commit y git push.
- Si no se suben los cambios al repositorio, se perderán.
- Cambiar en este documento los valores URL_DEL_REPOSITORIO, NOMBRE_DEL_REPOSITORIO y nombre_paquete por los valores reales del proyecto.


============================================================
1. AL COGER EL ORDENADOR DEL LABORATORIO
============================================================

Abrir una terminal y comprobar qué versión de ROS2 está instalada:

    ls /opt/ros

Normalmente aparecerá algo como:

    humble

o:

    jazzy

En este README se usará la variable ROS_DISTRO para no tener que escribir manualmente la versión cada vez.

Si la versión instalada es Humble, ejecutar:

    export ROS_DISTRO=humble
    source /opt/ros/$ROS_DISTRO/setup.bash

Si la versión instalada no es humble, cambiarla. Por ejemplo, si fuera jazzy:

    export ROS_DISTRO=jazzy
    source /opt/ros/$ROS_DISTRO/setup.bash

Comprobar que ROS2 funciona:

    ros2 --version


============================================================
2. CREAR EL WORKSPACE
============================================================

Crear un workspace limpio para la sesión:

    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws/src


============================================================
3. DESCARGAR EL PROYECTO
============================================================

Clonar el repositorio del proyecto:

    git clone URL_DEL_REPOSITORIO

Entrar en el workspace:

    cd ~/ros2_ws

La estructura debería quedar aproximadamente así:

    ~/ros2_ws/
    └── src/
        └── NOMBRE_DEL_REPOSITORIO/
            └── paquetes_ros2/


============================================================
4. INSTALAR DEPENDENCIAS NECESARIAS
============================================================

Actualizar la lista de paquetes:

    sudo apt update

Instalar herramientas básicas de ROS2:

    sudo apt install -y python3-pip python3-colcon-common-extensions python3-rosdep

Instalar dependencias para visión por computador:

    sudo apt install -y python3-opencv
    sudo apt install -y ros-$ROS_DISTRO-cv-bridge
    sudo apt install -y ros-$ROS_DISTRO-image-transport
    sudo apt install -y ros-$ROS_DISTRO-rqt-image-view

Instalar dependencias de Python:

    pip3 install numpy

Si rosdep no está inicializado, ejecutar:

    sudo rosdep init

Si da error diciendo que ya está inicializado, no pasa nada.

Después ejecutar:

    rosdep update

Instalar dependencias del workspace:

    cd ~/ros2_ws
    rosdep install --from-paths src --ignore-src -r -y


============================================================
5. COMPILAR EL WORKSPACE
============================================================

Desde la raíz del workspace:

    cd ~/ros2_ws
    colcon build

Si compila correctamente, cargar el workspace:

    source install/setup.bash

Para no tener que hacer source manualmente en cada terminal nueva durante esta sesión:

    echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
    echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
    source ~/.bashrc

Importante:
Como el ordenador borra la memoria al apagarse, esto se tendrá que repetir cada día.


============================================================
6. CONFIGURAR COMUNICACIÓN CON EL ROBOT
============================================================

El ordenador y el robot deben estar conectados a la misma red.

Comprobar la IP del ordenador:

    hostname -I

Comprobar que el ordenador ve los nodos ROS2:

    ros2 node list

Comprobar que se reciben topics:

    ros2 topic list

Si no aparece nada del robot, comprobar:

1. Que el robot está encendido.
2. Que ordenador y robot están en la misma red.
3. Que ambos usan el mismo ROS_DOMAIN_ID.

Configurar un ROS_DOMAIN_ID, por ejemplo:

    export ROS_DOMAIN_ID=30

En el robot debe estar configurado el mismo valor:

    export ROS_DOMAIN_ID=30

Para comprobar que ROS2 detecta topics de la cámara:

    ros2 topic list | grep image

Topics típicos de cámara:

    /camera/image_raw
    /camera/color/image_raw
    /camera/image

El nombre exacto puede cambiar según la cámara y la configuración del robot.


============================================================
7. PROBAR LA CÁMARA
============================================================

Ver los topics disponibles:

    ros2 topic list

Buscar topics de imagen:

    ros2 topic list | grep camera

Ver información de un topic de cámara:

    ros2 topic info /camera/image_raw

Si el topic correcto no es /camera/image_raw, cambiarlo por el que aparezca en vuestro robot.

Para visualizar la cámara:

    rqt_image_view

Seleccionar el topic de la cámara en la interfaz.


============================================================
8. EJECUTAR EL DETECTOR DE COLOR
============================================================

Ejecutar el nodo de detección de color.

Ejemplo general:

    ros2 run nombre_paquete color_detector_node

Si el nodo acepta el topic de imagen como parámetro:

    ros2 run nombre_paquete color_detector_node --ros-args -p image_topic:=/camera/image_raw

Si la cámara usa otro topic, por ejemplo /camera/color/image_raw:

    ros2 run nombre_paquete color_detector_node --ros-args -p image_topic:=/camera/color/image_raw

El nodo debería publicar el color detectado en un topic parecido a:

    /detected_color

Comprobarlo con:

    ros2 topic echo /detected_color

Resultado esperado:

    data: "yellow"

o:

    data: "blue"

o:

    data: "unknown"


============================================================
9. LÓGICA DE CLASIFICACIÓN POR COLOR
============================================================

El proyecto usa detección de color en RGB.

La idea es:

    Imagen de cámara
            ↓
    Recorte de la zona donde está el residuo
            ↓
    Cálculo del color dominante
            ↓
    Clasificación del color
            ↓
    Asignación del contenedor

Mapeo usado:

    Amarillo → contenedor amarillo → plástico, latas, bricks
    Azul     → contenedor azul     → papel y cartón
    Verde    → contenedor verde    → vidrio
    Marrón   → contenedor marrón   → orgánico
    Gris     → contenedor gris     → rechazo

Importante:
El robot no reconoce realmente si un objeto es una lata, un cartón o una botella. Lo que reconoce es el color asociado a la categoría del residuo.

Por tanto, para la demo se recomienda que cada residuo tenga una etiqueta, pegatina o zona visible del color correspondiente.

Ejemplo:

    Lata con pegatina amarilla → contenedor amarillo
    Caja con pegatina azul     → contenedor azul
    Botella con pegatina verde → contenedor verde


============================================================
10. EJECUTAR EL NODO DE DECISIÓN
============================================================

El nodo de decisión recibe el color detectado y decide el contenedor destino.

Ejemplo:

    ros2 run nombre_paquete decision_node

Comprobar que publica el contenedor destino:

    ros2 topic echo /target_container

Resultado esperado:

    data: "yellow_bin"

o:

    data: "blue_bin"


============================================================
11. EJECUTAR NAVEGACIÓN HACIA EL CONTENEDOR
============================================================

Antes de ejecutar navegación, comprobar que el robot está localizado y que el mapa está cargado si se usa Nav2.

Topics útiles:

    ros2 topic list

Comprobar odometría:

    ros2 topic echo /odom

Comprobar el mapa:

    ros2 topic echo /map

Comprobar el estado de navegación:

    ros2 node list

Si se usa un nodo propio para enviar al robot al contenedor:

    ros2 run nombre_paquete navigation_to_bin_node

La lógica esperada es:

    /target_container = yellow_bin
            ↓
    Ir a la posición del contenedor amarillo

Ejemplo de posiciones:

    yellow_bin → x = 1.0, y = 0.0
    blue_bin   → x = 2.0, y = 0.0
    green_bin  → x = 3.0, y = 0.0
    brown_bin  → x = 4.0, y = 0.0

Estas posiciones deben ajustarse al mapa real del laboratorio.


============================================================
12. EJECUTAR CONTROL DE LA PINZA
============================================================

Si la pinza está integrada como OpenMANIPULATOR o similar, comprobar primero que aparecen sus topics o servicios:

    ros2 topic list | grep joint
    ros2 service list | grep gripper
    ros2 action list

Para lanzar el nodo de manipulación:

    ros2 run nombre_paquete manipulation_node

La secuencia esperada de la pinza es:

    1. Abrir pinza
    2. Acercarse al residuo
    3. Cerrar pinza
    4. Levantar o asegurar residuo
    5. Navegar al contenedor
    6. Abrir pinza
    7. Volver a posición inicial


============================================================
13. EJECUCIÓN COMPLETA DEL SISTEMA
============================================================

En una sesión normal se usarían varias terminales.

------------------------------------------------------------
Terminal 1: cargar ROS2 y workspace
------------------------------------------------------------

    source /opt/ros/$ROS_DISTRO/setup.bash
    source ~/ros2_ws/install/setup.bash
    export ROS_DOMAIN_ID=30

------------------------------------------------------------
Terminal 2: comprobar cámara
------------------------------------------------------------

    source /opt/ros/$ROS_DISTRO/setup.bash
    source ~/ros2_ws/install/setup.bash
    export ROS_DOMAIN_ID=30
    rqt_image_view

------------------------------------------------------------
Terminal 3: detector de color
------------------------------------------------------------

    source /opt/ros/$ROS_DISTRO/setup.bash
    source ~/ros2_ws/install/setup.bash
    export ROS_DOMAIN_ID=30

    ros2 run nombre_paquete color_detector_node --ros-args -p image_topic:=/camera/image_raw

------------------------------------------------------------
Terminal 4: nodo de decisión
------------------------------------------------------------

    source /opt/ros/$ROS_DISTRO/setup.bash
    source ~/ros2_ws/install/setup.bash
    export ROS_DOMAIN_ID=30

    ros2 run nombre_paquete decision_node

------------------------------------------------------------
Terminal 5: navegación
------------------------------------------------------------

    source /opt/ros/$ROS_DISTRO/setup.bash
    source ~/ros2_ws/install/setup.bash
    export ROS_DOMAIN_ID=30

    ros2 run nombre_paquete navigation_to_bin_node

------------------------------------------------------------
Terminal 6: manipulación
------------------------------------------------------------

    source /opt/ros/$ROS_DISTRO/setup.bash
    source ~/ros2_ws/install/setup.bash
    export ROS_DOMAIN_ID=30

    ros2 run nombre_paquete manipulation_node


============================================================
14. COMPROBACIONES RÁPIDAS
============================================================

Ver nodos activos:

    ros2 node list

Ver topics activos:

    ros2 topic list

Ver mensajes del detector de color:

    ros2 topic echo /detected_color

Ver mensajes del contenedor destino:

    ros2 topic echo /target_container

Ver frecuencia de la cámara:

    ros2 topic hz /camera/image_raw

Ver tipo de mensaje de la cámara:

    ros2 topic info /camera/image_raw


============================================================
15. PROBLEMAS FRECUENTES
============================================================

------------------------------------------------------------
Problema: no funciona ros2
------------------------------------------------------------

Solución:

    source /opt/ros/$ROS_DISTRO/setup.bash

Si no se ha definido ROS_DISTRO:

    export ROS_DISTRO=humble
    source /opt/ros/$ROS_DISTRO/setup.bash


------------------------------------------------------------
Problema: no encuentra el paquete
------------------------------------------------------------

Ejemplo de error:

    Package 'nombre_paquete' not found

Solución:

    cd ~/ros2_ws
    colcon build
    source install/setup.bash

Comprobar paquetes disponibles:

    ros2 pkg list | grep nombre_paquete


------------------------------------------------------------
Problema: no se ve la cámara
------------------------------------------------------------

Comprobar topics:

    ros2 topic list | grep image

Si el topic no es /camera/image_raw, lanzar el detector con el topic correcto:

    ros2 run nombre_paquete color_detector_node --ros-args -p image_topic:=/topic_correcto


------------------------------------------------------------
Problema: el robot no aparece en ROS2
------------------------------------------------------------

Comprobar red:

    hostname -I

Comprobar que robot y ordenador están en la misma red.

Comprobar ROS_DOMAIN_ID:

    echo $ROS_DOMAIN_ID

Configurar el mismo valor en ordenador y robot:

    export ROS_DOMAIN_ID=30


------------------------------------------------------------
Problema: detecta mal los colores
------------------------------------------------------------

Soluciones:

1. Usar objetos con colores más saturados.
2. Acercar el objeto a la cámara.
3. Evitar fondos del mismo color.
4. Usar una región de interés fija.
5. Ajustar los rangos RGB.
6. Añadir una clase unknown si la confianza es baja.


============================================================
16. GUARDAR CAMBIOS ANTES DE APAGAR EL ORDENADOR
============================================================

Como el ordenador del laboratorio borra los datos al apagarse, antes de cerrar la sesión hay que subir los cambios al repositorio.

Ver cambios:

    git status

Añadir cambios:

    git add .

Crear commit:

    git commit -m "Actualiza deteccion de color y logica de contenedores"

Subir cambios:

    git push

Muy importante:
Si no se hace git push, los cambios pueden perderse al apagar el ordenador.


============================================================
17. SCRIPT RÁPIDO OPCIONAL
============================================================

Para ahorrar tiempo, se puede crear un script llamado setup_lab.sh.

Crear archivo:

    nano setup_lab.sh

Pegar:

    #!/bin/bash

    export ROS_DISTRO=humble
    export ROS_DOMAIN_ID=30

    source /opt/ros/$ROS_DISTRO/setup.bash

    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws

    if [ ! -d "src/NOMBRE_DEL_REPOSITORIO" ]; then
        cd src
        git clone URL_DEL_REPOSITORIO
        cd ..
    fi

    sudo apt update

    sudo apt install -y python3-pip python3-colcon-common-extensions python3-rosdep
    sudo apt install -y python3-opencv
    sudo apt install -y ros-$ROS_DISTRO-cv-bridge
    sudo apt install -y ros-$ROS_DISTRO-image-transport
    sudo apt install -y ros-$ROS_DISTRO-rqt-image-view

    pip3 install numpy

    rosdep update
    rosdep install --from-paths src --ignore-src -r -y

    colcon build

    source install/setup.bash

    echo "Entorno preparado."
    echo "ROS_DISTRO=$ROS_DISTRO"
    echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
    echo "Workspace: ~/ros2_ws"

Dar permisos:

    chmod +x setup_lab.sh

Ejecutar:

    ./setup_lab.sh

Antes de usarlo, cambiar:

    NOMBRE_DEL_REPOSITORIO
    URL_DEL_REPOSITORIO

por los valores reales del proyecto.


============================================================
18. RESUMEN RÁPIDO DE COMANDOS PARA CADA DÍA
============================================================

Ejecutar estos comandos al empezar una sesión nueva:

    export ROS_DISTRO=humble
    source /opt/ros/$ROS_DISTRO/setup.bash

    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws/src

    git clone URL_DEL_REPOSITORIO

    cd ~/ros2_ws

    sudo apt update
    sudo apt install -y python3-pip python3-colcon-common-extensions python3-opencv ros-$ROS_DISTRO-cv-bridge ros-$ROS_DISTRO-image-transport ros-$ROS_DISTRO-rqt-image-view

    rosdep update
    rosdep install --from-paths src --ignore-src -r -y

    colcon build
    source install/setup.bash

    export ROS_DOMAIN_ID=30

    ros2 topic list
    ros2 topic list | grep image

    ros2 run nombre_paquete color_detector_node --ros-args -p image_topic:=/camera/image_raw

Nota:
Si la distro no es humble, cambiar humble por la versión correcta.


============================================================
19. CHECKLIST ANTES DE LA DEMO
============================================================

Antes de enseñar la demo, comprobar:

    [ ] El robot está encendido.
    [ ] El ordenador y el robot están en la misma red.
    [ ] ROS_DOMAIN_ID es el mismo en robot y ordenador.
    [ ] El workspace compila sin errores.
    [ ] Se ven los topics de la cámara.
    [ ] rqt_image_view muestra imagen.
    [ ] El detector publica /detected_color.
    [ ] El nodo de decisión publica /target_container.
    [ ] La navegación funciona.
    [ ] La pinza abre y cierra correctamente.
    [ ] Los residuos tienen colores o pegatinas suficientemente visibles.
    [ ] Los contenedores están colocados en posiciones conocidas.
    [ ] Se ha hecho git push antes de apagar el ordenador.


============================================================
20. IDEA GENERAL DEL SISTEMA
============================================================

El sistema completo se puede resumir así:

    1. El robot observa el residuo con la cámara.
    2. El nodo de visión detecta el color dominante en RGB.
    3. El color detectado se publica en /detected_color.
    4. El nodo de decisión convierte el color en contenedor destino.
    5. El robot recoge el residuo con la pinza.
    6. El robot navega hasta el contenedor correspondiente.
    7. El robot suelta el residuo.
    8. El robot vuelve a la zona inicial o espera el siguiente residuo.

Ejemplo:

    Residuo detectado: amarillo
    Color publicado: yellow
    Contenedor destino: yellow_bin
    Acción: llevar residuo al contenedor amarillo


============================================================
21. ACLARACIÓN TÉCNICA PARA EL INFORME
============================================================

El sistema no reconoce la naturaleza real del residuo. Es decir, no sabe si un objeto es realmente una lata, una botella o un cartón.

Lo que hace es clasificar el residuo mediante una codificación visual por color.

Por ejemplo:

    Amarillo → residuo destinado al contenedor amarillo
    Azul     → residuo destinado al contenedor azul
    Verde    → residuo destinado al contenedor verde
    Marrón   → residuo destinado al contenedor marrón

Esta simplificación permite centrar el proyecto en la integración robótica:

    visión por computador + decisión + navegación + manipulación

En una versión más avanzada, se podría combinar la detección de color con un detector de objetos o un modelo de aprendizaje automático para reconocer residuos reales.
