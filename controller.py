import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3, Twist

def wrap(a): return (a+math.pi)%(2*math.pi)-math.pi

class Controller(Node):
    def __init__(self):
        super().__init__('controller')
        self.state=None; self.ref=None
        self.pub=self.create_publisher(Twist,'/uav/cmd_vel',10)
        self.create_subscription(Vector3,'/uav/state_estimate',self.state_cb,10)
        self.create_subscription(Vector3,'/uav/reference',self.ref_cb,10)
        self.create_timer(0.05,self.control)

    def state_cb(self,m): self.state=m
    def ref_cb(self,m): self.ref=m

    def control(self):
        if self.state is None or self.ref is None: return
        dx=self.ref.x-self.state.x; dy=self.ref.y-self.state.y
        desired=math.atan2(dy,dx)
        err=wrap(desired-self.state.z)
        distance=math.hypot(dx,dy)
        msg=Twist()
        msg.linear.x=max(2.0,min(10.0,0.6*distance))
        msg.angular.z=max(-1.0,min(1.0,2.0*err))
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args); n=Controller(); rclpy.spin(n); n.destroy_node(); rclpy.shutdown()
