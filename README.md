# RAPF-RM

Proyecto de robótica móvil para un TurtleBot3 Waffle que actúa como camión de la basura: detecta residuos, decide el contenedor correspondiente y prepara la misión de recogida y entrega.

## Estructura del repositorio

```text
RAPF-RM/
+-- README.md
+-- docs/
|   +-- lab_ros2_waffle_basura.md
+-- scripts/
    +-- setup_tb3_manipulation.sh
```

## Contenido

- `docs/lab_ros2_waffle_basura.md`: guía de laboratorio para preparar el entorno ROS2, conectar con el robot, probar la cámara y ejecutar la detección.
- `scripts/setup_tb3_manipulation.sh`: script de instalación para TurtleBot3 con manipulación en ROS Noetic. Se conserva como apoyo para la parte de manipulación, aunque el proyecto principal se orienta a ROS2.

## Uso recomendado en el laboratorio

Clona este repositorio dentro de un workspace ROS2:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone <URL_DEL_REPOSITORIO>
cd ~/ros2_ws
colcon build
source install/setup.bash
```

Consulta la guía completa en `docs/lab_ros2_waffle_basura.md`.

## Cuando haya código ROS2

Cuando el proyecto tenga nodos, paquetes o launch files, la estructura debería crecer dentro de `src/`. Por ejemplo:

```text
src/
+-- waffle_garbage_truck/
    +-- package.xml
    +-- setup.py
    +-- waffle_garbage_truck/
    +-- launch/
    +-- config/
```

Por ahora el repositorio queda centrado en documentación y scripts existentes, sin carpetas vacías innecesarias.
