from dataclasses import dataclass
from enum import Enum


CONTAINER_CLASSES = (
    "paper",
    "plastic",
    "glass",
    "residual",
)


TACO_CLASS_TO_CONTAINER = {
    "Aerosol": "plastic",
    "Aluminium blister pack": "plastic",
    "Aluminium foil": "plastic",
    "Battery": "residual",
    "Broken glass": "glass",
    "Carded blister pack": "plastic",
    "Cigarette": "residual",
    "Clear plastic bottle": "plastic",
    "Corrugated carton": "paper",
    "Crisp packet": "residual",
    "Disposable food container": "residual",
    "Disposable plastic cup": "plastic",
    "Drink can": "plastic",
    "Drink carton": "plastic",
    "Egg carton": "paper",
    "Foam cup": "residual",
    "Foam food container": "residual",
    "Food Can": "plastic",
    "Food waste": "residual",
    "Garbage bag": "plastic",
    "Glass bottle": "glass",
    "Glass cup": "glass",
    "Glass jar": "glass",
    "Magazine paper": "paper",
    "Meal carton": "plastic",
    "Metal bottle cap": "plastic",
    "Metal lid": "plastic",
    "Normal paper": "paper",
    "Other carton": "plastic",
    "Other plastic": "plastic",
    "Other plastic bottle": "plastic",
    "Other plastic container": "plastic",
    "Other plastic cup": "plastic",
    "Other plastic wrapper": "plastic",
    "Paper bag": "paper",
    "Paper cup": "paper",
    "Paper straw": "paper",
    "Pizza box": "paper",
    "Plastic bottle cap": "plastic",
    "Plastic film": "plastic",
    "Plastic glooves": "plastic",
    "Plastic lid": "plastic",
    "Plastic straw": "residual",
    "Plastic utensils": "residual",
    "Polypropylene bag": "plastic",
    "Pop tab": "plastic",
    "Rope & strings": "residual",
    "Scrap metal": "plastic",
    "Shoe": "residual",
    "Single-use carrier bag": "plastic",
    "Six pack rings": "plastic",
    "Squeezable tube": "plastic",
    "Spread tub": "plastic",
    "Styrofoam piece": "residual",
    "Tissues": "residual",
    "Toilet tube": "paper",
    "Tupperware": "plastic",
    "Unlabeled litter": "residual",
    "Wrapping paper": "paper",
}


COCO_CLASS_TO_CONTAINER = {
    "book": "paper",
    "bottle": "plastic",
    "wine glass": "glass",
    "apple": "residual",
    "banana": "residual",
    "broccoli": "residual",
    "cake": "residual",
    "carrot": "residual",
    "donut": "residual",
    "hot dog": "residual",
    "orange": "residual",
    "pizza": "residual",
    "sandwich": "residual",
}


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
                **{_normalize(source): container for source, container in TACO_CLASS_TO_CONTAINER.items()},
                "aluminium foil": "plastic",
                "banana peel": "residual",
                "battery": "residual",
                "blister pack": "plastic",
                "bottle": "plastic",
                "bottle cap": "plastic",
                "broken glass": "glass",
                "can": "plastic",
                "cardboard": "paper",
                "carton": "plastic",
                "cigarette": "residual",
                "cup": "residual",
                "drink carton": "plastic",
                "food waste": "residual",
                "glass": "glass",
                "glass bottle": "glass",
                "metal": "plastic",
                "metal bottle cap": "plastic",
                "paper": "paper",
                "paper bag": "paper",
                "paper straw": "paper",
                "plastic": "plastic",
                "plastic bag": "plastic",
                "plastic bottle": "plastic",
                "plastic container": "plastic",
                "plastic film": "plastic",
                "pop tab": "plastic",
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

    def map_coco_class(self, label: str) -> str | None:
        return COCO_CLASS_TO_CONTAINER.get(_normalize(label))

    def map_runtime_container(self, label: str) -> str | None:
        normalized = _normalize(label)
        if normalized in CONTAINER_CLASSES:
            return normalized
        return self.map_coco_class(label)

    def map_non_waste_label(self, label: str) -> SafetyClass:
        normalized = _normalize(label)
        if normalized == "person":
            return SafetyClass.PERSON
        if normalized in self.obstacle_labels:
            return SafetyClass.OBSTACLE
        return SafetyClass.UNKNOWN


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())
