from distutils.core import setup

from catkin_pkg.python_setup import generate_distutils_setup


setup_args = generate_distutils_setup(
    packages=["waste_robot_behavior", "waste_robot_behavior.dataset"],
    package_dir={
        "waste_robot_behavior": ".",
        "waste_robot_behavior.dataset": "dataset",
    },
)

setup(**setup_args)
