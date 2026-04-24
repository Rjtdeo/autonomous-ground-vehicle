import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time

class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        
        self.create_subscription(String, 'cmd/motor', self.cmd_callback, 10)
        
        try:
            self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            time.sleep(2)
            self.get_logger().info("Arduino connected!")
        except Exception as e:
            self.get_logger().error(f"Arduino failed: {e}")
            self.arduino = None

    def cmd_callback(self, msg):
        cmd = msg.data
        self.get_logger().info(f"CMD: {cmd}")
        if self.arduino:
            try:
                self.arduino.write(f"{cmd}\n".encode())
            except Exception as e:
                self.get_logger().error(f"Serial error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = MotorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
