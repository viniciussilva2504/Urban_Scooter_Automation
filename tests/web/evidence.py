"""Capture browser checkpoints as GIF and MP4 evidence for each pytest case."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image


class BrowserEvidence:
    def __init__(self, node_id: str, output_dir: Path):
        self.node_id = node_id
        self.output_dir = output_dir
        self.frames: list[Image.Image] = []

    def capture(self, driver) -> None:
        try:
            raw_png = driver.get_screenshot_as_png()
            with Image.open(BytesIO(raw_png)) as image:
                self.frames.append(image.convert("RGB").copy())
        except Exception:
            # Keep evidence collection from masking the browser/test exception.
            return

    def save(self) -> tuple[Path, Path] | None:
        if not self.frames:
            return None

        self.output_dir.mkdir(parents=True, exist_ok=True)
        base_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", self.node_id).strip("_.")
        if len(base_name) > 120:
            base_name = base_name[:100] + "_" + str(abs(hash(self.node_id)))
        gif_path = self.output_dir / f"{base_name}.gif"
        mp4_path = self.output_dir / f"{base_name}.mp4"

        self.frames[0].save(
            gif_path,
            save_all=True,
            append_images=self.frames[1:],
            optimize=True,
            duration=550,
            loop=0,
        )

        try:
            import imageio_ffmpeg

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError(
                "MP4 evidence requires imageio-ffmpeg or ffmpeg on PATH. "
                "Install it with: python -m pip install imageio-ffmpeg"
            )
        with tempfile.TemporaryDirectory(prefix="urban-scooter-evidence-") as temp_dir:
            frame_pattern = Path(temp_dir) / "frame_%05d.png"
            for index, frame in enumerate(self.frames):
                frame.save(str(frame_pattern).replace("%05d", f"{index:05d}"), format="PNG")

            command = [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-framerate",
                "2",
                "-i",
                str(frame_pattern),
                "-c:v",
                "mpeg4",
                "-q:v",
                "5",
                "-pix_fmt",
                "yuv420p",
                str(mp4_path),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)

        return gif_path, mp4_path
