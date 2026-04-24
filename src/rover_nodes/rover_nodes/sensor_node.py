import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "10.0.0.246"
MQTT_TOPIC = "rover/sensors"

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        
        self.front_pub = self.create_publisher(Float32, 'sensor/front', 10)
        self.left_pub  = self.create_publisher(Float32, 'sensor/left',  10)
        self.right_pub = self.create_publisher(Float32, 'sensor/right', 10)
        self.imu_pub   = self.create_publisher(String,  'sensor/imu',   10)
        self.gps_pub   = self.create_publisher(String,  'sensor/gps',   10)
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.mqtt_callback
        self.mqtt_client.connect(MQTT_BROKER, 1883, 60)
        self.mqtt_client.subscribe(MQTT_TOPIC)
        self.mqtt_client.loop_start()
        
        self.get_logger().info("Sensor node started!")

    def mqtt_callback(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            
            front_msg = Float32()
            front_msg.data = float(data['front'])
            self.front_pub.publish(front_msg)
            
            left_msg = Float32()
            left_msg.data = float(data['left'])
            self.left_pub.publish(left_msg)
            
            right_msg = Float32()
            right_msg.data = float(data['right'])
            self.right_pub.publish(right_msg)
            
            imu_msg = String()
            imu_msg.data = f"ax:{data['ax']} ay:{data['ay']} az:{data['az']} gx:{data['gx']} gy:{data['gy']} gz:{data['gz']}"
            self.imu_pub.publish(imu_msg)
            
            gps_msg = String()
            gps_msg.data = str(data['gps'])
            self.gps_pub.publish(gps_msg)
            
            self.get_logger().info(
                f"F:{data['front']:.1f} L:{data['left']:.1f} R:{data['right']:.1f}"
            )
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
