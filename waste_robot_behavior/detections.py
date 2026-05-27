from dataclasses import dataclass
from math import sqrt

from .taxonomy import SafetyClass


@dataclass(frozen=True)
class Position3D:
    x: float
    y: float
    z: float

    def distance(self) -> float:
        return sqrt((self.x * self.x) + (self.y * self.y) + (self.z * self.z))


@dataclass(frozen=True)
class DetectedObject:
    label: str
    confidence: float
    position: Position3D | None = None
    container: str | None = None
    safety_class: SafetyClass | None = None

    @property
    def is_actionable_trash(self) -> bool:
        return self.container is not None and self.position is not None

