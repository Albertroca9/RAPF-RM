import unittest

from waste_robot_behavior.taxonomy import (
    CONTAINER_CLASSES,
    DetectionClassMapper,
    SafetyClass,
    TACO_CLASS_TO_CONTAINER,
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

    def test_explicit_taco_60_mapping_is_complete_for_project_bins(self):
        expected_classes = {
            "Aerosol",
            "Aluminium blister pack",
            "Aluminium foil",
            "Battery",
            "Broken glass",
            "Carded blister pack",
            "Cigarette",
            "Clear plastic bottle",
            "Corrugated carton",
            "Crisp packet",
            "Disposable food container",
            "Disposable plastic cup",
            "Drink can",
            "Drink carton",
            "Egg carton",
            "Foam cup",
            "Foam food container",
            "Food Can",
            "Food waste",
            "Garbage bag",
            "Glass bottle",
            "Glass cup",
            "Glass jar",
            "Magazine paper",
            "Meal carton",
            "Metal bottle cap",
            "Metal lid",
            "Normal paper",
            "Other carton",
            "Other plastic",
            "Other plastic bottle",
            "Other plastic container",
            "Other plastic cup",
            "Other plastic wrapper",
            "Paper bag",
            "Paper cup",
            "Paper straw",
            "Pizza box",
            "Plastic bottle cap",
            "Plastic film",
            "Plastic glooves",
            "Plastic lid",
            "Plastic straw",
            "Plastic utensils",
            "Polypropylene bag",
            "Pop tab",
            "Rope & strings",
            "Scrap metal",
            "Shoe",
            "Single-use carrier bag",
            "Six pack rings",
            "Squeezable tube",
            "Spread tub",
            "Styrofoam piece",
            "Tissues",
            "Toilet tube",
            "Tupperware",
            "Unlabeled litter",
            "Wrapping paper",
        }

        self.assertEqual(set(TACO_CLASS_TO_CONTAINER), expected_classes)
        self.assertTrue(set(TACO_CLASS_TO_CONTAINER.values()).issubset(set(CONTAINER_CLASSES)))

    def test_specific_taco_60_classes_map_to_five_bins(self):
        mapper = DetectionClassMapper.default()
        cases = [
            ("Clear plastic bottle", "plastic_metal_carton"),
            ("Food Can", "plastic_metal_carton"),
            ("Aerosol", "plastic_metal_carton"),
            ("Corrugated carton", "paper_cardboard"),
            ("Pizza box", "paper_cardboard"),
            ("Glass jar", "glass"),
            ("Banana peel", "organic"),
            ("Battery", "residual"),
            ("Shoe", "residual"),
        ]

        for source_class, expected in cases:
            with self.subTest(source_class=source_class):
                self.assertEqual(mapper.map_waste_class(source_class), expected)

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
