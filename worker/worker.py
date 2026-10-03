import sys
import json
import os

from renderer import render_frame
from checkpoint import load_checkpoint
from checkpoint import save_checkpoint


STATUS_FILE = "status.json"


def update_status(
    status,
    start_frame,
    end_frame,
    completed
):

    data = {
        "status": status,
        "start_frame": start_frame,
        "end_frame": end_frame,
        "completed": completed,
        "total": end_frame - start_frame + 1
    }

    with open(
        STATUS_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def run_worker(
    start_frame,
    end_frame
):

    # Read previous checkpoint
    last_completed = load_checkpoint()

    # Resume from next unfinished frame
    actual_start = max(
        start_frame,
        last_completed + 1
    )

    # If everything is already completed
    if actual_start > end_frame:

        update_status(
            "completed",
            start_frame,
            end_frame,
            end_frame - start_frame + 1
        )

        print("All frames already completed.")

        return

    print()
    print("==============================")
    print("WORKER STARTED")
    print(
        f"Frames: {actual_start} - {end_frame}"
    )
    print("==============================")

    update_status(
        "running",
        start_frame,
        end_frame,
        last_completed
    )

    for frame in range(
        actual_start,
        end_frame + 1
    ):

        # Render frame
        render_frame(frame)

        # Save checkpoint
        save_checkpoint(frame)

        # Update frontend-visible status
        update_status(
            "running",
            start_frame,
            end_frame,
            frame
        )

    update_status(
        "completed",
        start_frame,
        end_frame,
        end_frame
    )

    print()
    print("✅ WORKER COMPLETED")
    print()


if __name__ == "__main__":

    start = int(sys.argv[1])

    end = int(sys.argv[2])

    run_worker(
        start,
        end
    )