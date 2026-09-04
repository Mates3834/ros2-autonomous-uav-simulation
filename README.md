# ROS2 Autonomous UAV Simulation

A modular **ROS 2-based autonomous UAV simulation framework** demonstrating trajectory generation, sensor simulation, state estimation, closed-loop guidance and control, vehicle-state propagation, and system-level monitoring through distributed ROS 2 nodes.

The project focuses on the software architecture required to connect individual autonomy components through **ROS 2 publishers, subscribers, topics, timers, and launch files**.

The current public implementation uses a lightweight planar UAV simulator together with synthetic GPS-like and IMU-like measurements. This allows the complete autonomy pipeline to be demonstrated without relying on a platform-specific flight controller or external simulator.

> **Note:** The current version implements the autonomous system directly through ROS 2 nodes. Gazebo/Ignition, PX4, ArduPilot, MAVROS, and real UAV hardware integration are considered future extensions and are not claimed as part of the current implementation.

---

## System Architecture

The complete ROS 2 architecture follows the closed-loop structure:

```text
                 Trajectory Planner
                        |
                        |
                  /uav/reference
                        |
                        v
                   Controller
                        |
                        |
                   /uav/cmd_vel
                        |
                        v
                Vehicle Simulator
                        |
                        |
                /uav/ground_truth
                        |
                        v
                    Sensors
                  /          \
                 /            \
                v              v
        GPS-like Sensor    IMU-like Sensor
                |              |
                v              v
       /uav/sensor/gps   /uav/sensor/imu_yaw
                \              /
                 \            /
                  v          v
                  State Estimator
                         |
                         |
                /uav/state_estimate
                         |
                 +-------+-------+
                 |               |
                 v               v
             Controller        Monitor
                                 |
                                 v
                       /uav/tracking_error
```

This architecture demonstrates the separation between:

```text
Planning
   ↓
Guidance / Control
   ↓
Vehicle Dynamics
   ↓
Sensors
   ↓
State Estimation
   ↓
Feedback
```

---

# 1. ROS 2 Architecture

The project is organized as a set of independent ROS 2 nodes.

The current implementation contains six main nodes:

| Node | Function |
|---|---|
| `vehicle_simulator` | Generic UAV state propagation |
| `sensor_node` | Synthetic GPS-like and IMU-like measurements |
| `state_estimator` | Filtered UAV-state estimation |
| `trajectory_planner` | Time-varying trajectory generation |
| `controller` | Closed-loop speed and heading control |
| `monitor` | Tracking-error calculation |

Each subsystem communicates through ROS 2 topics rather than direct function calls.

This produces a distributed software architecture similar to that used in larger autonomous robotic systems.

---

# 2. ROS 2 Communication Graph

The main communication graph is:

```text
trajectory_planner
        |
        | /uav/reference
        v
    controller
        |
        | /uav/cmd_vel
        v
vehicle_simulator
        |
        | /uav/ground_truth
        v
   sensor_node
     /      \
    /        \
   v          v
 GPS-like   IMU-like
    \          /
     \        /
      v      v
 state_estimator
        |
        | /uav/state_estimate
        |
    +---+---+
    |       |
    v       v
controller monitor
              |
              v
     /uav/tracking_error
```

The controller therefore operates using the **estimated state**, rather than directly accessing the simulated ground-truth state.

---

# 3. ROS 2 Topics

The following topics are used:

| Topic | Purpose |
|---|---|
| `/uav/ground_truth` | Simulated true UAV state |
| `/uav/sensor/gps` | Noisy GPS-like position measurement |
| `/uav/sensor/imu_yaw` | Noisy IMU-like yaw measurement |
| `/uav/state_estimate` | Filtered UAV-state estimate |
| `/uav/reference` | Desired trajectory reference |
| `/uav/cmd_vel` | Speed and yaw-rate commands |
| `/uav/tracking_error` | Position tracking error |

The topic structure creates a clear separation between simulation, sensing, estimation, planning, control, and monitoring.

---

# 4. Vehicle Simulator Node

The `vehicle_simulator` node represents the UAV using a generic planar kinematic model.

The state consists of

```text
x
y
psi
V
```

where:

```text
x, y = planar position
psi  = heading angle
V    = forward speed
```

The motion equations are:

```text
x_dot = V cos(psi)
```

```text
y_dot = V sin(psi)
```

```text
psi_dot = omega
```

where

```text
omega
```

is the commanded yaw rate.

The node receives control commands through:

```text
/uav/cmd_vel
```

and publishes the resulting state through:

```text
/uav/ground_truth
```

---

# 5. Command Limits

The public simulator applies simple limits to the control inputs.

The forward-speed command is bounded:

```text
0 <= V_cmd <= V_max
```

and the yaw-rate command is bounded:

```text
-omega_max <= omega_cmd <= omega_max
```

These constraints prevent unrealistic instantaneous control commands in the generic simulation.

---

# 6. Synthetic Sensor Node

The `sensor_node` subscribes to the simulated ground-truth state.

```text
/uav/ground_truth
        |
        v
    sensor_node
```

It produces two independent synthetic sensor streams.

---

## GPS-Like Position Sensor

The simulated position measurement is:

```text
x_GPS = x_true + n_x
```

```text
y_GPS = y_true + n_y
```

where

```text
n_x, n_y
```

represent synthetic measurement noise.

The result is published through:

```text
/uav/sensor/gps
```

---

## IMU-Like Yaw Sensor

The yaw measurement is represented as:

```text
psi_IMU = psi_true + n_psi
```

where

```text
n_psi
```

represents synthetic angular measurement noise.

The result is published through:

```text
/uav/sensor/imu_yaw
```

---

# 7. State Estimation Node

The `state_estimator` node receives both sensor streams:

```text
GPS-like position
        +
IMU-like yaw
        |
        v
 State Estimator
```

The current public implementation applies a lightweight low-pass filtering approach to the GPS-like position measurements.

For example:

```text
x_hat(k) =
(1-alpha) x_hat(k-1)
+
alpha x_GPS(k)
```

and similarly for `y`.

The yaw estimate is obtained from the IMU-like measurement.

The resulting estimated state is published through:

```text
/uav/state_estimate
```

---

# 8. Why Ground Truth Is Separated from Estimated State

A key architectural feature is that the controller does **not** directly use the simulated ground truth.

Instead:

```text
Ground Truth
     ↓
Synthetic Sensors
     ↓
State Estimator
     ↓
Estimated State
     ↓
Controller
```

This makes the software structure closer to a realistic autonomous robotic architecture where control algorithms operate using sensor-derived state information.

---

# 9. Trajectory Planner Node

The `trajectory_planner` generates a time-varying reference trajectory.

The current implementation uses a generic trajectory of the form:

```text
x_ref(t) = V_ref t
```

```text
y_ref(t) = A sin(omega t)
```

This produces forward motion combined with smooth lateral variation.

The reference is published through:

```text
/uav/reference
```

---

# 10. Closed-Loop Controller

The `controller` subscribes to:

```text
/uav/state_estimate
```

and

```text
/uav/reference
```

The position error is calculated as:

```text
e_x =
x_ref - x_hat
```

```text
e_y =
y_ref - y_hat
```

The desired heading is then:

```text
psi_d =
atan2(e_y, e_x)
```

---

# 11. Heading Control

The heading error is:

```text
e_psi =
wrap(psi_d - psi_hat)
```

A proportional heading controller generates:

```text
omega_cmd =
K_psi e_psi
```

subject to yaw-rate limits.

This command is published as the angular component of:

```text
/uav/cmd_vel
```

---

# 12. Speed Control

The reference distance is calculated as:

```text
d =
sqrt(e_x^2 + e_y^2)
```

The forward-speed command is generated proportionally to this distance:

```text
V_cmd =
K_V d
```

with minimum and maximum speed limits.

The final control message therefore contains:

```text
/uav/cmd_vel

linear.x  -> forward-speed command
angular.z -> yaw-rate command
```

---

# 13. Closed-Loop Autonomy Pipeline

The complete feedback loop becomes:

```text
Reference
    ↓
Controller
    ↓
Control Command
    ↓
UAV Simulator
    ↓
Ground Truth
    ↓
Sensor Simulation
    ↓
State Estimation
    ↓
Estimated State
    ↓
Controller
```

This allows trajectory tracking to operate continuously through the ROS 2 communication architecture.

---

# 14. Monitoring Node

The `monitor` node receives:

```text
/uav/reference
```

and

```text
/uav/state_estimate
```

The tracking error is calculated as:

```text
e_tracking =
sqrt(
    (x_ref - x_hat)^2
    +
    (y_ref - y_hat)^2
)
```

The result is published through:

```text
/uav/tracking_error
```

This topic can be used for performance monitoring or future ROS-based data logging.

---

# 15. Node-Level Architecture

The software organization can also be represented as:

```text
+-----------------------+
| trajectory_planner    |
+-----------+-----------+
            |
            | /uav/reference
            v
+-----------------------+
| controller            |
+-----------+-----------+
            |
            | /uav/cmd_vel
            v
+-----------------------+
| vehicle_simulator     |
+-----------+-----------+
            |
            | /uav/ground_truth
            v
+-----------------------+
| sensor_node           |
+-----------+-----------+
            |
            | GPS + IMU-like data
            v
+-----------------------+
| state_estimator       |
+-----------+-----------+
            |
            | /uav/state_estimate
            +--------------------+
            |                    |
            v                    v
      controller              monitor
```

---

# 16. ROS 2 Concepts Demonstrated

The project demonstrates several fundamental ROS 2 concepts:

- ROS 2 nodes
- Publishers
- Subscribers
- Topics
- Message passing
- Timers
- Launch files
- Python ROS 2 packages
- `ament_python`
- `package.xml`
- `setup.py`
- `setup.cfg`
- `colcon` workspace organization
- Modular autonomous-system architecture

---

# 17. Repository Structure

```text
ros2_autonomous_uav_simulation/
│
├── README.md
│
├── docs/
│   └── architecture.md
│
└── ros2_ws/
    └── src/
        └── uav_simulation/
            │
            ├── package.xml
            ├── setup.py
            ├── setup.cfg
            │
            ├── resource/
            │   └── uav_simulation
            │
            ├── launch/
            │   └── autonomous_uav.launch.py
            │
            ├── config/
            │
            └── uav_simulation/
                │
                ├── __init__.py
                ├── vehicle_simulator.py
                ├── sensor_node.py
                ├── state_estimator.py
                ├── trajectory_planner.py
                ├── controller.py
                └── monitor.py
```

---

# 18. Node Description

| File | ROS 2 Node | Purpose |
|---|---|---|
| `vehicle_simulator.py` | `vehicle_simulator` | Propagates UAV motion |
| `sensor_node.py` | `sensor_node` | Generates synthetic GPS/IMU-like data |
| `state_estimator.py` | `state_estimator` | Estimates UAV state |
| `trajectory_planner.py` | `trajectory_planner` | Generates reference trajectory |
| `controller.py` | `controller` | Calculates closed-loop commands |
| `monitor.py` | `monitor` | Calculates trajectory-tracking error |

---

# 19. Building the ROS 2 Workspace

The project follows a standard ROS 2 workspace structure.

Navigate to:

```bash
cd ros2_ws
```

Build the package:

```bash
colcon build
```

Then source the workspace:

```bash
source install/setup.bash
```

---

# 20. Running the Complete System

Launch all nodes using:

```bash
ros2 launch uav_simulation autonomous_uav.launch.py
```

The launch file starts:

```text
vehicle_simulator
sensor_node
state_estimator
trajectory_planner
controller
monitor
```

as separate ROS 2 nodes.

---

# 21. Inspecting the ROS Graph

Available nodes can be inspected using:

```bash
ros2 node list
```

Expected nodes include:

```text
/controller
/monitor
/sensor_node
/state_estimator
/trajectory_planner
/vehicle_simulator
```

Available topics can be inspected using:

```bash
ros2 topic list
```

---

# 22. Inspecting Individual Topics

The estimated UAV state can be monitored with:

```bash
ros2 topic echo /uav/state_estimate
```

The trajectory reference can be monitored using:

```bash
ros2 topic echo /uav/reference
```

The controller output can be inspected with:

```bash
ros2 topic echo /uav/cmd_vel
```

The tracking error can be monitored using:

```bash
ros2 topic echo /uav/tracking_error
```

---

# 23. System-Level Data Flow

The project demonstrates how autonomous robotics software can be separated into reusable modules.

```text
Autonomy Stack

Mission / Reference
        ↓
Planning
        ↓
Control
        ↓
Vehicle
        ↓
Sensors
        ↓
Estimation
        ↓
Feedback
```

ROS 2 provides the communication infrastructure connecting these modules.

---

# 24. Why ROS 2?

In a monolithic simulation, all algorithms may run inside a single script:

```text
Planner
+
Controller
+
Vehicle
+
Sensors
+
Estimator
```

In this project, the same functionality is separated into independent nodes:

```text
Planner Node
     ↓
Controller Node
     ↓
Vehicle Node
     ↓
Sensor Node
     ↓
Estimator Node
```

This architecture makes individual components easier to test, replace, extend, and integrate.

---

# 25. Example Evaluation

The current system allows evaluation of:

### Trajectory Tracking

```text
Reference trajectory
        vs.
Estimated UAV trajectory
```

### Sensor Noise

```text
Ground truth
      vs.
GPS-like measurement
```

### State Estimation

```text
Noisy measurements
        ↓
Filtered state
```

### Closed-Loop Error

```text
Tracking Error [m]
        |
        |\
        | \____
        |      \___
        +--------------> Time
```

---

# 26. Recommended Repository Figures

Useful screenshots or plots for the GitHub repository include:

```text
results/
├── ros2_node_graph.png
├── trajectory_tracking.png
├── sensor_vs_estimate.png
└── tracking_error.png
```

A screenshot of the ROS 2 node graph would be particularly useful because it visually demonstrates that the autonomy functions are running as independent ROS 2 components.

---

# 27. Technologies

- ROS 2
- Python
- `rclpy`
- NumPy
- ROS 2 Publishers / Subscribers
- ROS 2 Topics
- ROS 2 Launch
- `ament_python`
- `colcon`
- Autonomous Systems
- Guidance and Control
- State Estimation

---

# 28. Research Areas

The project is related to:

- Autonomous UAV Systems
- ROS 2 Robotics
- Robotic Software Architecture
- Guidance, Navigation and Control
- State Estimation
- Sensor Integration
- Trajectory Tracking
- Autonomous Robotics
- Distributed Robotic Software
- Simulation-Based Development

---

# 29. Project Motivation

Autonomous robotic systems require more than individual control or planning algorithms.

A complete autonomy stack typically contains:

```text
Perception
     +
State Estimation
     +
Planning
     +
Guidance
     +
Control
     +
Vehicle Interface
```

These modules must communicate reliably while remaining sufficiently independent for development and testing.

The purpose of this project is therefore to demonstrate the integration of an autonomous UAV control pipeline using **ROS 2 as the system middleware**.

---

# 30. Current Scope

The current public implementation includes:

- ROS 2 Python package
- Six ROS 2 nodes
- Publisher/subscriber architecture
- Topic-based communication
- Launch-file integration
- Generic UAV kinematics
- Synthetic GPS-like sensing
- Synthetic IMU-like yaw sensing
- Lightweight state estimation
- Reference-trajectory generation
- Closed-loop heading control
- Speed control
- Tracking-error monitoring

The current version does **not** include Gazebo, PX4, ArduPilot, MAVROS, or real UAV hardware.

---

# 31. Future Extensions

## Gazebo / Ignition Integration

The internal simulator could be replaced by a physics-based simulator:

```text
ROS 2 Controller
       ↓
Gazebo / Ignition
       ↓
Simulated UAV
       ↓
Simulated Sensors
       ↓
ROS 2
```

---

## PX4 Integration

A future architecture could connect the ROS 2 autonomy stack to a standard autopilot interface:

```text
Trajectory Planner
        ↓
Guidance / Controller
        ↓
ROS 2 Interface
        ↓
PX4
        ↓
UAV
```

---

## Advanced State Estimation

The current lightweight estimator could be replaced by:

- Kalman Filter
- Extended Kalman Filter
- Unscented Kalman Filter
- GPS/IMU fusion
- Visual-inertial odometry
- SLAM-based localization

---

## Advanced Control

Future controller implementations could include:

- PID
- LQR
- LQI
- MPC
- Nonlinear MPC
- Adaptive control
- Disturbance observers

---

## 3-D UAV Dynamics

The planar model could be extended to:

```text
[x, y, z]
+
[roll, pitch, yaw]
+
linear velocity
+
angular velocity
```

resulting in a complete 6-DoF UAV simulation.

---

## Multi-UAV ROS 2 Architecture

The framework could also be expanded toward:

```text
/uav1/...
/uav2/...
/uav3/...
```

with:

- Distributed state exchange
- Formation control
- Cooperative planning
- Task allocation
- Multi-agent coordination

This would provide a natural connection to the **Multi-UAV Cooperative Autonomy** project.

---

# 32. Public Implementation Notice

The source code provided in this repository contains **generic and sanitized implementations** intended to demonstrate ROS 2 autonomous-system integration.

The public version intentionally excludes:

- Operational mission parameters
- Platform-specific flight-controller parameters
- Restricted UAV configurations
- Payload-control logic
- Engagement logic
- Real operational coordinates
- Restricted communication protocols
- Real flight-test data
- Sensitive system interfaces
- Unpublished operational configurations

All sensor models, trajectories, dynamics, and controller parameters are generic educational examples.

---

# 33. Status

**Research-oriented ROS 2 autonomous-UAV architecture / active development**

The current implementation demonstrates a complete ROS 2 software loop:

```text
Reference Generation
        ↓
Control
        ↓
Vehicle Simulation
        ↓
Sensor Generation
        ↓
State Estimation
        ↓
Feedback
```

Future development may include Gazebo/Ignition simulation, advanced state estimation, 3-D dynamics, and autopilot integration.

---

# Author

**Mehmet Ateş**

Research interests:

- Autonomous Systems
- Guidance, Navigation and Control
- UAV Autonomy
- USV Autonomy
- ROS 2 Robotics
- Multi-Agent Systems
- State Estimation
- Sensor Fusion
- Path Planning
- Reinforcement Learning
- Robotic Systems Engineering
