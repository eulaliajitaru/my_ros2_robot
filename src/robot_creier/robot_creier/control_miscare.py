#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class ControlMiscare(Node):
    def __init__(self):
        super().__init__('nod_control_miscare')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.5 
        self.timer = self.create_timer(timer_period, self.trimite_comanda)
        self.get_logger().info('Creierul a pornit! Robotul primeste comenzi de miscare...')

    def trimite_comanda(self):
        msg = Twist()
        msg.linear.x = 0.2  
        msg.angular.z = 0.0 
        self.publisher_.publish(msg)
        self.get_logger().info(f'Trimit viteza: linear={msg.linear.x}, angular={msg.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    nod = ControlMiscare()
    rclpy.spin(nod) 
    nod.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()