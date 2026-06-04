#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ExploratorAutonom(Node):
    def __init__(self):
        super().__init__('explorator_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(LaserScan, '/scan', self.listener_callback, 10)
        
        # --- PARAMETRI CONTROL ---
        self.viteza_mers = 0.2
        self.distanta_siguranta = 0.8  # Referința noastră (unde vrem să stea robotul)

        # --- PARTEA DE MATLAB (Se execută o singură dată) ---
        # Creăm fișierul fizic pe "hard disk-ul" containerului
        self.fisier_date = open('date_pid.csv', 'w')
        self.fisier_date.write('timp,eroare\n') # Capul de tabel
        self.start_time = self.get_clock().now()

    def listener_callback(self, msg):
        # 1. Citim distanța din fața robotului
        fata = msg.ranges[160:200]
        distante_valide = [d for d in fata if d > 0.1]
        dist_min = min(distante_valide) if distante_valide else 10.0

        # 2. CALCULĂM EROAREA (Foarte important pentru MATLAB!)
        # Eroarea este diferența dintre unde suntem și unde vrem să fim
        eroare = dist_min - self.distanta_siguranta

        # 3. SALVĂM DATELE (Se execută la fiecare scanare laser)
        acum = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        self.fisier_date.write(f'{acum},{eroare}\n')

        # 4. LOGICA DE MIȘCARE
        msg_cmd = Twist()
        if dist_min < self.distanta_siguranta:
            self.get_logger().info(f'Obstacol! Eroare: {eroare:.2f}')
            msg_cmd.linear.x = 0.0
            msg_cmd.angular.z = 0.5 
        else:
            msg_cmd.linear.x = self.viteza_mers
            msg_cmd.angular.z = 0.0

        self.publisher_.publish(msg_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = ExploratorAutonom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Când apeși CTRL+C, închidem fișierul corect ca să se salveze datele
        node.fisier_date.close()
        node.get_logger().info('Datele au fost salvate în date_pid.csv!')
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()