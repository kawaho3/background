#!/usr/bin/env python3
"""Local foreground extraction preserving motion, removing background and audio.

Requires FFmpeg, Pillow and rembg. First run downloads a segmentation model.
This is a baseline, NOT a production-quality temporal video matting model.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path


def run(command):
    subprocess.run(command, check=True)


def probe_rate(source):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=avg_frame_rate,r_frame_rate", "-of", "json", str(source)],
        capture_output=True, text=True, check=True,
    )
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise ValueError("Input has no video stream")
    for name in ("avg_frame_rate", "r_frame_rate"):
        rate = streams[0].get(name, "0/0")
        try:
            fps = Fraction(rate)
            if fps > 0:
                return str(rate)
        except (ValueError, ZeroDivisionError):
            pass
    raise ValueError("Cannot determine frame rate")


def encode_command(frames_pattern, output, fps, crf=24):
    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
               "-framerate", fps, "-i", str(frames_pattern), "-an"]
    if output.suffix.lower() == ".webm":
        command += ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                    "-auto-alt-ref", "0", "-b:v", "0", "-crf", str(crf)]
    elif output.suffix.lower() == ".mov":
        command += ["-c:v", "qtrle", "-pix_fmt", "argb"]
    else:
        raise ValueError("Output must end in .webm or .mov (MP4 does not preserve alpha reliably)")
    return command + [str(output)]


def process_frames(input_dir, output_dir, model):
    try:
        from PIL import Image
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError("Install Python packages: pip install -r requirements.txt") from exc
    session = new_session(model_name=model)
    inputs = sorted(input_dir.glob("frame_*.png"))
    if not inputs:
        raise RuntimeError("FFmpeg extracted zero frames")
    for number, source in enumerate(inputs):
        with Image.open(source) as rgb:
            foreground = remove(rgb.convert("RGB"), session=session)
            if not isinstance(foreground, Image.Image):
                raise TypeError("rembg did not return an image")
            foreground.convert("RGBA").save(output_dir / source.name)
        if number % 30 == 0 or number + 1 == len(inputs):
            print(f"Processed {number + 1}/{len(inputs)} frames", flush=True)
    return len(inputs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source video containing the character")
    parser.add_argument("output", type=Path, help="Silent alpha video (.webm or .mov)")
    parser.add_argument("--model", default="u2net", help="Installed rembg model (default u2net)")
    parser.add_argument("--crf", type=int, default=24, help="VP9 quality, 0 best to 63 worst")
    parser.add_argument("--keep-frames", type=Path, help="Optional location to retain RGBA PNG frames")
    args = parser.parse_args(argv)
    if not args.input.is_file():
        parser.error(f"Input file not found: {args.input}")
    if args.output.suffix.lower() not in (".webm", ".mov"):
        parser.error("Output must be .webm or .mov")
    if not 0 <= args.crf <= 63:
        parser.error("--crf must be between 0 and 63")
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            parser.error(f"{tool} not found on PATH")
    rate = probe_rate(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="character_extract_") as temp:
        root = Path(temp)
        incoming = root / "input"
        incoming.mkdir()
        outgoing = args.keep_frames or (root / "rgba")
        outgoing.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y", "-i",
             str(args.input), "-map", "0:v:0", "-vsync", "0",
             str(incoming / "frame_%06d.png")])
        count = process_frames(incoming, outgoing, args.model)
        run(encode_command(outgoing / "frame_%06d.png", args.output, rate, args.crf))
        print(f"Wrote {args.output} ({count} video frames, no audio)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
