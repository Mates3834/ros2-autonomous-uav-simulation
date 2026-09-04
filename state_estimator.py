import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64

class StateEstimator(Node):
    def __init__(self):
        super().__init__('state_estimator')
        self.pub=self.create_publisher(Vector3,'/uav/state_estimate',10)
        self.x=None; self.y=None; self.yaw=0.; self.alpha=0.25
        self.create_subscription(Vector3,'/uav/sensor/gps',self.gps_cb,10)
        self.create_subscription(Float64,'/uav/sensor/imu_yaw',self.imu_cb,10)

    def imu_cb(self,msg): self.yaw=float(msg.data)

    def gps_cb(self,msg):
        if self.x is None: self.x,self.y=msg.x,msg.y
        else:
            self.x=(1-self.alpha)*self.x+self.alpha*msg.x
            self.y=(1-self.alpha)*self.y+self.alpha*msg.y
        out=Vector3(); out.x=self.x; out.y=self.y; out.z=self.yaw; self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args); n=StateEstimator(); rclpy.spin(n); n.destroy_node(); rclpy.shutdown()
