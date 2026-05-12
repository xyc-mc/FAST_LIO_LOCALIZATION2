#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import tf2_ros
from geometry_msgs.msg import TransformStamped


class TransformFusion(Node):
    def __init__(self):
        super().__init__("transform_fusion")

        self.cur_map_to_odom = None
        self.declare_parameter("publish_frequency", 30.0)
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("odom_init_frame", "camera_init")
        self.map_frame = self.get_parameter("map_frame").value
        self.odom_init_frame = self.get_parameter("odom_init_frame").value

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.create_subscription(Odometry, "/map_to_odom", self.cb_save_map_to_odom, 1)

        frequency = self.get_parameter("publish_frequency").value
        self.timer = self.create_timer(1.0 / frequency, self.transform_fusion)

    def transform_fusion(self):
        transform_stamped_msg = TransformStamped()
        transform_stamped_msg.header.stamp = self.get_clock().now().to_msg()
        transform_stamped_msg.header.frame_id = self.map_frame
        transform_stamped_msg.child_frame_id = self.odom_init_frame

        transform_stamped_msg.transform.rotation.w = 1.0
        if self.cur_map_to_odom is not None:
            pose = self.cur_map_to_odom.pose.pose
            transform_stamped_msg.transform.translation.x = pose.position.x
            transform_stamped_msg.transform.translation.y = pose.position.y
            transform_stamped_msg.transform.translation.z = pose.position.z

            transform_stamped_msg.transform.rotation = pose.orientation

        self.tf_broadcaster.sendTransform(transform_stamped_msg)

    def cb_save_map_to_odom(self, msg):
        self.cur_map_to_odom = msg


def main(args=None):
    rclpy.init(args=args)
    node = TransformFusion()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
