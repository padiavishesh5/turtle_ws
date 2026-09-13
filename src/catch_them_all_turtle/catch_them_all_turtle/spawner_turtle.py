#!/usr/bin/env python3
import math
import random
import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill
from turtle_interface.msg import Turtle, TurtleArray
from turtle_interface.srv import CatchTurtle
from functools import partial


class SpawnTurtleNode(Node):
    def __init__(self):
        super().__init__("spawner_turtle")
        self.declare_parameter("turtle_prefix_name", "turtle")
        self.turtle_name_prefix = self.get_parameter("turtle_prefix_name").value
        self.declare_parameter("spawn_frequency", 1.0)
        self.spawn_frequency_ = self.get_parameter("spawn_frequency").value
        self.turtle_counter = 1
        self.turtles_ = []
        self.alive_turtles_publisher_ = self.create_publisher(TurtleArray, "/alive_turtles", 10)
        self.spawn_turtle_client_ = self.create_client(Spawn, "/spawn")
        while not self.spawn_turtle_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for /spawn service...")
        self.kill_client_ = self.create_client(Kill, "/kill")
        self.catch_turtle_service_ = self.create_service(CatchTurtle, "catch_turtle", self.callback_catch_turtle_)
        self.spawn_turtle()
        self.spawn_turtle_timer_ = self.create_timer(1 / self.spawn_frequency_, self.spawn_turtle)

    def callback_catch_turtle_(self, request: CatchTurtle.Request, response: CatchTurtle.Response):
        self.call_kill_service_(request.name)
        response.success = True
        return response

    def publish_alive_turtles(self):
        msg = TurtleArray()
        msg.turtles = self.turtles_
        self.alive_turtles_publisher_.publish(msg)

    def spawn_turtle(self):
        self.turtle_counter += 1
        request = Spawn.Request()
        request.x = random.uniform(1.0, 10.0)
        request.y = random.uniform(1.0, 10.0)
        request.theta = random.uniform(0.0, 2 * math.pi)
        request.name = f"{self.turtle_name_prefix}{self.turtle_counter}"

        future = self.spawn_turtle_client_.call_async(request)
        future.add_done_callback(partial(self.spawn_turtle_response_callback, request))

    def spawn_turtle_response_callback(self, request: Spawn.Request, future):
        response = future.result()
        if response is not None:
            new_turtle = Turtle()
            new_turtle.name = response.name
            new_turtle.x = request.x
            new_turtle.y = request.y
            new_turtle.theta = request.theta
            self.turtles_.append(new_turtle)
            self.get_logger().info(f"Spawned turtle: {response.name}")
            self.publish_alive_turtles()
        else:
            self.get_logger().info("Failed to spawn turtle.")

    def call_kill_service_(self, turtle_name):
        while not self.kill_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("waiting for kill service")

        request = Kill.Request()
        request.name = turtle_name

        future = self.kill_client_.call_async(request)
        future.add_done_callback(
            partial(self.callback_call_kill_service_, turtle_name=turtle_name)
        )

    def callback_call_kill_service_(self, future, turtle_name):
        try:
            future.result()

            for i, turtle in enumerate(self.turtles_):
                if turtle.name == turtle_name:
                    del self.turtles_[i]
                    self.publish_alive_turtles()
                    self.get_logger().info(f"Removed turtle: {turtle_name}")
                    break

        except Exception as e:
            self.get_logger().error(f"Failed to kill {turtle_name}: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = SpawnTurtleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()























# #!/usr/bin/env python3
# import math
# import random
# import rclpy
# from rclpy.node import Node
# from turtlesim.srv import Spawn
# from turtle_interface.msg import Turtle, TurtleArray
# from functools import partial
# from turtle_interface.srv import CatchTurtle
# from turtlesim.srv import Kill


# class SpawnTurtleNode(Node):
#     def __init__(self):
#         super().__init__("spawner_turtle")
#         self.turtle_name_prefix = "turtle"
#         self.turtle_counter = 1
#         self.turtles_ = []
#         self.alive_turtles_ = self.create_publisher(TurtleArray, "/alive_turtles", 10)
#         self.spawn_turtle_client_ = self.create_client(Spawn, "/spawn")
#         while not self.spawn_turtle_client_.wait_for_service(timeout_sec=1.0):
#             self.get_logger().info("Waiting for /spawn service...")
#         self.kill_client_ = self.create_client(Kill, "/Kill")
#         self.catch_turtle_service_ = self.create_service(CatchTurtle, "catch_turtle", self.callback_catch_turtle_)
#         self.spawn_turtle()
#         self.spawn_turtle_timer_ = self.create_timer(3.5, self.spawn_turtle)

#     def callback_catch_turtle_(self, request: CatchTurtle.Request, response: CatchTurtle.Response)
#         # call kill service
#         self.call_kill_service_(request.name)
#         response.success = True
#         return response

#     def publish_alive_turtles(self):
#         msg = TurtleArray()
#         msg.turtles = self.turtles_
#         self.alive_turtles_.publish(msg)

#     def spawn_turtle(self):
#         self.turtle_counter += 1
#         request = Spawn.Request()
#         request.x = random.uniform(1.0, 10.0)
#         request.y = random.uniform(1.0, 10.0)
#         request.theta = random.uniform(0.0, 2 * math.pi)
#         request.name = f"{self.turtle_name_prefix}{self.turtle_counter}"

#         future = self.spawn_turtle_client_.call_async(request)
#         future.add_done_callback(partial(self.spawn_turtle_response_callback, request))

#     def spawn_turtle_response_callback(self, request: Spawn.Request, future):
#             response = future.result()
#             if response != None:
#                 self.get_logger().info("working")
#                 new_turtle = Turtle()
#                 new_turtle.name = response.name
#                 new_turtle.x = request.x
#                 new_turtle.y = request.y
#                 new_turtle.theta = request.theta
#                 self.turtles_.append(new_turtle)
#                 self.get_logger().info(f"Spawned turtle: {response.name}")
#                 self.publish_alive_turtles()
#             else:
#                 self.get_logger().info("Failed to spawn turtle.")

#     def call_kill_service_(self, turtle_name):
#         while not self.kill_client_.wait_for_service(timeout_sec=1.0):
#             self.get_logger().info("waiting for kill service")

#         request = kill.Request()
#         request.name = turtle_name
        
#         future = self.kill_client_.call_async(request)
#         future.add_done_callback(partial(self.callback_call_kill_service_, request=request))

#     def callback_call_kill_service_(self, future, turtle_name):
#         for (i, turtle) in enumerate(self.alive_turtles_)
#             if turtle.name == turtle_name
#                 del self.alive_turtles_[i]
#                 self.publish_alive_turtles()
#                 break


# def main(args=None):
#     rclpy.init(args=args)
#     node = SpawnTurtleNode()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()