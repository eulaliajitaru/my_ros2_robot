#!/usr/bin/env python3
"""
evitare_obstacole.py
--------------------
Nod ROS2 care citeste datele LiDAR si trimite comenzi de miscare
evitand obstacolele din fata robotului.

Fix-uri fata de versiunea initiala:
  - Verificare con 30 grade in FATA (nu spatele) robotului
  - Tratare valori inf si nan de la LiDAR
  - Logica de intoarcere cu directie aleasa in functie de spatiul liber lateral
"""

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class EvitareObstacole(Node):
    def __init__(self):
        super().__init__('nod_evitare_obstacole')

        # Parametri configurabili
        self.DISTANTA_PERICOL = 0.6    # metri - distanta la care oprim
        self.DISTANTA_ATENTIE = 1.0    # metri - distanta la care incetnim
        self.VITEZA_INAINTE   = 0.2    # m/s
        self.VITEZA_ROTATIE   = 0.5    # rad/s

        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info('Sistemul de evitare a obstacolelor a pornit!')

    def get_min_distance(self, ranges, index_start, index_end, total):
        """
        Returneaza distanta minima valida intr-un arc de cerc.
        Gestioneaza wrap-around (ex: 350..10 grade).
        """
        distante_valide = []
        i = index_start
        while i != index_end:
            val = ranges[i % total]
            if not math.isnan(val) and not math.isinf(val) and val > 0.0:
                distante_valide.append(val)
            i = (i + 1) % total
        return min(distante_valide) if distante_valide else float('inf')

    def scan_callback(self, msg):
        total = len(msg.ranges)  # 360 pentru RPLIDAR A1

        # ---- Calculam indecsi pentru arcuri ----
        # Index 0 = FATA robotului (conventia RPLIDAR A1)
        # Con fata: -15 .. +15 grade  (30 grade total)
        unghi_con = 15
        idx_fata_st  = total - unghi_con   # ex: 345
        idx_fata_dr  = unghi_con           # ex: 15

        # Lateral stanga: 60..120 grade
        idx_st_start = 60
        idx_st_end   = 120

        # Lateral dreapta: 240..300 grade
        idx_dr_start = 240
        idx_dr_end   = 300

        # ---- Distante minime pe fiecare zona ----
        dist_fata   = self.get_min_distance(msg.ranges, idx_fata_st, idx_fata_dr, total)
        dist_stanga = self.get_min_distance(msg.ranges, idx_st_start, idx_st_end, total)
        dist_dreapta= self.get_min_distance(msg.ranges, idx_dr_start, idx_dr_end, total)

        cmd = Twist()

        if dist_fata < self.DISTANTA_PERICOL:
            # OBSTACOL APROAPE - intoarce spre partea cu mai mult spatiu
            cmd.linear.x = 0.0
            if dist_stanga >= dist_dreapta:
                cmd.angular.z =  self.VITEZA_ROTATIE   # rotire stanga
                self.get_logger().warn(
                    f'OBSTACOL la {dist_fata:.2f}m! Rotesc STANGA (spatiu st={dist_stanga:.2f}m)')
            else:
                cmd.angular.z = -self.VITEZA_ROTATIE   # rotire dreapta
                self.get_logger().warn(
                    f'OBSTACOL la {dist_fata:.2f}m! Rotesc DREAPTA (spatiu dr={dist_dreapta:.2f}m)')

        elif dist_fata < self.DISTANTA_ATENTIE:
            # ZONA DE ATENTIE - incetineste
            factor = (dist_fata - self.DISTANTA_PERICOL) / (self.DISTANTA_ATENTIE - self.DISTANTA_PERICOL)
            cmd.linear.x = self.VITEZA_INAINTE * factor
            cmd.angular.z = 0.0
            self.get_logger().info(f'Atentie! Obstacol la {dist_fata:.2f}m. Incetinesc...')

        else:
            # DRUM LIBER
            cmd.linear.x = self.VITEZA_INAINTE
            cmd.angular.z = 0.0
            self.get_logger().info(f'Drum liber. Distanta fata: {dist_fata:.2f}m')

        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = EvitareObstacole()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
