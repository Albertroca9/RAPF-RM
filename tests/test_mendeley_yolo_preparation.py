import tempfile
import unittest
from pathlib import Path

from waste_robot_behavior.dataset.mendeley_yolo import (
    MENDELEY_CLASS_NAMES,
    convert_mendeley_class_id,
    prepare_mendeley_subset,
)


class MendeleyYoloPreparationTest(unittest.TestCase):
    def test_maps_mendeley_classes_to_project_four_bins(self):
        cases = {
            "plastic": "plastic",
            "paper": "paper",
            "cardboard": "paper",
            "metal": "plastic",
            "glass": "glass",
            "organic waste": "residual",
            "battery waste": "residual",
            "e-waste": "residual",
            "cloth": "residual",
            "other waste": "residual",
        }

        for class_id, source_name in enumerate(MENDELEY_CLASS_NAMES):
            with self.subTest(source_name=source_name):
                self.assertEqual(convert_mendeley_class_id(class_id).project_name, cases[source_name])

    def test_prepares_reproducible_subset_and_rewrites_labels(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            images = source / "images"
            labels = source / "labels"
            images.mkdir(parents=True)
            labels.mkdir(parents=True)
            for index in range(5):
                (images / f"sample_{index}.jpg").write_bytes(b"fake image")
                (labels / f"sample_{index}.txt").write_text(
                    f"{index} 0.500000 0.500000 0.250000 0.250000\n",
                    encoding="utf-8",
                )

            output = root / "prepared"
            summary = prepare_mendeley_subset(source, output, sample_size=4, val_ratio=0.25, seed=7)

            self.assertEqual(summary.selected_images, 4)
            self.assertEqual(summary.train_images, 3)
            self.assertEqual(summary.val_images, 1)
            self.assertTrue((output / "data.yaml").exists())
            self.assertIn("0: paper", (output / "data.yaml").read_text(encoding="utf-8"))
            self.assertIn("3: residual", (output / "data.yaml").read_text(encoding="utf-8"))

            label_rows = [
                path.read_text(encoding="utf-8").strip()
                for path in sorted((output / "labels").glob("*/*.txt"))
            ]
            self.assertTrue(all(row.split()[0] in {"0", "1", "2", "3"} for row in label_rows))
            self.assertTrue(any(row.startswith("0 ") for row in label_rows))
            self.assertTrue(any(row.startswith("1 ") for row in label_rows))
            self.assertTrue(any(row.startswith("2 ") for row in label_rows))
