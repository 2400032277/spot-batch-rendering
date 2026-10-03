import json
from pathlib import Path


CHECKPOINT_FILE = Path(__file__).resolve().with_name("checkpoint.json")


def load_checkpoint():
    if not CHECKPOINT_FILE.exists():
        return 0

    with CHECKPOINT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("last_completed_frame", 0)


def save_checkpoint(frame_number):
    data = {"last_completed_frame": frame_number}

    with CHECKPOINT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Checkpoint saved: frame {frame_number}")