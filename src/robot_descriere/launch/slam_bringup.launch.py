import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'robot_descriere'
    pkg_share = get_package_share_directory(pkg_name)

    urdf_file = os.path.join(pkg_share, 'urdf', 'robot_core.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # 1. Gazebo cu robotul in SDF
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': ['-r ', os.path.join(pkg_share, 'worlds', 'camera.sdf')]}.items()
    )

    # 2. Robot State Publisher (TF static: laser_frame, imu_link etc.)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # 3. Bridge ROS2 <-> Gazebo
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
                '/world/camera/model/robot_aspirator/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            remappings=[
                ('/world/camera/model/robot_aspirator/joint_state', '/joint_states'),
            ],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )]
    )

    # 4. TF bridge odom->base_link din Gazebo
    tf_bridge = TimerAction(
        period=4.0,
        actions=[Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/model/robot_aspirator/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'],
            parameters=[{'use_sim_time': True}],
            remappings=[('/model/robot_aspirator/tf', '/tf')],
            output='screen'
        )]
    )

    # 5. Odom to TF publisher (timestamp corect)
    odom_to_tf = TimerAction(
        period=5.0,
        actions=[Node(
            package='robot_creier',
            executable='odom_to_tf',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )]
    )

    # 6. SLAM Toolbox
    slam = TimerAction(
        period=6.0,
        actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py'
            )]),
            launch_arguments={
                'use_sim_time': 'true',
                'slam_params_file': '/tmp/slam_config.yaml'
            }.items()
        )]
    )

    # 7. RViz
    rviz = TimerAction(
        period=8.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )]
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        ros_gz_bridge,
        tf_bridge,
        odom_to_tf,
        slam,
        rviz,
    ])
