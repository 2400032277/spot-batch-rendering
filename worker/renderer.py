from pathlib import Path
import time

from PIL import Image, ImageDraw


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def render_frame(frame_number):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    width = 800
    height = 450

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    x = 50 + (frame_number * 10) % 700
    y = 200

    draw.ellipse((x, y, x + 50, y + 50), fill="blue")
    draw.text((20, 20), f"Animation Frame {frame_number}", fill="black")

    time.sleep(1)

    filename = OUTPUT_DIR / f"frame_{frame_number:04d}.png"
    image.save(filename)

    print(f"Rendered frame {frame_number}")
    return str(filename)


if __name__ == "__main__":
    for frame in range(1, 11):
        render_frame(frame)