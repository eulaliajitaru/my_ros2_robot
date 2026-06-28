import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'robot_descriere'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': ['-r ', os.path.join(pkg_share, 'worlds', 'camera.sdf')]}.items()
    )

    # 2. Bridge
    ros_gz_bridge = TimerAction(
        period=3.0,
        actions=[Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )]
    )

    # 3. Odom to TF
    odom_to_tf = TimerAction(
        period=5.0,
        actions=[Node(
            package='robot_creier',
            executable='odom_to_tf',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )]
    )

    # 4. Static TF laser_frame
    static_tf_laser = TimerAction(
        period=5.0,
        actions=[Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0.16', '0', '0', '0', 'base_link', 'robot_aspirator/laser_frame/lidar_sensor'],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )]
    )

    # 5. Cartographer
    cartographer = TimerAction(
        period=7.0,
        actions=[Node(
            package='cartographer_ros',
            executable='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': True}],
            arguments=[
                '-configuration_directory', os.path.join(pkg_share, 'config'),
                '-configuration_basename', 'roomba.lua'
            ]
        )]
    )

    # 6. Cartographer occupancy grid
    occupancy_grid = TimerAction(
        period=8.0,
        actions=[Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{'use_sim_time': True}, {'resolution': 0.05}]
        )]
    )

    # 7. RViz
    rviz = TimerAction(
        period=9.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )]
    )

    return LaunchDescription([
        gazebo,
        ros_gz_bridge,
        odom_to_tf,
        static_tf_laser,
        cartographer,
        occupancy_grid,
        rviz,
    ])
