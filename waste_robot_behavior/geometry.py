from dataclasses import dataclass
from math import isfinite
from statistics import median
from typing import Sequence

from .detections import Position3D


@dataclass(frozen=True)
class BoundingBox:
    xmin: int
    ymin: int
    xmax: int
    ymax: int

    @property
    def center(self) -> tuple[int, int]:
        return ((self.xmin + self.xmax) // 2, (self.ymin + self.ymax) // 2)


@dataclass(frozen=True)
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float


class DepthEstimator:
    def __init__(self, intrinsics: CameraIntrinsics, window_radius: int = 2):
        self.intrinsics = intrinsics
        self.window_radius = window_radius

    def estimate(self, bbox: BoundingBox, depth_image: Sequence[Sequence[float]]) -> Position3D | None:
        u, v = bbox.center
        depth = self._median_depth(depth_image, u, v)
        if depth is None:
            return None

        x = ((u - self.intrinsics.cx) * depth) / self.intrinsics.fx
        y = ((v - self.intrinsics.cy) * depth) / self.intrinsics.fy
        return Position3D(x=x, y=y, z=depth)

    def _median_depth(self, depth_image: Sequence[Sequence[float]], u: int, v: int) -> float | None:
        if not depth_image:
            return None
        height = len(depth_image)
        width = len(depth_image[0]) if height else 0
        values: list[float] = []
        for y in range(max(0, v - self.window_radius), min(height, v + self.window_radius + 1)):
            row = depth_image[y]
            for x in range(max(0, u - self.window_radius), min(width, u + self.window_radius + 1)):
                value = float(row[x])
                if isfinite(value) and value > 0.0:
                    values.append(value)
        if not values:
            return None
        return float(median(values))

