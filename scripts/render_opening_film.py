#!/usr/bin/env python3
"""Render the 60-second GOAI opening film from verified local artifacts.

The film deliberately distinguishes digital-twin visualization from evaluator
video. It does not imply a single uninterrupted robot run.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


WIDTH, HEIGHT = 1920, 1080
FPS = 24
DURATION = 60
RED = "#ff3b30"
CYAN = "#5ce1e6"
WHITE = "#f3f6f6"
MUTED = "#8d999b"
BG = "#060809"


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


F18 = font(18)
F22 = font(22)
F26 = font(26)
F34 = font(34, True)
F42 = font(42, True)
F58 = font(58, True)
F74 = font(74, True)
F96 = font(96, True)


def ease(value: float):
    value = min(max(value, 0.0), 1.0)
    return value * value * (3.0 - 2.0 * value)


def alpha_composite(base: Image.Image, overlay: Image.Image, xy: tuple[int, int]):
    if overlay.mode != "RGBA":
        overlay = overlay.convert("RGBA")
    base.alpha_composite(overlay, xy)


def darken(image: Image.Image, amount: float):
    return ImageEnhance.Brightness(image).enhance(amount)


def crop_cover(image: Image.Image, size: tuple[int, int], zoom: float = 1.0):
    tw, th = size
    iw, ih = image.size
    scale = max(tw / iw, th / ih) * zoom
    resized = image.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - tw) // 2)
    top = max(0, (resized.height - th) // 2)
    return resized.crop((left, top, left + tw, top + th))


def load_video_frames(imageio_ffmpeg, path: Path, size=(960, 426)):
    reader = imageio_ffmpeg.read_frames(
        str(path),
        pix_fmt="rgb24",
        output_params=["-vf", f"scale={size[0]}:{size[1]}"],
    )
    metadata = next(reader)
    frames = [Image.frombytes("RGB", size, frame).copy() for frame in reader]
    reader.close()
    if not frames:
        raise RuntimeError(f"No video frames decoded from {path}")
    return frames, float(metadata["fps"])


def video_frame(frames, source_fps: float, local_time: float):
    index = int(max(local_time, 0.0) * source_fps) % len(frames)
    return frames[index]


def read_gaussian_dog(path: Path):
    with path.open("rb") as handle:
        header = []
        while True:
            line = handle.readline()
            if not line:
                raise ValueError("Invalid PLY header")
            decoded = line.decode("ascii", "replace").strip()
            header.append(decoded)
            if decoded == "end_header":
                break
        count = int(next(line.split()[-1] for line in header if line.startswith("element vertex")))
        dtype = np.dtype(
            [(name, "<f4") for name in (
                "x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2",
                "opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3",
            )]
        )
        vertices = np.fromfile(handle, dtype=dtype, count=count)
    stride = max(1, count // 80000)
    points = np.column_stack((vertices["x"], vertices["y"], vertices["z"]))[::stride]
    sh = np.column_stack((vertices["f_dc_0"], vertices["f_dc_1"], vertices["f_dc_2"]))[::stride]
    colors = np.clip(0.5 + 0.28209479177387814 * sh, 0, 1)
    return points, (colors * 255).astype(np.uint8)


def render_dog_sprite(points: np.ndarray, colors: np.ndarray, size=(760, 520)):
    w, h = size
    yaw = math.radians(-22)
    rotated = points.copy()
    rotated[:, 0] = math.cos(yaw) * points[:, 0] - math.sin(yaw) * points[:, 1]
    rotated[:, 1] = math.sin(yaw) * points[:, 0] + math.cos(yaw) * points[:, 1]
    x = rotated[:, 0]
    z = rotated[:, 2]
    x = (x - x.min()) / max(np.ptp(x), 1e-6)
    z = (z - z.min()) / max(np.ptp(z), 1e-6)
    px = (70 + x * (w - 140)).astype(np.int32)
    py = (h - 55 - z * (h - 110)).astype(np.int32)
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    glow = np.zeros((h, w, 4), dtype=np.uint8)
    valid = (px >= 0) & (px < w) & (py >= 0) & (py < h)
    px, py, c = px[valid], py[valid], colors[valid]
    glow[py, px, :3] = np.array([92, 225, 230], dtype=np.uint8)
    glow[py, px, 3] = 120
    glow_image = Image.fromarray(glow, "RGBA").filter(ImageFilter.GaussianBlur(6))
    canvas[py, px, :3] = np.maximum(c, 100)
    canvas[py, px, 3] = 235
    point_image = Image.fromarray(canvas, "RGBA")
    glow_image.alpha_composite(point_image)
    return glow_image


def route_layout(manifest: dict, box: tuple[int, int, int, int]):
    x0, y0, x1, y1 = box
    points = manifest["points"]
    coords = [(float(p["scannerXYZ"][0]), float(p["scannerXYZ"][1])) for p in points]
    xs, ys = zip(*coords)
    margin = 55
    scale = min(
        (x1 - x0 - 2 * margin) / max(max(xs) - min(xs), 1),
        (y1 - y0 - 2 * margin) / max(max(ys) - min(ys), 1),
    )
    return [
        (
            int(x0 + margin + (x - min(xs)) * scale),
            int(y1 - margin - (y - min(ys)) * scale),
        )
        for x, y in coords
    ]


def route_position(points: list[tuple[int, int]], progress: float):
    distances = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(distances)
    target = min(max(progress, 0), 1) * total
    walked = 0.0
    for index, distance in enumerate(distances):
        if walked + distance >= target:
            ratio = 0 if distance == 0 else (target - walked) / distance
            a, b = points[index], points[index + 1]
            return (int(a[0] + (b[0] - a[0]) * ratio), int(a[1] + (b[1] - a[1]) * ratio)), index
        walked += distance
    return points[-1], len(points) - 1


def draw_route(draw: ImageDraw.ImageDraw, points, progress=1.0, labels=False):
    draw.line(points, fill="#28363a", width=8, joint="curve")
    position, active_index = route_position(points, progress)
    active = points[: active_index + 1] + [position]
    if len(active) > 1:
        draw.line(active, fill=CYAN, width=9, joint="curve")
    for index, (x, y) in enumerate(points):
        reached = index <= active_index
        radius = 10 if reached else 7
        color = RED if index in (0, len(points) - 1) else (WHITE if reached else "#536164")
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=BG, width=2)
        if labels and index % 2 == 0:
            draw.text((x + 10, y - 20), str(index + 1 if index < 28 else index + 2), font=F18, fill="#aab4b5")
    return position


def label(draw: ImageDraw.ImageDraw, text: str, x=46, y=38, real=False):
    color = CYAN if not real else "#ffe071"
    width = 430 if not real else 310
    draw.rounded_rectangle((x, y, x + width, y + 46), radius=4, fill=(4, 7, 8, 220), outline=color, width=2)
    draw.text((x + 15, y + 12), text, font=F18, fill=color)


def make_soundtrack(path: Path):
    rate = 48000
    t = np.arange(DURATION * rate, dtype=np.float64) / rate
    envelope = np.minimum(t / 2.5, 1.0) * np.minimum((DURATION - t) / 3.0, 1.0)
    drone = 0.13 * np.sin(2 * np.pi * 55 * t) + 0.06 * np.sin(2 * np.pi * 82.5 * t)
    pulse = np.zeros_like(t)
    for beat in np.arange(0, DURATION, 0.5):
        offset = t - beat
        active = (offset >= 0) & (offset < 0.18)
        pulse[active] += np.exp(-offset[active] * 25) * np.sin(2 * np.pi * 110 * offset[active])
    rng = np.random.default_rng(20260919)
    noise = rng.normal(0, 1, len(t))
    smooth = np.convolve(noise, np.ones(1800) / 1800, mode="same")
    riser = 0.06 * smooth * np.clip((t - 48) / 8, 0, 1)
    audio = np.clip((drone + 0.18 * pulse + riser) * envelope, -1, 1)
    stereo = np.column_stack((audio, audio * 0.94))
    pcm = (stereo * 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm.tobytes())


def frame_for_time(t: float, clips, dog, manifest):
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(canvas, "RGBA")

    if t < 4:
        progress = ease(t / 3.5)
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill="#040607")
        map_points = route_layout(manifest, (1030, 125, 1840, 955))
        draw_route(draw, map_points, progress)
        sprite = dog.resize((760, 520), Image.Resampling.LANCZOS)
        sprite.putalpha(sprite.getchannel("A").point(lambda a: int(a * min(progress * 1.6, 1))))
        alpha_composite(canvas, sprite, (1040, 300))
        draw.text((92, 110), "2026世界人工智能开源大赛", font=F34, fill=CYAN)
        draw.text((92, 170), "GOAI 总决赛", font=F96, fill=WHITE)
        draw.text((94, 298), "赛道四 · 具身未来  /  赛题二 · 产业园区全地形巡逻挑战赛", font=F26, fill="#a6b1b3")
        draw.rectangle((94, 390, 164, 398), fill=RED)
        draw.text((94, 430), "恐怖如斯战队", font=F58, fill=WHITE)
        label(draw, "数字孪生路线演示 / DIGITAL TWIN", real=False)

    elif t < 10:
        clip, source_fps = clips["campus"]
        source = video_frame(clip, source_fps, t - 4)
        canvas = crop_cover(source, (WIDTH, HEIGHT), 1.02 + (t - 4) * 0.005).convert("RGBA")
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 90))
        draw.rectangle((0, 700, WIDTH, HEIGHT), fill=(0, 0, 0, 135))
        draw.text((80, 748), "REAL CAMPUS · GAUSSIAN DIGITAL TWIN", font=F22, fill=CYAN)
        draw.text((80, 802), "真实园区扫描，进入可验证的导航环境", font=F58, fill=WHITE)
        draw.text((82, 888), "视觉重建用于观测  ·  碰撞网格与 NavMesh 用于通行约束", font=F26, fill="#d4dcdd")
        label(draw, "数字孪生路线演示 / DIGITAL TWIN", real=False)

    elif t < 17:
        local = (t - 10) / 7
        map_points = route_layout(manifest, (920, 90, 1840, 980))
        draw_route(draw, map_points, local, labels=True)
        sprite = dog.resize((850, 580), Image.Resampling.LANCZOS)
        alpha_composite(canvas, sprite, (55, 250))
        draw.text((82, 96), "LYNX S10", font=F74, fill=WHITE)
        draw.text((86, 185), "31 个目标点  ·  逐站到达  ·  精准 STOP", font=F26, fill="#aeb8ba")
        draw.text((84, 865), "定位 → 目标理解 → 局部轨迹 → 运动执行", font=F34, fill=CYAN)
        label(draw, "数字孪生路线演示 / DIGITAL TWIN", real=False)

    elif t < 35:
        local = (t - 17) / 18
        clip_keys = ["route12", "route25", "route22"]
        clip_key = clip_keys[min(int((t - 17) / 6), 2)]
        clip, source_fps = clips[clip_key]
        source = video_frame(clip, source_fps, t - 17)
        left = crop_cover(source, (1110, HEIGHT)).convert("RGBA")
        alpha_composite(canvas, darken(left, 0.86).convert("RGBA"), (0, 0))
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.rectangle((1108, 0, WIDTH, HEIGHT), fill="#080b0c")
        map_points = route_layout(manifest, (1130, 70, 1880, 1010))
        marker, active_index = route_position(map_points, local)
        draw_route(draw, map_points, local, labels=True)
        marker_dog = dog.resize((150, 103), Image.Resampling.LANCZOS)
        alpha_composite(canvas, marker_dog, (marker[0] - 75, marker[1] - 78))
        draw.rectangle((0, 824, 1110, HEIGHT), fill=(0, 0, 0, 162))
        messages = [
            (17, 23, "顺路绕开景观石", "Route 12 · verified detour"),
            (23, 29, "穿越可通行草地区域", "Route 25 · direct grass corridor"),
            (29, 35, "跨高程与长距离路段", "Multi-terrain patrol"),
        ]
        message = next(item for item in messages if item[0] <= t < item[1])
        draw.text((55, 858), message[2], font=F58, fill=WHITE)
        draw.text((58, 940), message[3], font=F22, fill=CYAN)
        draw.text((1160, 40), f"CHECKPOINT {min(active_index + 1, 31):02d} / 31", font=F22, fill=CYAN)
        label(draw, "数字孪生路线演示 / DIGITAL TWIN", real=False)

    elif t < 45:
        sections = [("route12", "视觉与里程计联合输入", "20 历史前视 + 当前左 / 中 / 右"),
                    ("route25", "局部 GoalPoint 注入", "目标随机器人姿态实时转换"),
                    ("route22", "模型输出轨迹与 STOP", "每一站完成后再下发下一站")]
        index = min(int((t - 35) / (10 / 3)), 2)
        key, headline, subline = sections[index]
        clip, source_fps = clips[key]
        source = video_frame(clip, source_fps, t - 35)
        canvas = crop_cover(source, (WIDTH, HEIGHT)).convert("RGBA")
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.rectangle((0, 0, WIDTH, 155), fill=(0, 0, 0, 170))
        draw.rectangle((0, 815, WIDTH, HEIGHT), fill=(0, 0, 0, 175))
        draw.text((70, 850), headline, font=F58, fill=WHITE)
        draw.text((72, 934), subline, font=F26, fill=CYAN)
        label(draw, "数字孪生中的模型输入 / MODEL INPUT", real=False)

    elif t < 54:
        key = "route12" if t < 49.5 else "route25"
        clip, source_fps = clips[key]
        source = video_frame(clip, source_fps, t - 45)
        canvas = crop_cover(source, (WIDTH, HEIGHT)).convert("RGBA")
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 70))
        draw.rectangle((1060, 110, 1840, 930), fill=(4, 7, 8, 205), outline=(255, 255, 255, 35), width=2)
        draw.text((1110, 165), "EPOCH 2 · 30 SEGMENTS", font=F22, fill=CYAN)
        metrics = [("30 / 30", "模型输出 STOP"), ("0.255 m", "平均终点误差"), ("30 / 30", "STOP + ≤ 1 m"), ("14 / 30", "STOP + ≤ 0.25 m")]
        for idx, (value, name) in enumerate(metrics):
            y = 245 + idx * 155
            draw.text((1110, y), value, font=F58, fill=WHITE)
            draw.text((1114, y + 74), name, font=F22, fill="#9da8aa")
        label(draw, "模型仿真推理 / MODEL INFERENCE", real=True)

    else:
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill="#050708")
        progress = ease((t - 54) / 3.5)
        stages = ["定位建图", "数字孪生", "逐站目标", "GoalPoint VLN", "执行与安全"]
        cell_w = 330
        start_x = 75
        for index, stage in enumerate(stages):
            x = start_x + index * (cell_w + 25)
            active = progress * len(stages) >= index
            draw.rounded_rectangle((x, 205, x + cell_w, 485), radius=8, fill="#0d1213", outline=CYAN if active else "#273033", width=3)
            draw.text((x + 25, 240), f"0{index + 1}", font=F22, fill=RED if active else MUTED)
            draw.text((x + 25, 355), stage, font=F34, fill=WHITE if active else MUTED)
            if index < len(stages) - 1:
                draw.line((x + cell_w, 345, x + cell_w + 25, 345), fill=CYAN if active else "#273033", width=3)
        draw.text((76, 615), "恐怖如斯·视觉语义注入具身导航巡检方案", font=F58, fill=WHITE)
        draw.text((78, 706), "恐怖如斯战队  ·  GOAI 2026 总决赛", font=F26, fill=CYAN)
        draw.text((78, 795), "开放路线数据接口、GoalPoint 转换与评测工具", font=F26, fill="#9aa5a7")
        draw.rectangle((78, 880, 380, 886), fill=RED)

    return canvas.convert("RGB")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--video-tools", type=Path, required=True)
    args = parser.parse_args()
    os.environ["PYTHONPATH"] = str(args.video_tools)
    import sys
    sys.path.insert(0, str(args.video_tools))
    import imageio_ffmpeg

    public = args.project_root / "public"
    media = public / "media"
    manifest = json.loads((public / "data" / "routes.json").read_text(encoding="utf-8"))
    dog_points, dog_colors = read_gaussian_dog(args.project_root / "assets-private" / "s10_model_3d.ply")
    dog = render_dog_sprite(dog_points, dog_colors)

    clip_paths = {
        "campus": media / "routes" / "epoch2" / "route_021_p21_to_p22.mp4",
        "route12": media / "routes" / "epoch2" / "route_012_p12_to_p13.mp4",
        "route25": media / "routes" / "epoch2" / "route_025_p25_to_p26.mp4",
        "route22": media / "routes" / "epoch2" / "route_022_p22_to_p23.mp4",
    }
    clips = {key: load_video_frames(imageio_ffmpeg, path) for key, path in clip_paths.items()}

    clean = media / "goai_yungu_goalnav_clean.mp4"
    writer = imageio_ffmpeg.write_frames(
        str(clean),
        (WIDTH, HEIGHT),
        fps=FPS,
        codec="libx264",
        quality=7,
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        macro_block_size=1,
        ffmpeg_log_level="warning",
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)
    poster = None
    for frame_index in range(DURATION * FPS):
        current = frame_for_time(frame_index / FPS, clips, dog, manifest)
        if frame_index == 18 * FPS:
            poster = current.copy()
        writer.send(np.asarray(current, dtype=np.uint8).tobytes())
    writer.close()
    if poster is None:
        poster = frame_for_time(18, clips, dog, manifest)
    poster.save(media / "goai_yungu_goalnav_poster.png")

    audio = args.project_root / "assets-private" / "goai_yungu_goalnav_soundtrack.wav"
    make_soundtrack(audio)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    full = media / "goai_yungu_goalnav_full_60s.mp4"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(clean), "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(full)],
        check=True,
    )
    teaser = media / "goai_yungu_goalnav_teaser_15s.mp4"
    subprocess.run(
        [ffmpeg, "-y", "-ss", "4", "-i", str(clean), "-t", "15", "-an", "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(teaser)],
        check=True,
    )
    print(json.dumps({"clean": str(clean), "full": str(full), "teaser": str(teaser)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
