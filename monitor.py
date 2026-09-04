import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64

class Monitor(Node):
    def __init__(self):
        super().__init__('monitor')
        self.state=None; self.ref=None
        self.pub=self.create_publisher(Float64,'/uav/tracking_error',10)
        self.create_subscription(Vector3,'/uav/state_estimate',self.s,10)
        self.create_subscription(Vector3,'/uav/reference',self.r,10)

    def s(self,m): self.state=m; self.publish_error()
    def r(self,m): self.ref=m

    def publish_error(self):
        if self.state is None or self.ref is None: return
        e=Float64()
        e.data=math.hypot(self.ref.x-self.state.x,self.ref.y-self.state.y)
        self.pub.publish(e)

def main(args=None):
    rclpy.init(args=args); n=Monitor(); rclpy.spin(n); n.destroy_node(); rclpy.shutdown()
