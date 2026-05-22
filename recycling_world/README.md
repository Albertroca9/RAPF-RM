# Recycling World — Paquet ROS per a TurtleBot3
## Pràctica 4: Mapeig i Localització en ROS | RA Robòtica Mòbil 2026

---

## Descripció de l'entorn

Entorn tancat de **10×10 metres** dissenyat per practicar SLAM i localització amb TurtleBot3.

### Containers de reciclatge (fixos, als cantons)
| Color   | Posició       | Tipus de residu         |
|---------|---------------|-------------------------|
| 🔵 Blau  | Cantó NE      | Paper i cartró          |
| 🟡 Groc  | Cantó NW      | Envasos (plàstic/llauna)|
| 🟢 Verd  | Cantó SW      | Vidre                   |
| ⚫ Gris  | Cantó SE      | Resta (no reciclable)   |
| 🟫 Marró | Paret Nord    | Orgànic                 |

### Obstacles interiors
- 2 parets internes (1 horitzontal + 1 vertical)
- 1 pilar central

### Brossa dispersa (detectable per càmera)
| Objecte          | Color aproximat | Container destí |
|------------------|-----------------|-----------------|
| Ampolla plàstic  | Groc            | 🟡 Groc         |
| Llauna           | Groc/daurat     | 🟡 Groc         |
| Ampolla de vidre | Verd transparent| 🟢 Verd         |
| Caixa de cartró  | Marró           | 🔵 Blau         |
| Bossa de brossa  | Gris fosc       | ⚫ Gris         |
| Full de paper    | Blanc           | 🔵 Blau         |

---

## Instal·lació

```bash
# 1. Copieu el paquet al vostre workspace
cp -r recycling_world ~/catkin_ws/src/

# 2. Creeu el directori de mapes
mkdir -p ~/catkin_ws/src/recycling_world/maps

# 3. Compileu
cd ~/catkin_ws
catkin_make

# 4. Carregueu l'entorn
source devel/setup.bash
```

---

## FASE 1: Mapeig amb SLAM (gmapping)

### Pas 1 — Inicieu el món i el SLAM
Obriu **5 terminals** i executeu, en ordre:

```bash
# T1: ROS Master
roscore

# T2: Simulació Gazebo
export TURTLEBOT3_MODEL=burger
roslaunch recycling_world recycling_world.launch

# T3: SLAM gmapping
roslaunch recycling_world recycling_slam.launch

# T4: Visualitzador RViz
rosrun rviz rviz
```

### Pas 2 — Configureu RViz per al mapeig
A RViz, afegiu les següents visualitzacions (botó **Add**):
1. **Map** → Topic: `/map`
2. **LaserScan** → Topic: `/scan`
3. **RobotModel**
4. **TF**

Configureu **Fixed Frame** = `map` (Global Options)

### Pas 3 — Navegueu per crear el mapa
```bash
# T5: Teleoperació amb teclat
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```

**Consells per a un bon mapeig:**
- Moveu-vos **lentament** (velocitat màxima recomanada: 0.1 m/s)
- Feu **mínims girs bruscos**
- Recorreu **tots els racons** de l'entorn, especialment on hi ha containers
- Torneu ocasionalment per zones ja visitades per refinar el mapa

### Pas 4 — Deseu el mapa
Quan el mapa es vegi complet i net:
```bash
rosrun map_server map_saver -f ~/catkin_ws/src/recycling_world/maps/recycling_map
```
Això generarà dos fitxers:
- `recycling_map.yaml` — metadades del mapa
- `recycling_map.pgm` — imatge del mapa

---

## FASE 2: Localització amb AMCL

### Pas 1 — Inicieu la navegació
```bash
# T1: roscore
# T2: roslaunch recycling_world recycling_world.launch

# T3: Localització AMCL + map_server
roslaunch recycling_world recycling_navigation.launch \
  map_file:=$HOME/catkin_ws/src/recycling_world/maps/recycling_map.yaml

# T4: RViz
rosrun rviz rviz
```

### Pas 2 — Configureu RViz per a la localització
Afegiu a RViz:
1. **Map** → Topic: `/map`
2. **LaserScan** → Topic: `/scan`
3. **PoseArray** → Topic: `/particlecloud`
4. **RobotModel**

**Fixed Frame** = `map`

### Pas 3 — Establiu la posició inicial
1. A RViz, feu clic a **"2D Pose Estimate"** (barra superior)
2. Feu clic al mapa on es troba el robot a la simulació
3. Arrossegueu per indicar l'orientació
4. Observeu com apareixen les **partícules AMCL** (fletxes) al voltant del robot

### Pas 4 — Refinar la localització
```bash
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```
Moveu el robot i observeu com el núvol de partícules es **concentra** a mesura que el robot recull més dades del làser.

---

## Topics importants

| Topic             | Tipus                        | Descripció                        |
|-------------------|------------------------------|-----------------------------------|
| `/map`            | `nav_msgs/OccupancyGrid`     | Mapa d'ocupació                   |
| `/map_metadata`   | `nav_msgs/MapMetaData`       | Metadades del mapa                |
| `/scan`           | `sensor_msgs/LaserScan`      | Dades del làser                   |
| `/odom`           | `nav_msgs/Odometry`          | Odometria del robot               |
| `/particlecloud`  | `geometry_msgs/PoseArray`    | Núvol de partícules AMCL          |
| `/amcl_pose`      | `geometry_msgs/PoseWithCov.` | Posició estimada pel robot        |
| `/initialpose`    | `geometry_msgs/PoseWithCov.` | Posició inicial (2D Pose Estimate)|
| `/tf`             | `tf2_msgs/TFMessage`         | Arbre de transformacions          |

---

## Posicions dels containers (per al codi de navegació futur)

```python
CONTAINERS = {
    'blau':  {'x':  3.8, 'y':  3.8, 'tipus': 'paper'},
    'groc':  {'x': -3.8, 'y':  3.8, 'tipus': 'envasos'},
    'verd':  {'x': -3.8, 'y': -3.8, 'tipus': 'vidre'},
    'gris':  {'x':  3.8, 'y': -3.8, 'tipus': 'resta'},
    'marro': {'x':  0.0, 'y':  4.3, 'tipus': 'organic'},
}
```

---

## Resolució de problemes comuns

**El mapa no s'actualitza a RViz**
→ Comproveu que Fixed Frame sigui `map`, no `odom`

**El node gmapping no troba el làser**
→ `rostopic list` i comproveu que `/scan` és actiu

**AMCL no troba el robot al mapa**
→ Useu "2D Pose Estimate" per establir la posició inicial manualment

**Error "map not received"**
→ Assegureu-vos que el fitxer `.yaml` apunta correctament al `.pgm`
