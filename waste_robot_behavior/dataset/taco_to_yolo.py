import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from waste_robot_behavior.taxonomy import CONTAINER_CLASSES, DetectionClassMapper


@dataclass(frozen=True)
class ConversionSummary:
    images: int
    annotations: int
    skipped: int


def convert_taco_annotations(annotation_path: Path, output_dir: Path) -> ConversionSummary:
    annotation_path = Path(annotation_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(annotation_path.read_text(encoding="utf-8"))
    images = {image["id"]: image for image in data.get("images", [])}
    categories = {category["id"]: category["name"] for category in data.get("categories", [])}
    mapper = DetectionClassMapper.default()

    rows_by_image: dict[int, list[str]] = {}
    skipped = 0
    for annotation in data.get("annotations", []):
        image = images.get(annotation.get("image_id"))
        category = categories.get(annotation.get("category_id"))
        bbox = annotation.get("bbox")
        if image is None or category is None or bbox is None:
            skipped += 1
            continue

        class_name = mapper.map_waste_class(category)
        class_id = CONTAINER_CLASSES.index(class_name)
        row = _bbox_to_yolo_row(class_id, bbox, image["width"], image["height"])
        rows_by_image.setdefault(image["id"], []).append(row)

    for image_id, rows in rows_by_image.items():
        label_path = output_dir / _label_name(images[image_id]["file_name"])
        label_path.parent.mkdir(parents=True, exist_ok=True)
        label_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    return ConversionSummary(images=len(rows_by_image), annotations=sum(len(rows) for rows in rows_by_image.values()), skipped=skipped)


def write_yolo_data_yaml(output_path: Path, train_path: str, val_path: str) -> None:
    lines = [
        f"train: {train_path}",
        f"val: {val_path}",
        "names:",
    ]
    lines.extend(f"  {index}: {name}" for index, name in enumerate(CONTAINER_CLASSES))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _bbox_to_yolo_row(class_id: int, bbox: list[float], width: int, height: int) -> str:
    x, y, w, h = bbox
    x_center = (x + (w / 2.0)) / width
    y_center = (y + (h / 2.0)) / height
    return f"{class_id} {x_center:.6f} {y_center:.6f} {w / width:.6f} {h / height:.6f}"


def _label_name(file_name: str) -> str:
    normalized = file_name.replace("\\", "/").replace("/", "_")
    return str(Path(normalized).with_suffix(".txt"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert TACO COCO annotations into YOLO label files.")
    parser.add_argument("annotations", type=Path, help="Path to TACO annotations.json")
    parser.add_argument("output_dir", type=Path, help="Directory where YOLO label files will be written")
    parser.add_argument("--data-yaml", type=Path, help="Optional path for a YOLO data.yaml template")
    parser.add_argument("--train", default="../images/train", help="train path to write into data.yaml")
    parser.add_argument("--val", default="../images/val", help="validation path to write into data.yaml")
    args = parser.parse_args()

    summary = convert_taco_annotations(args.annotations, args.output_dir)
    if args.data_yaml:
        write_yolo_data_yaml(args.data_yaml, args.train, args.val)
    print(f"converted_images={summary.images} converted_annotations={summary.annotations} skipped={summary.skipped}")


if __name__ == "__main__":
    main()
