import json
import unittest
from pathlib import Path


class ColabNotebookTest(unittest.TestCase):
    def test_finetuning_notebook_is_valid_and_contains_required_steps(self):
        notebook_path = Path("notebooks/yolov8n_mendeley_colab.ipynb")

        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        self.assertEqual(notebook["nbformat"], 4)
        self.assertIn("colab", notebook["metadata"])

        source = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook["cells"]
        )
        required_fragments = [
            "pip install -q ultralytics",
            "Mendeley dataset page",
            "data/mendeley_yolo_4bins",
            "def prepare_mendeley_subset",
            "def convert_mendeley_class_id",
            "def find_images",
            "def rewrite_label_rows",
            "paper",
            "plastic",
            "glass",
            "residual",
            "YOLO('yolov8n.pt')",
            "model.train",
            "best.pt",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, source)

        forbidden_fragments = [
            "git clone",
            "sys.path.insert",
            "waste_robot_behavior",
            "REPO_URL",
            "PROJECT_DIR",
        ]
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
