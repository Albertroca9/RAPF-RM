#!/bin/bash
# =============================================================================
# setup_tb3_manipulation.sh
# Instalación completa: ROS Noetic + TurtleBot3 + OpenMANIPULATOR-X
# Para PC Remoto (Ubuntu 20.04) — sin tocar hardware del robot
# =============================================================================

set -e  # Salir si cualquier comando falla

# --- Colores para mensajes ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# =============================================================================
# 0. COMPROBACIONES PREVIAS
# =============================================================================

info "Comprobando sistema..."

# Verificar Ubuntu 20.04
if ! lsb_release -r | grep -q "20.04"; then
    warning "Este script está pensado para Ubuntu 20.04. Continúa bajo tu responsabilidad."
    read -p "¿Continuar de todas formas? [s/N] " -n 1 -r
    echo
    [[ $REPLY =~ ^[Ss]$ ]] || exit 1
fi

# Verificar conexión a internet
if ! ping -c 1 google.com &>/dev/null; then
    error "Sin conexión a internet. Conéctate y vuelve a ejecutar el script."
fi

info "Sistema OK. Comenzando instalación..."
echo ""

# =============================================================================
# 1. ROS NOETIC
# =============================================================================

if ! command -v roscore &>/dev/null; then
    info "ROS Noetic no detectado — instalando..."

    # Configurar sources
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
    sudo apt update

    # Instalar ROS Desktop Full
    sudo apt install -y ros-noetic-desktop-full

    # Inicializar rosdep
    if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
        sudo rosdep init
    fi
    rosdep update

    # Añadir source al bashrc
    if ! grep -q "source /opt/ros/noetic/setup.bash" ~/.bashrc; then
        echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
    fi

    info "ROS Noetic instalado."
else
    info "ROS Noetic ya está instalado — omitiendo."
fi

# Asegurarse de que ROS está disponible en esta sesión
source /opt/ros/noetic/setup.bash

# =============================================================================
# 2. DEPENDENCIAS DEL SISTEMA
# =============================================================================

info "Instalando dependencias del sistema..."

sudo apt update
sudo apt install -y \
    python3-rosdep \
    python3-rosinstall \
    python3-rosinstall-generator \
    python3-wstool \
    python3-catkin-tools \
    build-essential \
    git \
    curl \
    ros-noetic-dynamixel-sdk \
    ros-noetic-turtlebot3-msgs \
    ros-noetic-turtlebot3 \
    ros-noetic-ros-control \
    ros-noetic-ros-controllers \
    ros-noetic-gazebo-ros-control \
    ros-noetic-gazebo-ros-pkgs \
    ros-noetic-moveit \
    ros-noetic-moveit-ros-planning-interface \
    ros-noetic-moveit-commander \
    ros-noetic-joint-state-publisher-gui \
    ros-noetic-dwa-local-planner \
    ros-noetic-map-server \
    ros-noetic-amcl \
    ros-noetic-move-base

info "Dependencias instaladas."

# =============================================================================
# 3. WORKSPACE CATKIN
# =============================================================================

CATKIN_WS="$HOME/catkin_ws"

if [ ! -d "$CATKIN_WS" ]; then
    info "Creando workspace catkin en $CATKIN_WS..."
    mkdir -p "$CATKIN_WS/src"
    cd "$CATKIN_WS"
    catkin_make
else
    info "Workspace $CATKIN_WS ya existe — omitiendo creación."
fi

cd "$CATKIN_WS/src"

# =============================================================================
# 4. CLONAR REPOSITORIOS
# =============================================================================

info "Clonando repositorios de TurtleBot3 + OpenMANIPULATOR-X..."

clone_or_update() {
    local REPO_URL=$1
    local BRANCH=$2
    local DIR_NAME=$3

    if [ -d "$DIR_NAME" ]; then
        info "  $DIR_NAME ya existe — actualizando..."
        cd "$DIR_NAME"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
        cd ..
    else
        info "  Clonando $DIR_NAME (rama $BRANCH)..."
        git clone -b "$BRANCH" "$REPO_URL" "$DIR_NAME"
    fi
}

cd "$CATKIN_WS/src"

# Paquete principal de manipulación (rama noetic — ACTIVA)
clone_or_update \
    https://github.com/ROBOTIS-GIT/turtlebot3_manipulation.git \
    noetic \
    turtlebot3_manipulation

# Simulaciones de manipulación
clone_or_update \
    https://github.com/ROBOTIS-GIT/turtlebot3_manipulation_simulations.git \
    noetic \
    turtlebot3_manipulation_simulations

# Dependencias de OpenMANIPULATOR
clone_or_update \
    https://github.com/ROBOTIS-GIT/open_manipulator_dependencies.git \
    noetic \
    open_manipulator_dependencies

info "Repositorios listos."

# =============================================================================
# 5. INSTALAR DEPENDENCIAS CON ROSDEP
# =============================================================================

info "Resolviendo dependencias con rosdep..."

cd "$CATKIN_WS"
rosdep update
rosdep install --from-paths src --ignore-src -r -y || \
    warning "rosdep reportó algunos paquetes no resueltos — continuando de todas formas."

# =============================================================================
# 6. COMPILAR
# =============================================================================

info "Compilando workspace (esto puede tardar varios minutos)..."

cd "$CATKIN_WS"

# Intentar compilar todo; si falla open_manipulator_dependencies, compilar sin él
if ! catkin_make 2>&1 | tee /tmp/catkin_make.log | grep -q "Error"; then
    info "Compilación completa exitosa."
else
    warning "Error en compilación completa. Intentando compilar solo los paquetes esenciales..."
    catkin_make --pkg \
        turtlebot3_manipulation \
        turtlebot3_manipulation_simulations \
        || error "La compilación de paquetes esenciales también falló. Revisa /tmp/catkin_make.log"
    warning "Compilados solo los paquetes esenciales. open_manipulator_dependencies fue omitido."
fi

# =============================================================================
# 7. CONFIGURAR VARIABLES DE ENTORNO EN .bashrc
# =============================================================================

info "Configurando variables de entorno..."

add_to_bashrc() {
    local LINE=$1
    if ! grep -qF "$LINE" ~/.bashrc; then
        echo "$LINE" >> ~/.bashrc
        info "  Añadido: $LINE"
    else
        info "  Ya existe: $LINE"
    fi
}

add_to_bashrc "source /opt/ros/noetic/setup.bash"
add_to_bashrc "source $CATKIN_WS/devel/setup.bash"
add_to_bashrc "export TURTLEBOT3_MODEL=waffle"
add_to_bashrc "export ROS_MASTER_URI=http://localhost:11311"

# ROS_IP: detectar IP local automáticamente
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -n "$LOCAL_IP" ]; then
    add_to_bashrc "export ROS_IP=$LOCAL_IP"
    info "  ROS_IP detectada: $LOCAL_IP"
else
    warning "No se pudo detectar la IP local. Añade manualmente 'export ROS_IP=<tu_ip>' al .bashrc."
fi

# Aplicar en la sesión actual
source ~/.bashrc 2>/dev/null || true
source "$CATKIN_WS/devel/setup.bash"

# =============================================================================
# 8. VERIFICACIÓN FINAL
# =============================================================================

echo ""
info "=========================================="
info "  VERIFICACIÓN FINAL"
info "=========================================="

check_pkg() {
    if rospack find "$1" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $1"
    else
        echo -e "  ${RED}✗${NC} $1 — NO encontrado"
    fi
}

source "$CATKIN_WS/devel/setup.bash"

check_pkg turtlebot3_manipulation_bringup
check_pkg turtlebot3_manipulation_moveit_config
check_pkg turtlebot3_manipulation_gazebo
check_pkg turtlebot3_manipulation_gui

echo ""
info "=========================================="
info "  INSTALACIÓN COMPLETADA"
info "=========================================="
echo ""
echo "  Para aplicar los cambios en este terminal, ejecuta:"
echo ""
echo -e "  ${YELLOW}source ~/.bashrc${NC}"
echo ""
echo "  --- ARRANQUE ROBOT REAL ---"
echo "  Terminal 1:  roscore"
echo "  Terminal 2:  roslaunch turtlebot3_manipulation_bringup turtlebot3_manipulation_bringup.launch"
echo "  Terminal 3:  roslaunch turtlebot3_manipulation_moveit_config move_group.launch"
echo "  Terminal 4:  roslaunch turtlebot3_manipulation_gui turtlebot3_manipulation_gui.launch"
echo ""
echo "  --- SIMULACIÓN GAZEBO ---"
echo "  Terminal 1:  roslaunch turtlebot3_manipulation_gazebo turtlebot3_manipulation_gazebo.launch"
echo "  Terminal 2:  roslaunch turtlebot3_manipulation_moveit_config move_group.launch"
echo "  Terminal 3:  roslaunch turtlebot3_manipulation_gui turtlebot3_manipulation_gui.launch"
echo ""
echo -e "  ${YELLOW}RECUERDA:${NC} Cambia ROS_MASTER_URI a la IP del TurtleBot3 cuando uses el robot real:"
echo "  export ROS_MASTER_URI=http://<IP_DEL_ROBOT>:11311"
echo ""
