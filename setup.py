from setuptools import setup

package_name = 'uav_simulation'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
         ['launch/autonomous_uav.launch.py']),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='Mehmet Ates',
    maintainer_email='example@example.com',
    description='Generic ROS 2 autonomous UAV simulation architecture.',
    license='MIT',
    entry_points={'console_scripts': [
        'vehicle_simulator = uav_simulation.vehicle_simulator:main',
        'sensor_node = uav_simulation.sensor_node:main',
        'state_estimator = uav_simulation.state_estimator:main',
        'trajectory_planner = uav_simulation.trajectory_planner:main',
        'controller = uav_simulation.controller:main',
        'monitor = uav_simulation.monitor:main',
    ]},
)
