import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'robot_descriere'
    
    urdf_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'robot_core.urdf')
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # 1. Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 2. Pornim noul Gazebo (Harmonic) - în loc de gazebo_ros
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # 3. Spawn robot - folosim executabilul 'create' din ros_gz_sim
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'licenta_robot', '-z', '0.2'],
        output='screen'
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity
    ])