import unittest

from waste_robot_behavior.taxonomy import (
    CONTAINER_CLASSES,
    DetectionClassMapper,
    SafetyClass,
)


class TaxonomyTest(unittest.TestCase):
    def test_container_classes_are_the_project_five_bins(self):
        self.assertEqual(
            CONTAINER_CLASSES,
            (
                "paper_cardboard",
                "plastic_metal_carton",
                "glass",
                "organic",
                "residual",
            ),
        )

    def test_maps_taco_classes_to_project_bins(self):
        mapper = DetectionClassMapper.default()
        cases = [
            ("Cardboard", "paper_cardboard"),
            ("paper", "paper_cardboard"),
            ("Plastic bottle", "plastic_metal_carton"),
            ("Metal bottle cap", "plastic_metal_carton"),
            ("Drink carton", "plastic_metal_carton"),
            ("Glass bottle", "glass"),
            ("Food waste", "organic"),
            ("Cigarette", "residual"),
        ]

        for source_class, expected in cases:
            with self.subTest(source_class=source_class):
                self.assertEqual(mapper.map_waste_class(source_class), expected)

    def test_unknown_waste_class_maps_to_residual_bin(self):
        mapper = DetectionClassMapper.default()

        self.assertEqual(mapper.map_waste_class("Unlabeled litter"), "residual")

    def test_non_waste_labels_are_safety_classes(self):
        mapper = DetectionClassMapper.default()
        cases = [
            ("person", SafetyClass.PERSON),
            ("Person", SafetyClass.PERSON),
            ("chair", SafetyClass.OBSTACLE),
            ("unknown", SafetyClass.UNKNOWN),
        ]

        for label, expected in cases:
            with self.subTest(label=label):
                self.assertEqual(mapper.map_non_waste_label(label), expected)


if __name__ == "__main__":
    unittest.main()
