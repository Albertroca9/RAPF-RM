# YOLO RGB-D Waste Behavior Algorithm

## Goal

Detect waste, classify it into one of five container classes, estimate its 3D position with depth, and drive a high-level behavior state machine that can later be connected to `move_base` and OpenMANIPULATOR.

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

TACO is used as the first dataset because it is annotated for litter in real-world contexts. The project does not expose TACO's full taxonomy to the robot. Instead, TACO labels are collapsed into the five operational container classes:

- `paper_cardboard`
- `plastic_metal_carton`
- `glass`
- `organic`
- `residual`

The conversion tool writes YOLO labels and a `data.yaml` template. Images, labels and trained weights are intentionally ignored by git.

## Next Integration Step

Replace `mock_robot_io_node.py` with adapters that:

- send approach/navigation goals to `move_base`;
- command OpenMANIPULATOR gripper open/close;
- publish feedback using the same JSON shape consumed by `waste_behavior_node.py`.
