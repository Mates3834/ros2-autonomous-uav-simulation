from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    names=['vehicle_simulator','sensor_node','state_estimator',
           'trajectory_planner','controller','monitor']
    return LaunchDescription([
        Node(package='uav_simulation', executable=n, name=n, output='screen')
        for n in names
    ])
