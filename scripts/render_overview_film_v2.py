#!/usr/bin/env python3
"""Render a narrated, uncropped 64-second navigation overview.

Inference sources are displayed at their recorded cadence, never cover-cropped,
stretched, wrapped, or presented as one continuous physical robot run.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

W, H, FPS, DURATION = 1920, 1080, 24, 64
BG, WHITE, MUTED, CYAN = "#101315", "#f1f4f5", "#b8c3c7", "#91cbc9"
STEM = "goai_yungu_vln_overview_v2"

NARRATION = [
    (0.5, 6.7, "云谷中心，产业园区全地形巡逻。恐怖如斯战队，逐站到点。"),
    (7.1, 9.9, "面向山猫S十轮足机器人。"),
    (10.1, 12.9, "定位到执行，形成闭环。"),
    (13.1, 16.9, "高保真高斯仿真中采样轨迹，训练模型。"),
    (17.1, 20.9, "激光与惯性融合，持续输出可信位姿。"),
    (21.1, 26.9, "三视图或单视图，融合多帧观测、目标点与语义，预测轨迹。"),
    (27.1, 31.8, "安全执行，停车确认到点，再下发下一站。"),
    (32.2, 37.8, "以下是模型仿真推理。先看阶梯路段，到点后输出停止。"),
    (38.2, 46.8, "绕开景观石，沿可通行区域接近目标。前视画面与俯视轨迹，完整保留。"),
    (47.2, 53.8, "穿越草地区域，修正朝向，到达目标后停车。"),
    (54.1, 59.8, "三十段仿真均输出停止，平均终点误差零点二五五米。"),
    (60.2, 63.8, "让视觉语言导航真正落地园区巡检。"),
]

CLIP_SCHEDULE = [
    {"start": 32, "end": 38, "ordinal": 2, "title": "阶梯路段", "file": "route_002_p02_to_p03.mp4"},
    {"start": 38, "end": 47, "ordinal": 12, "title": "绕开景观石", "file": "route_012_p12_to_p13.mp4"},
    {"start": 47, "end": 54, "ordinal": 25, "title": "穿越草地区域", "file": "route_025_p25_to_p26.mp4"},
]


@lru_cache(maxsize=60)
def font(size, bold=False):
    name = "msyhbd.ttc" if bold else "msyh.ttc"
    return ImageFont.truetype(str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / name), size)


def fit_rect(source_size, box):
    x, y, width, height = box
    scale = min(width / source_size[0], height / source_size[1])
    sw, sh = round(source_size[0] * scale), round(source_size[1] * scale)
    return x + (width - sw) // 2, y + (height - sh) // 2, sw, sh


def paste_contained(canvas, image, box):
    x, y, width, height = fit_rect(image.size, box)
    canvas.paste(image.resize((width, height), Image.Resampling.LANCZOS), (x, y))
    return x, y, width, height


def text(draw, xy, value, size=34, fill=WHITE, bold=False, max_width=None):
    selected = font(size, bold)
    if max_width is not None:
        while draw.textlength(value, font=selected) > max_width and size > 18:
            size -= 1
            selected = font(size, bold)
    draw.text(xy, value, font=selected, fill=fill)


def centered(draw, y, value, size=34, fill=WHITE, bold=False):
    width = draw.textlength(value, font=font(size, bold))
    assert width < W - 80, (value, width)
    text(draw, ((W - width) / 2, y), value, size, fill, bold)


def caption(canvas, heading, subtitle):
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 950, W, H), fill=BG)
    text(draw, (52, 960), heading, 25, CYAN, True, W - 104)
    text(draw, (52, 1003), subtitle, 34, WHITE, False, W - 104)


def aerial(image, progress, reverse=False):
    # Camera moves apply only to the supplied establishing photographs.
    p = min(max(progress, 0), 1)
    zoom = 1.0 + 0.05 * (1 - p if reverse else p)
    width, height = round(W * zoom), round(H * zoom)
    scaled = ImageOps.fit(image, (width, height), Image.Resampling.LANCZOS)
    left, top = (width - W) // 2, (height - H) // 2
    return scaled.crop((left, top, left + W, top + H))


def scrim(image, strength=0.65):
    overlay = Image.new("RGB", image.size, BG)
    return Image.blend(image, overlay, strength)


def opening(images, t, titles=True):
    if t < 3.5:
        canvas = aerial(images["aerial2"], t / 3.5)
    else:
        canvas = aerial(images["aerial1"], (t - 3.5) / 3.5, True)
    if titles:
        shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        pixels = np.zeros((H, W, 4), dtype=np.uint8)
        pixels[:, :, 3] = (np.linspace(12, 190, H)[:, None]).astype(np.uint8)
        shade = Image.fromarray(pixels)
        canvas = Image.alpha_composite(canvas.convert("RGBA"), shade).convert("RGB")
        draw = ImageDraw.Draw(canvas)
        text(draw, (90, 68), "GOAI 2026  /  GRAND FINALS", 27, WHITE)
        draw.line((94, 638, 174, 638), fill=CYAN, width=5)
        if t < 3.5:
            text(draw, (88, 665), "云谷中心", 104, WHITE, True)
            text(draw, (94, 805), "产业园区全地形巡逻", 43, WHITE)
        else:
            text(draw, (88, 665), "恐怖如斯战队", 90, WHITE, True)
            text(draw, (94, 795), "2026世界人工智能开源大赛（GOAI）总决赛", 36, WHITE)
            text(draw, (94, 861), "赛道四 · 具身未来  |  赛题二 · 产业园区全地形巡逻挑战赛", 30, WHITE)
    return canvas


def product_frame(images):
    canvas = Image.new("RGB", (W, H), "white")
    paste_contained(canvas, images["robot"], (880, 78, 1000, 915))
    draw = ImageDraw.Draw(canvas)
    text(draw, (90, 128), "ROBOT PLATFORM", 26, "#527176")
    text(draw, (86, 266), "山猫 S10", 96, "#192124", True)
    text(draw, (94, 402), "云深处 · 轮足机器人", 40, "#354347")
    text(draw, (94, 539), "高台 / 楼梯 / 平地 / 石子路", 31, "#354347")
    draw.line((94, 641, 773, 641), fill="#bfcacd", width=2)
    text(draw, (94, 690), "31", 78, "#192124", True)
    text(draw, (94, 794), "必经目标点", 27, "#526064")
    text(draw, (442, 690), "30", 78, "#192124", True)
    text(draw, (442, 794), "逐站任务", 27, "#526064")
    return canvas


DIAGRAM_CHAPTERS = [
    (10, 13, None, "方案总览", "定位支撑决策，VLN 连接目标与行动，执行层闭环确认到点。"),
    (13, 17, (0.004, 0.805, 0.995, 0.993), "01  高保真高斯地图与训练", "实景扫描 → 高斯仿真 → 轨迹采样与修正 → 导航策略训练"),
    (17, 21, (0.008, 0.142, 0.270, 0.795), "02  可信三维定位", "全局重定位与连续跟踪，为局部 Goal Point 转换提供可信位姿。"),
    (21, 27, (0.271, 0.142, 0.677, 0.795), "03  VLN 模型", "三视图或单视图 + 多帧观测 + odom + Goal Point + 语义输入"),
    (27, 32, (0.680, 0.142, 0.994, 0.795), "04  执行与逐站确认", "局部轨迹 → 安全执行 → STOP 与距离确认 → 下发下一站"),
]


def diagram_frame(image, chapter):
    canvas = Image.new("RGB", (W, H), BG)
    x, y, width, height = paste_contained(canvas, image, (92, 18, 1736, 924))
    focus = chapter[2]
    if focus:
        a, b, c, d = focus
        box = (x + round(a * width), y + round(b * height), x + round(c * width), y + round(d * height))
        active = canvas.crop(box)
        canvas = ImageEnhance.Brightness(canvas).enhance(0.55)
        canvas.paste(active, box[:2])
        draw = ImageDraw.Draw(canvas)
        draw.rectangle(box, outline=CYAN, width=3)
    caption(canvas, chapter[3], chapter[4])
    return canvas


def read_clip(module, path):
    reader = module.read_frames(str(path), pix_fmt="rgb24")
    metadata = next(reader)
    frames = [Image.frombytes("RGB", tuple(metadata["size"]), data) for data in reader]
    reader.close()
    assert frames and metadata["source_size"] == metadata["size"]
    return frames, metadata


def source_index(t, fps, count):
    return min(max(math.floor(t * fps + 1e-6), 0), count - 1)


def inference_frame(t, spec, clip, result):
    frames, metadata = clip
    local = t - spec["start"]
    index = source_index(local, metadata["fps"], len(frames))
    canvas = Image.new("RGB", (W, H), BG)
    rect = paste_contained(canvas, frames[index], (0, 96, W, 852))
    assert rect == (0, 96, W, 852), rect
    draw = ImageDraw.Draw(canvas)
    text(draw, (40, 17), f"VLN 仿真推理  /  {spec['title']}", 33, WHITE, True)
    text(draw, (42, 60), f"EPOCH 2 · ROUTE {spec['ordinal']:02d} · 前视画面 + 俯视轨迹 · 独立 episode", 21, MUTED)
    text(draw, (1570, 25), f"P{result['startIndex']:02d} → P{result['goalIndex']:02d}", 28, CYAN)
    if index == len(frames) - 1:
        detail = result["models"]["epoch2"]
        subtitle = f"模型 STOP  ·  最终误差 {detail['navErrorM']:.3f} m  ·  路径长度 {detail['pathLengthM']:.2f} m"
        heading = "本段推理结束"
    else:
        heading = "模型推理 / 路径执行"
        subtitle = "局部目标引导路径选择，模型持续预测轨迹并执行。"
    caption(canvas, heading, subtitle)
    return canvas


def results_frame(metrics):
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)
    text(draw, (92, 120), "EPOCH 2  /  SIMULATION EVALUATION", 28, CYAN)
    text(draw, (86, 190), "30 段独立仿真评测", 72, WHITE, True)
    values = [
        ("30 / 30", "模型输出 STOP"),
        (f"{metrics['nav_error_mean_m']:.3f} m", "平均终点误差"),
        ("30 / 30", "STOP + 终点误差 ≤ 1 m"),
    ]
    for i, (value, label) in enumerate(values):
        x = 92 + i * 600
        draw.line((x, 380, x + 500, 380), fill="#435358", width=2)
        text(draw, (x, 435), value, 77, WHITE, True)
        text(draw, (x + 4, 545), label, 30, MUTED)
    draw.line((92, 681, 1818, 681), fill="#435358", width=2)
    text(draw, (92, 753), "同场景、同基础路段的起点扰动验证；30 段分别初始化。", 28, MUTED)
    text(draw, (92, 801), "仿真指标，不作为实机比赛成绩。", 28, MUTED)
    return canvas


def ending(images, t):
    canvas = scrim(aerial(images["aerial2"], (t - 60) / 4), 0.72)
    draw = ImageDraw.Draw(canvas)
    centered(draw, 312, "恐怖如斯战队", 92, WHITE, True)
    centered(draw, 471, "高保真场景训练 × 可信定位 × VLN 导航", 40, CYAN)
    centered(draw, 605, "让视觉语言导航真正落地园区巡检", 49, WHITE, True)
    centered(draw, 819, "GOAI 2026 总决赛 · 产业园区全地形巡逻挑战赛", 29, WHITE)
    return canvas


def subtitle_time(value):
    ms = round(value * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}.{ms % 1000:03}"


async def synthesize(voice_dir):
    import edge_tts

    voice_dir.mkdir(parents=True, exist_ok=True)
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    for index, (_, _, words) in enumerate(NARRATION):
        path = voice_dir / f"{index:02}.mp3"
        stamp = voice_dir / f"{index:02}.sha256"
        digest = hashlib.sha256((words + "zh-CN-YunxiNeural+8%").encode()).hexdigest()
        if path.exists() and path.stat().st_size > 1000 and stamp.exists() and stamp.read_text() == digest:
            continue
        await asyncio.wait_for(edge_tts.Communicate(words, "zh-CN-YunxiNeural", rate="+8%", proxy=proxy).save(str(path)), 45)
        stamp.write_text(digest)
        print(f"Narration {index + 1}/{len(NARRATION)}", flush=True)


def audio_mix(ffmpeg, voice_dir, output):
    rate = 48000
    length = DURATION * rate
    speech = np.zeros(length, dtype=np.float32)
    activity = np.zeros(length, dtype=np.float32)
    report = []
    for i, (start, end, words) in enumerate(NARRATION):
        path = voice_dir / f"{i:02}.mp3"
        command = [ffmpeg, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(rate), "pipe:1"]
        raw = np.frombuffer(subprocess.check_output(command), dtype="<f4")
        original_duration = len(raw) / rate
        speed = max(1.0, original_duration / (end - start - 0.08))
        command[5:5] = ["-af", f"atempo={speed:.6f},loudnorm=I=-18:TP=-2:LRA=7"]
        samples = np.frombuffer(subprocess.check_output(command), dtype="<f4").copy()
        offset = round(start * rate)
        count = min(len(samples), length - offset)
        assert count / rate < end - start + 0.15
        speech[offset:offset + count] += samples[:count]
        activity[max(0, offset - rate // 8):min(length, offset + count + rate // 5)] = 1
        report.append({"start": start, "end": end, "text": words, "source_duration": original_duration, "tempo": speed})

    # Original restrained pulse score, not borrowed music.
    t = np.arange(length, dtype=np.float32) / rate
    music = np.zeros(length, dtype=np.float32)
    chords = [(110, 130.81, 164.81), (87.31, 110, 130.81), (98, 123.47, 146.83), (82.41, 98, 123.47)]
    for i in range(16):
        lo, hi = i * 4 * rate, min((i + 1) * 4 * rate, length)
        local = t[lo:hi] - i * 4
        env = np.minimum(local / 0.18, 1) * np.minimum((4 - local) / 0.4, 1)
        for f in chords[i % 4]:
            music[lo:hi] += 0.025 * np.sin(2 * np.pi * f * local) * env
    for beat in np.arange(0, DURATION, 0.5):
        lo = round(beat * rate)
        n = min(round(0.18 * rate), length - lo)
        local = np.arange(n) / rate
        kick = np.sin(2 * np.pi * (64 * local + 2.8 * (1 - np.exp(-local * 23)))) * np.exp(-local * 27)
        music[lo:lo + n] += (0.10 if round(beat * 2) % 4 == 0 else 0.045) * kick
    music *= (1 - 0.72 * activity) * np.minimum(t / 0.5, 1) * np.minimum((DURATION - t) / 1.5, 1)
    mixed = speech + music
    peak = float(np.max(np.abs(mixed)))
    mixed *= min(1, 0.93 / max(peak, 1e-6))
    stereo = np.column_stack((mixed, mixed)).astype(np.float32)
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes((stereo * 32767).astype("<i2").tobytes())
    return {"voice": "zh-CN-YunxiNeural", "synthetic_narration": True, "music": "original synthesized pulse score", "peak_before_limit": peak, "segments": report}


def publish_web_video(ffmpeg, source, destination):
    temporary = destination.with_name(destination.stem + ".webtmp.mp4")
    subprocess.run([
        ffmpeg, "-y", "-v", "error", "-i", str(source),
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-maxrate", "2400k", "-bufsize", "4800k", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(temporary),
    ], check=True)
    if temporary.stat().st_size >= 25 * 1024 * 1024:
        raise RuntimeError("Web video exceeds the preview host's 25 MiB asset limit")
    os.replace(temporary, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--video-tools", type=Path, required=True)
    parser.add_argument("--aerial1", type=Path, required=True)
    parser.add_argument("--aerial2", type=Path, required=True)
    parser.add_argument("--robot", type=Path, required=True)
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(args.video_tools))
    import imageio_ffmpeg as video

    root = args.project_root
    media = root / "public/media"
    work = root / "assets-private/film-v2"
    qa = work / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    inputs = work / "inputs"
    inputs.mkdir(exist_ok=True)
    images = {}
    for name in ("aerial1", "aerial2", "robot"):
        source = getattr(args, name)
        target = inputs / f"{name}.png"
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        images[name] = Image.open(target).convert("RGB")
    diagram = Image.open(media / "kbrs-vln-architecture-academic-dark-v1.png").convert("RGB")
    manifest = json.loads((root / "public/data/routes.json").read_text(encoding="utf-8"))
    metrics = json.loads((root / "public/data/metrics.json").read_text(encoding="utf-8"))["epoch2"]
    results = {x["ordinal"]: x for x in manifest["routes"]}
    clips = {s["ordinal"]: read_clip(video, media / "routes/epoch2" / s["file"]) for s in CLIP_SCHEDULE}
    diagrams = {c[0]: diagram_frame(diagram, c) for c in DIAGRAM_CHAPTERS}
    product = product_frame(images)
    statistics = results_frame(metrics)

    def frame(t):
        if t < 7:
            return opening(images, t)
        if t < 10:
            return product.copy()
        if t < 32:
            chapter = next(c for c in DIAGRAM_CHAPTERS if c[0] <= t < c[1])
            return diagrams[chapter[0]].copy()
        if t < 54:
            spec = next(s for s in CLIP_SCHEDULE if s["start"] <= t < s["end"])
            return inference_frame(t, spec, clips[spec["ordinal"]], results[spec["ordinal"]])
        if t < 60:
            return statistics.copy()
        return ending(images, t)

    checks = [1.5, 5, 8, 11, 15, 19, 24, 29, 34, 37.7, 42, 46.7, 49, 53.7, 57, 62]
    sheet = Image.new("RGB", (1920, 4 * 300), BG)
    for i, time in enumerate(checks):
        image = frame(time)
        image.save(qa / f"frame-{time:05.1f}.jpg", quality=95)
        sheet.paste(image.resize((480, 270)), ((i % 4) * 480, (i // 4) * 300))
        text(ImageDraw.Draw(sheet), ((i % 4) * 480 + 12, (i // 4) * 300 + 274), f"{time:04.1f}s", 18)
    sheet.save(qa / "storyboard.jpg", quality=96)
    validation = {"duration_seconds": DURATION, "output_size": [W, H], "fps": FPS, "clips": [], "narration": NARRATION}
    for spec in CLIP_SCHEDULE:
        frames, metadata = clips[spec["ordinal"]]
        assert len(frames) / metadata["fps"] <= spec["end"] - spec["start"]
        indices = {source_index(t / FPS, metadata["fps"], len(frames)) for t in range((spec["end"] - spec["start"]) * FPS)}
        assert indices == set(range(len(frames)))
        validation["clips"].append({**spec, "source_size": metadata["source_size"], "source_frames": len(frames), "source_fps": metadata["fps"], "all_source_frames_included": True, "destination_rect": [0, 96, W, 852], "crop": False, "stretch": False, "final_frame_held": True})
    (qa / "render-validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.preview_only:
        print(qa / "storyboard.jpg", flush=True)
        return

    asyncio.run(synthesize(work / "voice"))
    ffmpeg = video.get_ffmpeg_exe()
    audio = audio_mix(ffmpeg, work / "voice", work / "mix.wav")
    validation["audio"] = audio
    masters = work / "masters"
    masters.mkdir(exist_ok=True)
    clean = masters / f"{STEM}_clean.mp4"
    writer = video.write_frames(str(clean), (W, H), fps=FPS, codec="libx264", quality=8, pix_fmt_in="rgb24", pix_fmt_out="yuv420p", macro_block_size=1, output_params=["-preset", "fast", "-movflags", "+faststart"])
    writer.send(None)
    try:
        for i in range(DURATION * FPS):
            writer.send(np.asarray(frame(i / FPS)).tobytes())
            if i % (FPS * 4) == 0:
                print(f"Render {i / FPS:.0f}/{DURATION}s", flush=True)
    finally:
        writer.close()
    full = masters / f"{STEM}_64s.mp4"
    subprocess.run([ffmpeg, "-y", "-v", "error", "-i", str(clean), "-i", str(work / "mix.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(full)], check=True)
    publish_web_video(ffmpeg, full, media / full.name)
    publish_web_video(ffmpeg, clean, media / clean.name)
    teaser = media / f"{STEM}_teaser_15s.mp4"
    writer = video.write_frames(str(teaser), (W, H), fps=FPS, codec="libx264", quality=7, pix_fmt_out="yuv420p", macro_block_size=1, output_params=["-preset", "fast", "-movflags", "+faststart"])
    writer.send(None)
    try:
        for i in range(15 * FPS):
            writer.send(np.asarray(opening(images, (i / FPS) % 7, titles=False)).tobytes())
    finally:
        writer.close()
    frame(5).save(media / f"{STEM}_poster.jpg", quality=97)
    vtt = "WEBVTT\n\n" + "\n\n".join(f"{subtitle_time(a)} --> {subtitle_time(b)}\n{words}" for a, b, words in NARRATION) + "\n"
    (media / f"{STEM}.zh.vtt").write_text(vtt, encoding="utf-8")
    (qa / "render-validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"full": str(full), "clean": str(clean), "teaser": str(teaser), "qa": str(qa)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
