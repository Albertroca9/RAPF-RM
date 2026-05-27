import json
import tempfile
import unittest
from pathlib import Path

from waste_robot_behavior.dataset.taco_to_yolo import convert_taco_annotations


class TacoConversionTest(unittest.TestCase):
    def test_converts_taco_coco_annotations_to_yolo_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            annotation_path = root / "annotations.json"
            output_dir = root / "labels"
            annotation_path.write_text(
                json.dumps(
                    {
                        "images": [{"id": 1, "file_name": "batch_1/img.jpg", "width": 100, "height": 50}],
                        "categories": [{"id": 7, "name": "Plastic bottle"}],
                        "annotations": [{"image_id": 1, "category_id": 7, "bbox": [10, 5, 20, 10]}],
                    }
                ),
                encoding="utf-8",
            )

            summary = convert_taco_annotations(annotation_path, output_dir)

            label_file = output_dir / "batch_1_img.txt"
            self.assertEqual(summary.images, 1)
            self.assertEqual(summary.annotations, 1)
            self.assertEqual(
                label_file.read_text(encoding="utf-8").strip(),
                "1 0.200000 0.200000 0.200000 0.200000",
            )

    def test_skips_annotations_without_known_image(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            annotation_path = root / "annotations.json"
            output_dir = root / "labels"
            annotation_path.write_text(
                json.dumps(
                    {
                        "images": [],
                        "categories": [{"id": 7, "name": "Plastic bottle"}],
                        "annotations": [{"image_id": 99, "category_id": 7, "bbox": [10, 5, 20, 10]}],
                    }
                ),
                encoding="utf-8",
            )

            summary = convert_taco_annotations(annotation_path, output_dir)

            self.assertEqual(summary.images, 0)
            self.assertEqual(summary.annotations, 0)
            self.assertEqual(summary.skipped, 1)


if __name__ == "__main__":
    unittest.main()
