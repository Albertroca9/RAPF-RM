from dataclasses import dataclass
from enum import Enum


CONTAINER_CLASSES = (
    "paper_cardboard",
    "plastic_metal_carton",
    "glass",
    "organic",
    "residual",
)


TACO_CLASS_TO_CONTAINER = {
    "Aerosol": "plastic_metal_carton",
    "Aluminium blister pack": "plastic_metal_carton",
    "Aluminium foil": "plastic_metal_carton",
    "Battery": "residual",
    "Broken glass": "glass",
    "Carded blister pack": "plastic_metal_carton",
    "Cigarette": "residual",
    "Clear plastic bottle": "plastic_metal_carton",
    "Corrugated carton": "paper_cardboard",
    "Crisp packet": "residual",
    "Disposable food container": "residual",
    "Disposable plastic cup": "plastic_metal_carton",
    "Drink can": "plastic_metal_carton",
    "Drink carton": "plastic_metal_carton",
    "Egg carton": "paper_cardboard",
    "Foam cup": "residual",
    "Foam food container": "residual",
    "Food Can": "plastic_metal_carton",
    "Food waste": "organic",
    "Garbage bag": "plastic_metal_carton",
    "Glass bottle": "glass",
    "Glass cup": "glass",
    "Glass jar": "glass",
    "Magazine paper": "paper_cardboard",
    "Meal carton": "plastic_metal_carton",
    "Metal bottle cap": "plastic_metal_carton",
    "Metal lid": "plastic_metal_carton",
    "Normal paper": "paper_cardboard",
    "Other carton": "plastic_metal_carton",
    "Other plastic": "plastic_metal_carton",
    "Other plastic bottle": "plastic_metal_carton",
    "Other plastic container": "plastic_metal_carton",
    "Other plastic cup": "plastic_metal_carton",
    "Other plastic wrapper": "plastic_metal_carton",
    "Paper bag": "paper_cardboard",
    "Paper cup": "paper_cardboard",
    "Paper straw": "paper_cardboard",
    "Pizza box": "paper_cardboard",
    "Plastic bottle cap": "plastic_metal_carton",
    "Plastic film": "plastic_metal_carton",
    "Plastic glooves": "plastic_metal_carton",
    "Plastic lid": "plastic_metal_carton",
    "Plastic straw": "residual",
    "Plastic utensils": "residual",
    "Polypropylene bag": "plastic_metal_carton",
    "Pop tab": "plastic_metal_carton",
    "Rope & strings": "residual",
    "Scrap metal": "plastic_metal_carton",
    "Shoe": "residual",
    "Single-use carrier bag": "plastic_metal_carton",
    "Six pack rings": "plastic_metal_carton",
    "Squeezable tube": "plastic_metal_carton",
    "Spread tub": "plastic_metal_carton",
    "Styrofoam piece": "residual",
    "Tissues": "residual",
    "Toilet tube": "paper_cardboard",
    "Tupperware": "plastic_metal_carton",
    "Unlabeled litter": "residual",
    "Wrapping paper": "paper_cardboard",
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
