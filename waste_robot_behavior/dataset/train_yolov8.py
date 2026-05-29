import argparse
from pathlib import Path


def build_training_kwargs(
    data_yaml: Path,
    model: str = "yolov8n.pt",
    imgsz: int = 640,
    epochs: int = 30,
    batch: int = 8,
    project: str = "runs/waste_yolov8",
    name: str = "yolov8n_mendeley_4bins",
) -> dict[str, str | int]:
    return {
        "model": model,
        "data": data_yaml.as_posix(),
        "imgsz": imgsz,
        "epochs": epochs,
        "batch": batch,
        "project": project,
        "name": name,
    }


def split_model_from_training_kwargs(kwargs: dict[str, str | int]) -> tuple[str, dict[str, str | int]]:
    train_kwargs = dict(kwargs)
    return str(train_kwargs.pop("model")), train_kwargs


def train_yolov8(kwargs: dict[str, str | int]) -> None:
    from ultralytics import YOLO

    model_path, train_kwargs = split_model_from_training_kwargs(kwargs)
    model = YOLO(model_path)
    model.train(**train_kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8n on the prepared four-bin waste dataset.")
    parser.add_argument("data_yaml", type=Path, help="Path to prepared YOLO data.yaml")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--project", default="runs/waste_yolov8")
    parser.add_argument("--name", default="yolov8n_mendeley_4bins")
    args = parser.parse_args()

    kwargs = build_training_kwargs(
        data_yaml=args.data_yaml,
        model=args.model,
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        project=args.project,
        name=args.name,
    )
    train_yolov8(kwargs)


if __name__ == "__main__":
    main()
