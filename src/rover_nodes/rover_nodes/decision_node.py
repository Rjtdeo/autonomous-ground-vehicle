import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import threading

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')

        self.create_subscription(Float32, 'sensor/front', self.front_callback, 10)
        self.create_subscription(Float32, 'sensor/left',  self.left_callback,  10)
        self.create_subscription(Float32, 'sensor/right', self.right_callback, 10)

        self.cmd_pub = self.create_publisher(String, 'cmd/motor', 10)

        self.front = -1.0
        self.left  = -1.0
        self.right = -1.0
        self.running = False

        self.create_timer(0.2, self.make_decision)

        self.input_thread = threading.Thread(target=self.read_input, daemon=True)
        self.input_thread.start()

        self.get_logger().info("Decision node ready! Type START or STOP")

    def read_input(self):
        while True:
            try:
                cmd = input("").strip().upper()
                if cmd == "START":
                    self.running = True
                    self.get_logger().info("Rover STARTED!")
                elif cmd == "STOP":
                    self.running = False
                    self.send_command("STOP")
                    self.get_logger().info("Rover STOPPED!")
            except:
                pass

    def front_callback(self, msg): self.front = msg.data
    def left_callback(self, msg):  self.left  = msg.data
    def right_callback(self, msg): self.right = msg.data

    def send_command(self, cmd):
        msg = String()
        msg.data = cmd
        self.cmd_pub.publish(msg)

    def make_decision(self):
        if not self.running:
            return

        front = self.front if self.front > 0 else 999
        left  = self.left  if self.left  > 0 else 999
        right = self.right if self.right > 0 else 999

        # Emergency stop
        if front < 20:
            self.send_command("STOP")
            self.get_logger().info(f"EMERGENCY STOP! Front:{front:.0f}cm")
            return

        # Front obstacle
        if front < 50:
            if right > 20:
                self.send_command("TURN_RIGHT")
                self.get_logger().info(f"Front blocked → TURN_RIGHT")
            else:
                self.send_command("TURN_LEFT")
                self.get_logger().info(f"Front+Right blocked → TURN_LEFT")
            return

        # Right obstacle
        if right < 20:
            self.send_command("TURN_LEFT")
            self.get_logger().info(f"Right:{right:.0f}cm → TURN_LEFT")
            return

        # Left obstacle
        if left < 20:
            self.send_command("TURN_RIGHT")
            self.get_logger().info(f"Left:{left:.0f}cm → TURN_RIGHT")
            return

        # All clear
        self.send_command("FORWARD")
        self.get_logger().info(f"FORWARD F:{front:.0f} L:{left:.0f} R:{right:.0f}")

def main(args=None):
    rclpy.init(args=args)
    node = DecisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
