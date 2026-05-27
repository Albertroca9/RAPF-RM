import math
import unittest

from waste_robot_behavior.geometry import BoundingBox, CameraIntrinsics, DepthEstimator


class GeometryTest(unittest.TestCase):
    def test_estimates_3d_position_from_bbox_center_and_depth(self):
        estimator = DepthEstimator(CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0))
        bbox = BoundingBox(xmin=310, ymin=230, xmax=330, ymax=250)
        depth_image = [[2.0 for _ in range(640)] for _ in range(480)]

        position = estimator.estimate(bbox, depth_image)

        self.assertIsNotNone(position)
        self.assertEqual(position.x, 0.0)
        self.assertEqual(position.y, 0.0)
        self.assertEqual(position.z, 2.0)

    def test_uses_median_valid_depth_around_bbox_center(self):
        estimator = DepthEstimator(CameraIntrinsics(fx=500.0, fy=500.0, cx=320.0, cy=240.0))
        bbox = BoundingBox(xmin=318, ymin=238, xmax=322, ymax=242)
        depth_image = [[float("nan") for _ in range(640)] for _ in range(480)]
        depth_image[239][320] = 1.2
        depth_image[240][320] = 1.0
        depth_image[241][320] = 1.4

        position = estimator.estimate(bbox, depth_image)

        self.assertIsNotNone(position)
        self.assertEqual(position.z, 1.2)

    def test_returns_none_when_depth_has_no_valid_measurement(self):
        estimator = DepthEstimator(CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0))
        bbox = BoundingBox(xmin=310, ymin=230, xmax=330, ymax=250)
        depth_image = [[math.nan for _ in range(640)] for _ in range(480)]

        self.assertIsNone(estimator.estimate(bbox, depth_image))


if __name__ == "__main__":
    unittest.main()
