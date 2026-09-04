# ROS2 Autonomous UAV Simulation

A generic ROS 2 package demonstrating a modular autonomous-UAV software
architecture using publishers, subscribers, timers, state estimation,
trajectory references, and closed-loop control.

Pipeline:

```text
Vehicle Simulator -> IMU/GPS-like Sensors -> State Estimator
       ^                                      |
       |                                      v
   Control Cmd <- Controller <- Reference Generator
```

The public version uses a lightweight planar UAV simulator so the ROS 2
software architecture can be studied without platform-specific flight stacks.

## Nodes

- `vehicle_simulator` — propagates generic UAV kinematics
- `sensor_node` — publishes noisy GPS-like position and IMU-like yaw
- `state_estimator` — fuses measurements into a simple filtered state estimate
- `trajectory_planner` — publishes a time-varying reference trajectory
- `controller` — computes bounded speed and yaw-rate commands
- `monitor` — reports tracking error

## Topics

```text
/uav/ground_truth
/uav/sensor/gps
/uav/sensor/imu_yaw
/uav/state_estimate
/uav/reference
/uav/cmd_vel
/uav/tracking_error
```

## Run

Create a ROS 2 workspace, place `uav_simulation` under `src`, then:

```bash
colcon build
source install/setup.bash
ros2 launch uav_simulation autonomous_uav.launch.py
```

## Scope

This repository demonstrates ROS 2 integration and autonomous-control software
structure. Gazebo/Ignition integration is documented as a future extension and
is not claimed as implemented in the current public package.

## Public Implementation Notice

All dynamics, sensors, trajectories, and parameters are generic educational
examples. No operational mission, payload, engagement, restricted platform, or
real flight-test logic is included.
