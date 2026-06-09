# RAPF-RM

Proyecto de robot móvil con TurtleBot3 Waffle para detectar residuos, decidir el contenedor correspondiente y preparar la misión de recogida y entrega.

El repositorio combina documentación de laboratorio, scripts de instalación ROS y paquetes Python/ROS para detección YOLO y comportamiento.

## Estructura del repositorio

```text
RAPF-RM/
+-- README.md
+-- README_YOLO_WAFFLE_ROS1_NOETIC.txt
+-- setup_tb3_manipulation.sh
+-- data/
+-- docs/
+-- tests/
+-- waste_robot_behavior/
+-- yolo_test/
```

## Contenido

- `setup_tb3_manipulation.sh`: instalación de ROS Noetic, TurtleBot3 y OpenMANIPULATOR-X en un PC remoto Ubuntu 20.04.
- `README_YOLO_WAFFLE_ROS1_NOETIC.txt`: guía de prueba inicial YOLOv8n con la cámara del Waffle usando ROS1 Noetic.
- `waste_robot_behavior/`: paquete ROS Python para detección RGB-D, mapeo de clases YOLO, clasificación y comportamiento de residuos.
- `yolo_test/`: paquete ROS de prueba para ejecutar YOLOv8n sobre `/camera/image` y visualizar el mapeo COCO a contenedores.
- `docs/waste_behavior_algorithm.md`: diseño operativo del algoritmo YOLO RGB-D.

## Runtime YOLOv8n

La lógica principal actual usa `yolov8n.pt` normal y mapea clases COCO a los contenedores del proyecto:

- `book` -> `paper`
- `bottle` -> `plastic`
- `wine glass` -> `glass`
- alimentos COCO como `banana`, `apple` o `pizza` -> `residual`

Las clases ambiguas no se recogen como basura. `person` sigue siendo una clase de seguridad.

```bash
rosrun yolo_test yolo_node.py _image_topic:=/camera/image _confidence_threshold:=0.25
```

## Fine-tuning YOLOv8n

El pipeline Mendeley/Colab queda conservado como histórico para retomar entrenamiento si hace falta, pero no es la vía principal de runtime.

## Verificación Local

Los módulos core no dependen de ROS para poder probar la lógica en cualquier entorno con Python:

```bash
python -m unittest discover -s tests -v
```
