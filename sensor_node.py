import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        self.rng=np.random.default_rng(5)
        self.gps=self.create_publisher(Vector3,'/uav/sensor/gps',10)
        self.imu=self.create_publisher(Float64,'/uav/sensor/imu_yaw',10)
        self.create_subscription(Vector3,'/uav/ground_truth',self.cb,10)

    def cb(self,msg):
        g=Vector3()
        g.x=msg.x+float(self.rng.normal(0,1.5))
        g.y=msg.y+float(self.rng.normal(0,1.5))
        self.gps.publish(g)
        y=Float64(); y.data=msg.z+float(self.rng.normal(0,0.02)); self.imu.publish(y)

def main(args=None):
    rclpy.init(args=args); n=SensorNode(); rclpy.spin(n); n.destroy_node(); rclpy.shutdown()
