import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'robot_descriere'
    pkg_share = get_package_share_directory(pkg_name)

    urdf_file = os.path.join(pkg_share, 'urdf', 'robot_core.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    map_file = os.path.join(pkg_share, 'maps', 'camera_map.yaml')
    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': ['-r ', os.path.join(pkg_share, 'worlds', 'camera.sdf')]}.items()
    )

    rsp = TimerAction(period=2.0, actions=[Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )])

    bridge = TimerAction(period=3.0, actions=[Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/world/camera/model/robot_aspirator/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[('/world/camera/model/robot_aspirator/joint_state', '/joint_states')],
        parameters=[{'use_sim_time': True}]
    )])

    tf_bridge = TimerAction(period=4.0, actions=[Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/model/robot_aspirator/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'],
        parameters=[{'use_sim_time': True}],
        remappings=[('/model/robot_aspirator/tf', '/tf')]
    )])

    scan_fix = TimerAction(period=5.0, actions=[Node(
        package='robot_creier',
        executable='scan_frame_fix',
        parameters=[{'use_sim_time': True}]
    )])

    map_server = TimerAction(period=6.0, actions=[Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[{'use_sim_time': True, 'yaml_filename': map_file}]
    )])

    amcl = TimerAction(period=6.0, actions=[Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        parameters=[nav2_params]
    )])

    lifecycle_map = TimerAction(period=7.0, actions=[Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )])

    nav2 = TimerAction(period=8.0, actions=[IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py'
        )]),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': nav2_params,
        }.items()
    )])

    rviz = TimerAction(period=14.0, actions=[Node(
        package='rviz2',
        executable='rviz2',
        parameters=[{'use_sim_time': True}]
    )])

    return LaunchDescription([gazebo, rsp, bridge, tf_bridge, scan_fix, map_server, amcl, lifecycle_map, nav2, rviz])
