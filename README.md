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
- `waste_robot_behavior/`: paquete ROS Python para detección RGB-D, clasificación, fine-tuning y comportamiento de residuos.
- `yolo_test/`: paquete ROS de prueba para ejecutar YOLO sobre `/camera/image`, con parámetro `model_path` para cargar `best.pt`.
- `docs/waste_behavior_algorithm.md`: diseño operativo del algoritmo YOLO RGB-D.

## Fine-tuning YOLOv8n

El primer dataset elegido es Mendeley "A synthetic outdoor waste image dataset with YOLO-format annotations for object detection":

```text
https://data.mendeley.com/datasets/2x69gjbcz6/2
```

Tras descargarlo y extraerlo:

```bash
python3 -m waste_robot_behavior.dataset.mendeley_yolo /ruta/dataset data/mendeley_yolo_4bins --sample-size 600
python3 -m waste_robot_behavior.dataset.train_yolov8 data/mendeley_yolo_4bins/data.yaml
```

Tambien hay una version autocontenida para Google Colab en `notebooks/yolov8n_mendeley_colab.ipynb`.

Las clases entrenadas son `paper`, `plastic`, `glass` y `residual`.

## Uso del modelo entrenado

Después de descargar `best.pt` desde Colab al PC donde ejecutas ROS:

```bash
rosrun yolo_test yolo_node.py _image_topic:=/camera/image _model_path:=/ruta/a/best.pt
```

Si no pasas `_model_path`, el nodo usa `yolov8n.pt`.

## Verificación Local

Los módulos core no dependen de ROS para poder probar la lógica en cualquier entorno con Python:

```bash
python -m unittest discover -s tests -v
```
