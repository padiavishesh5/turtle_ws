# Turtlesim Catch Them All (ROS 2, Python)

`turtle1` chases the nearest spawned turtle and kills it. New turtles keep spawning at random positions.

A C++ version of this project is available here: https://github.com/padiavishesh5/turtle_cpp_ws

## Packages
- `my_robot_interfaces` - `Turtle`, `TurtleArray` msgs and `CatchTurtle` srv
- `turtlesim_catch_them_all` - `spawner` and `controller` nodes (`rclpy`)
- `my_robot_bringup` - launch file and parameters

## Nodes

| Node | Executable | Role |
|---|---|---|
| `turtle_spawner` | `spawner` | Spawns turtles via `/spawn`, keeps the list of alive turtles, kills caught turtles via `/kill` |
| `turtle_controller` | `controller` | Drives `turtle1` to the target turtle and requests the catch |

## How it works
1. `spawner` calls `/spawn` at a fixed frequency with a random x, y (0 to 11) and theta, then publishes all alive turtles on `alive_turtles`.
2. `controller` subscribes to `/turtle1/pose` and `alive_turtles`, then picks the nearest turtle (or the first in the list).
3. A 100 Hz control loop publishes `/turtle1/cmd_vel` with a proportional controller: linear speed = 2 x distance, angular speed = 6 x angle error.
4. When `turtle1` is within 0.5 of the target, it stops and calls the `catch_turtle` service.
5. `spawner` calls `/kill`, removes that turtle from its list and publishes the updated `alive_turtles`.

## Topics, services and interfaces

| Name | Type | Used by |
|---|---|---|
| `alive_turtles` | `my_robot_interfaces/msg/TurtleArray` | published by spawner, subscribed by controller |
| `catch_turtle` | `my_robot_interfaces/srv/CatchTurtle` | served by spawner, called by controller |
| `/turtle1/pose` | `turtlesim/msg/Pose` | subscribed by controller |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | published by controller |
| `/spawn`, `/kill` | `turtlesim/srv/Spawn`, `turtlesim/srv/Kill` | called by spawner |

Interface definitions:
```
# Turtle.msg
string name
float64 x
float64 y
float64 theta

# TurtleArray.msg
Turtle[] turtles

# CatchTurtle.srv
string name
---
bool success
```

## Build and run
```bash
colcon build
source install/setup.bash
ros2 launch my_robot_bringup turtlesim_catch_them_all.launch.xml
```

Run the nodes manually instead of the launch file:
```bash
ros2 run turtlesim turtlesim_node
ros2 run turtlesim_catch_them_all spawner
ros2 run turtlesim_catch_them_all controller
```

## Parameters
Set in `my_robot_bringup/config/catch_them_all_config.yaml`:

| Node | Parameter | Default | Meaning |
|---|---|---|---|
| `turtle_controller` | `catch_closest_turtle_first` | `True` | `True`: chase the nearest turtle, `False`: chase the first one in the list |
| `turtle_spawner` | `turtle_name_prefix` | `turtle` | Name prefix of spawned turtles |
| `turtle_spawner` | `spawn_frequency` | `1.0` | Turtles spawned per second |

The provided config file sets `turtle_name_prefix: "my_turtle"` and `spawn_frequency: 1.5`.

Override a parameter from the command line:
```bash
ros2 run turtlesim_catch_them_all spawner --ros-args -p spawn_frequency:=3.0
```

## Repository layout
```
src/
├── my_robot_interfaces/
│   ├── msg/Turtle.msg
│   ├── msg/TurtleArray.msg
│   └── srv/CatchTurtle.srv
├── turtlesim_catch_them_all/
│   └── turtlesim_catch_them_all/
│       ├── turtle_controller.py
│       └── turtle_spawner.py
└── my_robot_bringup/
    ├── config/catch_them_all_config.yaml
    └── launch/turtlesim_catch_them_all.launch.xml
```

## Requirements
- ROS 2 with `rclpy`, `turtlesim`, `geometry_msgs`
- `colcon` for building
