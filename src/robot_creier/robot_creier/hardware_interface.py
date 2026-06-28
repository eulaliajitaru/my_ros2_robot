#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

try:
    from gpiozero import Motor
    from gpiozero.pins.lgpio import LGPIOFactory
    GPIO_OK = True
except Exception:
    GPIO_OK = False

MAX_SPEED = 0.4
WHEEL_SEPARATION = 0.18

class MotorDriver(Node):
    def __init__(self):
        super().__init__('motor_driver')
        if GPIO_OK:
            factory = LGPIOFactory()
            self.motor_l = Motor(forward=17, backward=18, enable=23, pin_factory=factory)
            self.motor_r = Motor(forward=27, backward=22, enable=16, pin_factory=factory)
            self.get_logger().info('GPIO initializat OK')
        else:
            self.motor_l = self.motor_r = None
            self.get_logger().warn('GPIO indisponibil - mod simulare')
        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_cb, 10)
        self.get_logger().info('Motor driver pornit')

    def cmd_vel_cb(self, msg):
        v = msg.linear.x
        w = msg.angular.z
        v_l = max(-1.0, min(1.0, (v - w * WHEEL_SEPARATION / 2.0) / MAX_SPEED))
        v_r = max(-1.0, min(1.0, (v + w * WHEEL_SEPARATION / 2.0) / MAX_SPEED))
        self._set_motor(self.motor_l, v_l)
        self._set_motor(self.motor_r, v_r)

    def _set_motor(self, motor, speed):
        if motor is None:
            return
        if speed > 0.05:
            motor.forward(speed)
        elif speed < -0.05:
            motor.backward(-speed)
        else:
            motor.stop()

def main():
    rclpy.init()
    rclpy.spin(MotorDriver())
    rclpy.shutdown()
