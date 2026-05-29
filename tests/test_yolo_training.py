import unittest
from pathlib import Path

from waste_robot_behavior.dataset.train_yolov8 import build_training_kwargs
from waste_robot_behavior.dataset.train_yolov8 import split_model_from_training_kwargs


class YoloTrainingTest(unittest.TestCase):
    def test_builds_default_yolov8n_training_arguments(self):
        kwargs = build_training_kwargs(Path("data/mendeley_yolo_4bins/data.yaml"))

        self.assertEqual(kwargs["data"], "data/mendeley_yolo_4bins/data.yaml")
        self.assertEqual(kwargs["model"], "yolov8n.pt")
        self.assertEqual(kwargs["imgsz"], 640)
        self.assertEqual(kwargs["epochs"], 30)
        self.assertEqual(kwargs["project"], "runs/waste_yolov8")
        self.assertEqual(kwargs["name"], "yolov8n_mendeley_4bins")

    def test_splits_model_without_mutating_training_arguments(self):
        kwargs = build_training_kwargs(Path("data/mendeley_yolo_4bins/data.yaml"))

        model_path, train_kwargs = split_model_from_training_kwargs(kwargs)

        self.assertEqual(model_path, "yolov8n.pt")
        self.assertNotIn("model", train_kwargs)
        self.assertIn("model", kwargs)


if __name__ == "__main__":
    unittest.main()
