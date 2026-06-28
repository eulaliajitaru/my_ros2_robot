import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'robot_descriere'
    pkg_share = get_package_share_directory(pkg_name)

    urdf_file = os.path.join(pkg_share, 'urdf', 'robot_core.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # Calea catre configuratia RViz (optional, poate fi absent)
    rviz_config = os.path.join(pkg_share, 'config', 'robot.rviz')

    # 1. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': False  # standalone, fara Gazebo
        }]
    )

    # 2. Joint State Publisher GUI (slidere pentru rotile)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # 3. RViz2
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        # Incarca configuratia salvata daca exista, altfel porneste gol
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else []
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz2,
    ])
