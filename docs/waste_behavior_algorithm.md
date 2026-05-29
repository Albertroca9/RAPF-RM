# YOLO RGB-D Waste Behavior Algorithm

## Goal

Detect waste, classify it into one of four container classes, estimate its 3D position with depth, and drive a high-level behavior state machine that can later be connected to `move_base` and OpenMANIPULATOR.

## Runtime Flow

```text
RGB image + depth + camera_info
        -> YOLO detector
        -> class mapper
        -> 3D target estimate
        -> behavior state machine
        -> decision JSON
        -> mock or real robot IO
```

## Behavior Rules

- Waste detections with valid depth become pickup candidates.
- The nearest actionable waste target is selected first.
- If the target is within approach distance, the state machine requests gripper close.
- After mock or real gripper feedback confirms pickup, the robot navigates to the bin for that container.
- `person` is a safety class and blocks motion before any trash action.
- Unknown non-waste objects are not pickup targets.
- Detections without valid depth are not actionable, because the pinza needs a reachable 3D target.

## Dataset Strategy

The first fine-tuning dataset is the Mendeley synthetic outdoor waste YOLO dataset, version 2:

```text
https://data.mendeley.com/datasets/2x69gjbcz6/2
```

It is already annotated in YOLO format and includes plastic, paper, cardboard, metal, glass, organic waste, battery waste, e-waste, cloth, and other waste. These labels are collapsed into the four operational container classes:

- `paper`
- `plastic`
- `glass`
- `residual`

Paper and cardboard map to `paper`. Plastic and metal map to `plastic`. Glass maps to `glass`. Organic waste and all remaining waste classes map to `residual`.

The legacy TACO conversion path is still available for later real-image expansion. Its labels are also collapsed into the same four classes through `waste_robot_behavior/config/taco_to_4_bins.csv`.

The preparation tools write YOLO labels and a `data.yaml` template. Images, labels, training runs, and trained weights are intentionally ignored by git.

## Fine-Tuning Commands

After downloading and extracting the Mendeley dataset:

```bash
python3 -m waste_robot_behavior.dataset.mendeley_yolo \
  /path/to/extracted_mendeley_dataset \
  data/mendeley_yolo_4bins \
  --sample-size 600

python3 -m waste_robot_behavior.dataset.train_yolov8 \
  data/mendeley_yolo_4bins/data.yaml
```

The expected best weights path is:

```text
runs/waste_yolov8/yolov8n_mendeley_4bins/weights/best.pt
```

## Next Integration Step

Replace `mock_robot_io_node.py` with adapters that:

- send approach/navigation goals to `move_base`;
- command OpenMANIPULATOR gripper open/close;
- publish feedback using the same JSON shape consumed by `waste_behavior_node.py`.
