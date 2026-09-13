#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_interface.msg import TurtleArray
from turtle_interface.msg import Turtle
from turtle_interface.srv import CatchTurtle
from functools import partial

class catchturtlenode(Node):
    def __init__(self):
        super().__init__("catch_turtle")
        self.pose_ = None
        self.alive_turtle_: Turtle = None
        self.declare_parameter("closest_turtle_to_catch", True)
        self.catch_closest_turtle_first_ = self.get_parameter("closest_turtle_to_catch").value
        self.subscribe_pose_ = self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 10)
        self.publish_cmd_vel_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subscribe_alive_turtle_ = self.create_subscription(TurtleArray, "/alive_turtles", self.alive_turtle_callback, 10)
        self.timer_ = self.create_timer(0.01, self.timer_callback)
        self.catch_turtle_client_ = self.create_client(CatchTurtle, "catch_turtle")
        while not self.catch_turtle_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for catch_turtle service...")

    def pose_callback(self, msg: Pose):
        self.pose_ = msg

    def alive_turtle_callback(self, msg: TurtleArray):
        if self.pose_ is None:
            return
        if len(msg.turtles) > 0:
            if self.catch_closest_turtle_first_:
                closest_turtle = None
                closest_distance = None

                for turtle in msg.turtles:
                    dx = turtle.x - self.pose_.x
                    dy = turtle.y - self.pose_.y
                    distance = math.hypot(dx, dy)

                    if closest_turtle is None or distance < closest_distance:
                        closest_distance = distance
                        closest_turtle = turtle

                self.alive_turtle_ = closest_turtle

            else:
                self.alive_turtle_ = msg.turtles[0]

    def timer_callback(self):
        if self.pose_ is None or self.alive_turtle_ is None:
            return

        dx = self.alive_turtle_.x - self.pose_.x
        dy = self.alive_turtle_.y - self.pose_.y
        distance = math.hypot(dx, dy)

        cmd_vel = Twist()
        if distance > 0.1:
            cmd_vel.linear.x = 2.0 * distance
            angular_distance = math.atan2(dy, dx) - self.pose_.theta
            if angular_distance > math.pi:
                angular_distance -= 2 * math.pi
            elif angular_distance < -math.pi:
                angular_distance += 2 * math.pi
            cmd_vel.angular.z = 4.0 * angular_distance
        else:
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
            self.call_catch_turtle(self.alive_turtle_.name)
            self.alive_turtle_ = None

        self.publish_cmd_vel_.publish(cmd_vel)

    def call_catch_turtle(self, turtle_name):
        request = CatchTurtle.Request()
        request.name = turtle_name

        future = self.catch_turtle_client_.call_async(request)
        future.add_done_callback(partial(self.callback_call_catch_turtle, turtle_name=turtle_name))

    def callback_call_catch_turtle(self, future, turtle_name):
        response: CatchTurtle.Response = future.result()
        if not response.success:
            self.get_logger().info("this " + turtle_name + " could not be removed")


def main(args=None):
    rclpy.init(args=args)
    node = catchturtlenode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()





# #!/usr/bin/env python3
# import math
# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# from turtlesim.msg import Pose
# from turtle_interface.msg import TurtleArray
# from turtle_interface.msg import Turtle
# from turtle_interface.srv import CatchTurtle
# from functools import partial

# class catchturtlenode(Node):
#     def __init__(self):
#         super().__init__("catch_turtle")
#         self.pose_ = None
#         self.alive_turtle_: Turtle = None
#         self.subscribe_pose_= self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 10)
#         self.publish_cmd_vel_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
#         self.subscribe_alive_turtle_ = self.create_subscription(TurtleArray, "/alive_turtles", self.alive_turtle_callback, 10)
#         self.timer_ = self.create_timer(0.01, self.timer_callback)
#         self.catch_turtle_client_ = self.create_client(CatchTurtle, "catch_turtle")
#         while not self.catch_turtle_client_.wait_for_service(timeout_sec=1.0):
#             self.get_logger().info("Waiting for catch_turtle service...")  


#     def pose_callback(self, msg: Pose):
#         self.pose_ = msg

#     def alive_turtle_callback(self, msg: TurtleArray):
#         if len(msg.turtles) > 0:
#             self.alive_turtle_ = msg.turtles[0]


#     def timer_callback(self):
#         if self.pose_ is None or self.alive_turtle_ == None:
#             return

#         # Calculate the distance to the target
#         dx = self.alive_turtle_.x - self.pose_.x
#         dy = self.alive_turtle_.y - self.pose_.y
#         distance = math.hypot(dx, dy)

#         # Create a Twist message
#         cmd_vel = Twist()
#         if distance > 0.1: 
#             cmd_vel.linear.x = 2.0 * distance
#             angular_distance = math.atan2(dy, dx) - self.pose_.theta
#             if angular_distance > math.pi:
#                 angular_distance -= 2 * math.pi
#             elif angular_distance < -math.pi:
#                 angular_distance += 2 * math.pi
#             cmd_vel.angular.z = 4.0 * angular_distance
#         else:
#             cmd_vel.linear.x = 0.0
#             cmd_vel.angular.z = 0.0
#             self.call_catch_turtle(self.alive_turtle_.name)
#             self.alive_turtle_ = None

#         self.publish_cmd_vel_.publish(cmd_vel)

#     def call_catch_turtle(self, turtle_name):
#         request = CatchTurtle.Request()
#         request.name = turtle_name
    
#         future = self.catch_turtle_client_.call_async(request)
#         future.add_done_callback(partial(self.callback_catch_turtle, turtle_name=turtle_name))
            
#     def callback_call_catch_turtle(self, future, turtle_name):
#         response: CatchTurtle.Response = future.result()
#             if not response.success:
#             self.get_logger().info("this " + turtle_name + "could not be removed")

# def main(args=None):
#     rclpy.init(args=args)
#     node = catchturtlenode()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()