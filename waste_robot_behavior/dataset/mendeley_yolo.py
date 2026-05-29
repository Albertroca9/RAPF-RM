import argparse
import random
import shutil
from dataclasses import dataclass
from pathlib import Path

from waste_robot_behavior.taxonomy import CONTAINER_CLASSES


MENDELEY_CLASS_NAMES = (
    "plastic",
    "paper",
    "cardboard",
    "metal",
    "glass",
    "organic waste",
    "battery waste",
    "e-waste",
    "cloth",
    "other waste",
)

MENDELEY_TO_PROJECT = {
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

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class ClassMapping:
    source_id: int
    source_name: str
    project_id: int
    project_name: str


@dataclass(frozen=True)
class PreparationSummary:
    selected_images: int
    train_images: int
    val_images: int
    skipped_images: int


def convert_mendeley_class_id(source_id: int) -> ClassMapping:
    source_name = MENDELEY_CLASS_NAMES[source_id]
    project_name = MENDELEY_TO_PROJECT[source_name]
    return ClassMapping(
        source_id=source_id,
        source_name=source_name,
        project_id=CONTAINER_CLASSES.index(project_name),
        project_name=project_name,
    )


def prepare_mendeley_subset(
    source_dir: Path,
    output_dir: Path,
    sample_size: int = 600,
    val_ratio: float = 0.2,
    seed: int = 42,
) -> PreparationSummary:
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    image_files = _find_images(source_dir)
    random.Random(seed).shuffle(image_files)

    selected = []
    skipped = 0
    for image_path in image_files:
        label_path = _label_for_image(source_dir, image_path)
        if label_path is None:
            skipped += 1
            continue
        selected.append((image_path, label_path))
        if len(selected) == sample_size:
            break

    if not selected:
        raise ValueError(f"No labeled images found under {source_dir}")

    val_count = max(1, round(len(selected) * val_ratio)) if len(selected) > 1 else 0
    train_items = selected[:-val_count] if val_count else selected
    val_items = selected[-val_count:] if val_count else []

    _reset_output_tree(output_dir)
    _copy_items(train_items, output_dir, "train")
    _copy_items(val_items, output_dir, "val")
    write_data_yaml(output_dir / "data.yaml", "images/train", "images/val")

    return PreparationSummary(
        selected_images=len(selected),
        train_images=len(train_items),
        val_images=len(val_items),
        skipped_images=skipped,
    )


def write_data_yaml(output_path: Path, train_path: str, val_path: str) -> None:
    lines = [f"train: {train_path}", f"val: {val_path}", "names:"]
    lines.extend(f"  {index}: {name}" for index, name in enumerate(CONTAINER_CLASSES))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _find_images(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def _label_for_image(source_dir: Path, image_path: Path) -> Path | None:
    candidates = [
        image_path.with_suffix(".txt"),
        source_dir / "labels" / image_path.with_suffix(".txt").name,
        source_dir / "labels" / image_path.relative_to(source_dir).with_suffix(".txt"),
    ]
    parts = list(image_path.relative_to(source_dir).parts)
    if "images" in parts:
        parts[parts.index("images")] = "labels"
        candidates.append(source_dir / Path(*parts).with_suffix(".txt"))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _reset_output_tree(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    for split in ("train", "val"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def _copy_items(items: list[tuple[Path, Path]], output_dir: Path, split: str) -> None:
    for image_path, label_path in items:
        target_image = output_dir / "images" / split / image_path.name
        target_label = output_dir / "labels" / split / label_path.name
        shutil.copy2(image_path, target_image)
        target_label.write_text(_rewrite_label_rows(label_path), encoding="utf-8")


def _rewrite_label_rows(label_path: Path) -> str:
    rows = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        mapping = convert_mendeley_class_id(int(parts[0]))
        rows.append(" ".join([str(mapping.project_id), *parts[1:]]))
    return "\n".join(rows) + ("\n" if rows else "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a Mendeley YOLO waste subset for YOLOv8 fine-tuning.")
    parser.add_argument("source_dir", type=Path, help="Directory containing the extracted Mendeley images and labels")
    parser.add_argument("output_dir", type=Path, help="Output YOLO dataset directory")
    parser.add_argument("--sample-size", type=int, default=600)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    summary = prepare_mendeley_subset(args.source_dir, args.output_dir, args.sample_size, args.val_ratio, args.seed)
    print(
        "selected_images={0.selected_images} train_images={0.train_images} "
        "val_images={0.val_images} skipped_images={0.skipped_images}".format(summary)
    )


if __name__ == "__main__":
    main()
