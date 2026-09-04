# ROS 2 Architecture

```text
trajectory_planner
       |
 /uav/reference
       |
       v
   controller <--------- /uav/state_estimate
       |
 /uav/cmd_vel
       |
       v
vehicle_simulator
       |
 /uav/ground_truth
       |
       v
   sensor_node
   /          \
gps-like     imu-like
   \          /
    state_estimator
          |
 /uav/state_estimate
          |
        monitor
```

The package intentionally uses standard ROS 2 messages to keep the example
portable and easy to inspect.
