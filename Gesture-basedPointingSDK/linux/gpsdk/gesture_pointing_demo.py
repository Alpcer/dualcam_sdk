"""
GesturePointing 的 ROS2 发布示例

把 GesturePointing 输出的 3D 关键点（相机系，米）和食指指向射线
包装成 PointCloud2 与 Marker 发布出去。

需要 rclpy、sensor_msgs、visualization_msgs、geometry_msgs。
"""

import struct
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from sensor_msgs.msg import PointCloud2, PointField
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import Header
from builtin_interfaces.msg import Time as TimeMsg

from gesture_pointing import GesturePointing


class HandMarkerNode(Node):
    def __init__(self):
        super().__init__("gesture_pointing_demo")

        sensor_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # 相机坐标系 frame_id，请按你的 URDF / TF 树改成合适的名字
        self.frame_id = "camera_left_link"
        self.ray_length_m = 10.0

        self.pc_pub = self.create_publisher(PointCloud2, "/camera/hand", sensor_qos)
        self.marker_pub = self.create_publisher(Marker, "/camera/hand_pointing_line", sensor_qos)

        self.gesture = GesturePointing(
            model_path="gesture_recognizer.task",
            target_hand="any",           # 改成 'left' 可只选左手
            num_hands=1,
        )
        self.gesture.register_callback(self.on_gesture)
        self.gesture.start()             # 默认 cam_path 走 rgbsdk 平台默认

        self.get_logger().info("GesturePointing demo started.")

    # ------------------------------------------------------------------ #
    #  SDK 回调
    # ------------------------------------------------------------------ #
    def on_gesture(self, points_3d, ray_origin, ray_direction, timestamp):
        header = Header()
        header.frame_id = self.frame_id
        header.stamp = self._sec_to_ros_time(timestamp)

        if points_3d is None:
            self._clear_marker(header)
            return

        self._publish_cloud(points_3d, header)

        if ray_origin is not None and ray_direction is not None:
            self._publish_ray(ray_origin, ray_direction, header)
        else:
            self._clear_marker(header)

    # ------------------------------------------------------------------ #
    #  发布工具
    # ------------------------------------------------------------------ #
    @staticmethod
    def _sec_to_ros_time(ts_sec: float) -> TimeMsg:
        t = TimeMsg()
        t.sec = int(ts_sec)
        t.nanosec = int((ts_sec - t.sec) * 1e9)
        return t

    @staticmethod
    def _rgb_to_float(r, g, b):
        rgb_int = (int(r) << 16) | (int(g) << 8) | int(b)
        return struct.unpack("f", struct.pack("I", rgb_int))[0]

    def _publish_cloud(self, points_3d: np.ndarray, header: Header):
        NORMAL_RGB = (255, 255, 255)
        SPECIAL_RGB = (255, 0, 0)

        rows = []
        for i, (x, y, z) in enumerate(points_3d):
            r, g, b = SPECIAL_RGB if 5 <= i <= 8 else NORMAL_RGB
            rows.append([x, y, z, self._rgb_to_float(r, g, b)])
        pts = np.asarray(rows, dtype=np.float32)

        msg = PointCloud2()
        msg.header = header
        msg.height = 1
        msg.width = pts.shape[0]
        msg.is_dense = True
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * pts.shape[0]
        msg.fields = [
            PointField(name="x",   offset=0,  datatype=PointField.FLOAT32, count=1),
            PointField(name="y",   offset=4,  datatype=PointField.FLOAT32, count=1),
            PointField(name="z",   offset=8,  datatype=PointField.FLOAT32, count=1),
            PointField(name="rgb", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.data = pts.tobytes()
        self.pc_pub.publish(msg)

    def _publish_ray(self, origin: np.ndarray, direction: np.ndarray, header: Header):
        end = origin + direction * self.ray_length_m

        marker = Marker()
        marker.header = header
        marker.ns = "finger_direction"
        marker.id = 0
        marker.type = Marker.ARROW
        marker.action = Marker.ADD

        p0 = Point()
        p0.x, p0.y, p0.z = float(origin[0]), float(origin[1]), float(origin[2])
        p1 = Point()
        p1.x, p1.y, p1.z = float(end[0]), float(end[1]), float(end[2])
        marker.points = [p0, p1]

        marker.scale.x = 0.02
        marker.scale.y = 0.06
        marker.scale.z = 0.06
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        marker.lifetime.sec = 0
        marker.lifetime.nanosec = 1_000_000_000
        self.marker_pub.publish(marker)

    def _clear_marker(self, header: Header):
        marker = Marker()
        marker.header = header
        marker.ns = "finger_direction"
        marker.id = 0
        marker.action = Marker.DELETE
        self.marker_pub.publish(marker)

    # ------------------------------------------------------------------ #
    def destroy(self):
        try:
            self.gesture.stop()
        finally:
            self.destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HandMarkerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy()
        rclpy.shutdown()


if __name__ == "__main__":
    main()