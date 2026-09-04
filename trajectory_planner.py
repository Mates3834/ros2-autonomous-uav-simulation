import math, time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

class TrajectoryPlanner(Node):
    def __init__(self):
        super().__init__('trajectory_planner')
        self.pub=self.create_publisher(Vector3,'/uav/reference',10)
        self.t0=time.monotonic()
        self.create_timer(0.1,self.tick)

    def tick(self):
        t=time.monotonic()-self.t0
        msg=Vector3()
        msg.x=6.0*t
        msg.y=20.0*math.sin(0.08*t)
        msg.z=0.0
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args); n=TrajectoryPlanner(); rclpy.spin(n); n.destroy_node(); rclpy.shutdown()
