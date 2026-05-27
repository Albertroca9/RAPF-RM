from dataclasses import dataclass
from enum import Enum


CONTAINER_CLASSES = (
    "paper_cardboard",
    "plastic_metal_carton",
    "glass",
    "organic",
    "residual",
)


class SafetyClass(str, Enum):
    PERSON = "person"
    OBSTACLE = "obstacle"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DetectionClassMapper:
    waste_aliases: dict[str, str]
    obstacle_labels: frozenset[str]

    @classmethod
    def default(cls) -> "DetectionClassMapper":
        return cls(
            waste_aliases={
                "aluminium foil": "plastic_metal_carton",
                "banana peel": "organic",
                "battery": "residual",
                "blister pack": "plastic_metal_carton",
                "bottle": "plastic_metal_carton",
                "bottle cap": "plastic_metal_carton",
                "broken glass": "glass",
                "can": "plastic_metal_carton",
                "cardboard": "paper_cardboard",
                "carton": "plastic_metal_carton",
                "cigarette": "residual",
                "cup": "residual",
                "drink carton": "plastic_metal_carton",
                "food waste": "organic",
                "glass": "glass",
                "glass bottle": "glass",
                "metal": "plastic_metal_carton",
                "metal bottle cap": "plastic_metal_carton",
                "paper": "paper_cardboard",
                "paper bag": "paper_cardboard",
                "paper straw": "paper_cardboard",
                "plastic": "plastic_metal_carton",
                "plastic bag": "plastic_metal_carton",
                "plastic bottle": "plastic_metal_carton",
                "plastic container": "plastic_metal_carton",
                "plastic film": "plastic_metal_carton",
                "pop tab": "plastic_metal_carton",
                "straw": "residual",
                "styrofoam": "residual",
                "unlabeled litter": "residual",
                "wrapper": "residual",
            },
            obstacle_labels=frozenset(
                {
                    "backpack",
                    "bench",
                    "chair",
                    "cupboard",
                    "dining table",
                    "door",
                    "sofa",
                    "table",
                    "wall",
                }
            ),
        )

    def map_waste_class(self, source_class: str) -> str:
        normalized = _normalize(source_class)
        if normalized in self.waste_aliases:
            return self.waste_aliases[normalized]
        for key, container in self.waste_aliases.items():
            if key in normalized:
                return container
        return "residual"

    def map_non_waste_label(self, label: str) -> SafetyClass:
        normalized = _normalize(label)
        if normalized == "person":
            return SafetyClass.PERSON
        if normalized in self.obstacle_labels:
            return SafetyClass.OBSTACLE
        return SafetyClass.UNKNOWN


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())

