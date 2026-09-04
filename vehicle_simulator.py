import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3

class VehicleSimulator(Node):
    def __init__(self):
        super().__init__('vehicle_simulator')
        self.pub = self.create_publisher(Vector3, '/uav/ground_truth', 10)
        self.create_subscription(Twist, '/uav/cmd_vel', self.cmd_cb, 10)
        self.dt=0.05; self.x=0.; self.y=0.; self.yaw=0.; self.speed=5.; self.yaw_rate=0.
        self.create_timer(self.dt, self.step)

    def cmd_cb(self,msg):
        self.speed=max(0., min(15., float(msg.linear.x)))
        self.yaw_rate=max(-1., min(1., float(msg.angular.z)))

    def step(self):
        self.yaw += self.yaw_rate*self.dt
        self.x += self.speed*math.cos(self.yaw)*self.dt
        self.y += self.speed*math.sin(self.yaw)*self.dt
        msg=Vector3(); msg.x=self.x; msg.y=self.y; msg.z=self.yaw
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args); n=VehicleSimulator(); rclpy.spin(n); n.destroy_node(); rclpy.shutdown()
