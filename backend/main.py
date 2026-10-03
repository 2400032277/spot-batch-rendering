# Backend entry point

import json
import sys
import threading
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]

WORKER_DIR = ROOT_DIR / "worker"

STATUS_FILE = Path(__file__).resolve().with_name("status.json")


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Spot Rendering Backend",
    description="Backend API for Amazon EC2 Spot batch rendering",
    version="1.0"
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class RenderRequest(BaseModel):

    start_frame: int
    end_frame: int


# --------------------------------------------------
# STATUS FUNCTION
# --------------------------------------------------

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

    with STATUS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def read_root():

    return {
        "status": "ok",
        "message": "Spot rendering backend is running"
    }


# --------------------------------------------------
# STATUS ENDPOINT
# --------------------------------------------------

@app.get("/status")
def get_status():

    if not STATUS_FILE.exists():

        return {
            "status": "idle",
            "start_frame": 0,
            "end_frame": 0,
            "completed": 0,
            "total": 0
        }

    with STATUS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# --------------------------------------------------
# WORKER FUNCTION
# --------------------------------------------------

def run_worker(
    start_frame,
    end_frame
):

    # Import worker modules
    if str(WORKER_DIR) not in sys.path:

        sys.path.insert(
            0,
            str(WORKER_DIR)
        )

    from checkpoint import (
        load_checkpoint,
        save_checkpoint
    )

    from renderer import render_frame


    # Read previous checkpoint
    last_completed = load_checkpoint()

    # Resume from next unfinished frame
    actual_start = max(
        start_frame,
        last_completed + 1
    )


    # Already completed
    if actual_start > end_frame:

        update_status(
            "completed",
            start_frame,
            end_frame,
            end_frame - start_frame + 1
        )

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


    # Render frames
    for frame in range(
        actual_start,
        end_frame + 1
    ):

        print(
            f"Rendering frame {frame}"
        )

        # Render
        render_frame(frame)

        # Save checkpoint
        save_checkpoint(frame)

        # Update status
        update_status(
            "running",
            start_frame,
            end_frame,
            frame
        )


    # Completed
    update_status(
        "completed",
        start_frame,
        end_frame,
        end_frame
    )


    print()
    print("✅ WORKER COMPLETED")
    print()


# --------------------------------------------------
# START JOB ENDPOINT
# --------------------------------------------------

@app.post("/start-job")
def start_job(
    request: RenderRequest
):

    # Validate start frame
    if request.start_frame < 1:

        return {
            "status": "error",
            "message": "Start frame must be at least 1"
        }


    # Validate frame range
    if request.end_frame < request.start_frame:

        return {
            "status": "error",
            "message": "End frame must be greater than start frame"
        }


    # Update status immediately
    update_status(
        "starting",
        request.start_frame,
        request.end_frame,
        0
    )


    # Run rendering in background
    thread = threading.Thread(
        target=run_worker,
        args=(
            request.start_frame,
            request.end_frame
        ),
        daemon=True
    )

    thread.start()


    return {
        "status": "started",
        "message": "Rendering job started",
        "start_frame": request.start_frame,
        "end_frame": request.end_frame
    }