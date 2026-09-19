"""Decode the delivered MP4 and compare its inset video against source frames."""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from render_overview_film_v2 import CLIP_SCHEDULE, STEM


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--video-tools", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.video_tools))
    import imageio_ffmpeg as video

    media = args.project_root / "public/media"
    qa = args.project_root / "assets-private/film-v2/qa"
    film = media / f"{STEM}_64s.mp4"
    reader = video.read_frames(str(film))
    info = next(reader)
    reader.close()
    assert tuple(info["size"]) == (1920, 1080), info
    assert abs(info["duration"] - 64) < 0.1, info
    assert info["codec"] == "h264", info
    ffmpeg = video.get_ffmpeg_exe()
    subprocess.run([ffmpeg, "-v", "error", "-i", str(film), "-f", "null", "-"], check=True)

    def frame(path, time):
        stream = video.read_frames(str(path), input_params=["-ss", str(time)])
        meta = next(stream)
        image = Image.frombytes("RGB", tuple(meta["size"]), next(stream))
        stream.close()
        return image

    checks = []
    for spec in CLIP_SCHEDULE:
        time = spec["start"] + 2
        actual = frame(film, time)
        source = frame(media / "routes/epoch2" / spec["file"], 2)
        crop = actual.crop((0, 96, 1920, 948))
        assert crop.size == source.size
        error = np.mean((np.asarray(crop).astype(float) - np.asarray(source).astype(float)) ** 2)
        psnr = 100.0 if error == 0 else 20 * math.log10(255 / math.sqrt(error))
        assert psnr > 32, (spec["file"], psnr)
        actual.save(qa / f"encoded-route-{spec['ordinal']:02}.jpg", quality=95)
        checks.append({"route": spec["ordinal"], "time": time, "source_frame_psnr_db": psnr, "complete_source_bounds_preserved": True})

    samples = np.frombuffer(subprocess.check_output([ffmpeg, "-v", "error", "-i", str(film), "-map", "0:a:0", "-f", "f32le", "-ac", "2", "-ar", "48000", "pipe:1"]), dtype="<f4")
    assert abs(len(samples) / (48000 * 2) - 64) < 0.1
    rms = float(np.sqrt(np.mean(samples ** 2)))
    peak = float(np.max(np.abs(samples)))
    assert 0.015 < rms < 0.5 and peak < 1, (rms, peak)
    render = json.loads((qa / "render-validation.json").read_text(encoding="utf-8"))
    assert max(x["tempo"] for x in render["audio"]["segments"]) <= 1.3
    report = {"metadata": info, "decode_errors": 0, "visual_checks": checks, "audio_rms": rms, "audio_peak": peak, "synthetic_narration": True}
    (qa / "encoded-video-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
