import unittest

from waste_robot_behavior.taxonomy import (
    COCO_CLASS_TO_CONTAINER,
    CONTAINER_CLASSES,
    DetectionClassMapper,
    SafetyClass,
    TACO_CLASS_TO_CONTAINER,
)


class TaxonomyTest(unittest.TestCase):
    def test_container_classes_are_the_project_four_bins(self):
        self.assertEqual(
            CONTAINER_CLASSES,
            (
                "paper",
                "plastic",
                "glass",
                "residual",
            ),
        )

    def test_maps_taco_classes_to_project_bins(self):
        mapper = DetectionClassMapper.default()
        cases = [
            ("Cardboard", "paper"),
            ("paper", "paper"),
            ("Plastic bottle", "plastic"),
            ("Metal bottle cap", "plastic"),
            ("Drink carton", "plastic"),
            ("Glass bottle", "glass"),
            ("Food waste", "residual"),
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

    def test_specific_taco_60_classes_map_to_four_bins(self):
        mapper = DetectionClassMapper.default()
        cases = [
            ("Clear plastic bottle", "plastic"),
            ("Food Can", "plastic"),
            ("Aerosol", "plastic"),
            ("Corrugated carton", "paper"),
            ("Pizza box", "paper"),
            ("Glass jar", "glass"),
            ("Banana peel", "residual"),
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

    def test_maps_conservative_coco_classes_to_project_bins(self):
        mapper = DetectionClassMapper.default()
        cases = [
            ("book", "paper"),
            ("bottle", "plastic"),
            ("cup", "plastic"),
            ("bowl", "plastic"),
            ("fork", "plastic"),
            ("knife", "plastic"),
            ("spoon", "plastic"),
            ("toothbrush", "plastic"),
            ("frisbee", "plastic"),
            ("sports ball", "plastic"),
            ("wine glass", "glass"),
            ("vase", "glass"),
            ("banana", "residual"),
            ("apple", "residual"),
            ("pizza", "residual"),
        ]

        for label, expected in cases:
            with self.subTest(label=label):
                self.assertEqual(mapper.map_coco_class(label), expected)

    def test_ambiguous_coco_classes_are_not_pickup_targets(self):
        mapper = DetectionClassMapper.default()

        for label in ("cell phone", "remote", "laptop"):
            with self.subTest(label=label):
                self.assertIsNone(mapper.map_coco_class(label))
                self.assertIsNone(mapper.map_runtime_container(label))

    def test_explicit_coco_mapping_is_subset_of_project_bins(self):
        self.assertTrue(set(COCO_CLASS_TO_CONTAINER.values()).issubset(set(CONTAINER_CLASSES)))


if __name__ == "__main__":
    unittest.main()
