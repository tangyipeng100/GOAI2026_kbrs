#!/usr/bin/env python3
"""Build the public route manifest and optional local video bundle.

The script intentionally exports a small, stable schema. Raw evaluator metadata can
contain machine-specific paths and is never copied into the public directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


MODELS = ("epoch1", "epoch2")
CORRECTED_ORDINALS = {12, 25}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def as_number(value: str):
    if value == "":
        return None
    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return value


def load_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def source_episode(eval_root: Path, model: str, ordinal: int, route_id: str) -> Path:
    subset = "corrected" if ordinal in CORRECTED_ORDINALS else "ordinary"
    return eval_root / f"{model}_full_{subset}" / f"handscanner_{model}" / route_id


def public_route_id(route_id: str) -> str:
    return route_id.removesuffix("_v04")


def find_font(size: int):
    candidates = (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def render_route_map(points: list[dict], output: Path):
    width, height = 1600, 1000
    margin = 110
    coords = [(float(p["scanner_xyz"][0]), float(p["scanner_xyz"][1])) for p in points]
    xs, ys = zip(*coords)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    scale = min((width - 2 * margin) / max(max_x - min_x, 1), (height - 2 * margin) / max(max_y - min_y, 1))

    def project(point):
        x, y = point
        return (
            int(margin + (x - min_x) * scale),
            int(height - margin - (y - min_y) * scale),
        )

    image = Image.new("RGB", (width, height), "#080a0b")
    draw = ImageDraw.Draw(image)
    projected = [project(c) for c in coords]
    draw.line(projected, fill="#5ce1e6", width=8, joint="curve")

    title_font = find_font(42)
    body_font = find_font(22)
    label_font = find_font(18)
    draw.text((54, 42), "云谷中心 · 31 点巡逻路线", font=title_font, fill="#f7f8f8")
    draw.text((56, 96), "30 段连续任务 · 逐站下发目标", font=body_font, fill="#8e989b")

    for point, (x, y) in zip(points, projected):
        index = int(point["index"])
        radius = 10 if index not in (1, 32) else 15
        color = "#ff3b30" if index in (1, 32) else "#f4f6f6"
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline="#080a0b", width=3)
        draw.text((x + 13, y - 22), str(index), font=label_font, fill="#d9dedf")

    draw.rounded_rectangle((48, height - 98, 510, height - 42), radius=6, fill="#111619", outline="#273033")
    draw.text((68, height - 82), "31 个必经点 · 30 段独立导航任务", font=label_font, fill="#a8b0b2")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, quality=94)


def export_video(source: Path, destination: Path, ffmpeg: str | None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not ffmpeg:
        shutil.copy2(source, destination)
        return

    temporary = destination.with_name(f"{destination.stem}.h264.mp4")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(temporary),
        ],
        check=True,
    )
    os.replace(temporary, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--episodes-csv", type=Path, required=True)
    parser.add_argument("--metrics-json", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--contact-sheet-root", type=Path)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--copy-videos", action="store_true")
    parser.add_argument(
        "--ffmpeg",
        help="Optional FFmpeg executable. When set, public videos are converted to browser-compatible H.264.",
    )
    args = parser.parse_args()

    catalog = read_json(args.catalog)
    point_data = read_json(args.points)
    metrics = read_json(args.metrics_json)
    rows = load_rows(args.episodes_csv)
    catalog_by_id = {r["route_id"]: r for r in catalog["routes"]}
    ordered_points = [
        next(p for p in point_data["points"] if int(p["index"]) == int(index))
        for index in catalog["point_order"]
    ]

    routes: dict[int, dict] = {}
    for row in rows:
        route_id = row["route_id"]
        catalog_row = catalog_by_id[route_id]
        ordinal = int(catalog_row["segment_ordinal"])
        item = routes.setdefault(
            ordinal,
            {
                "ordinal": ordinal,
                "routeId": public_route_id(route_id),
                "episodeRouteId": route_id,
                "startIndex": int(catalog_row["measurement_start_index"]),
                "goalIndex": int(catalog_row["measurement_goal_index"]),
                "tier": catalog_row["tier"],
                "corrected": ordinal in CORRECTED_ORDINALS,
                "models": {},
            },
        )
        model = row["model"]
        episode = source_episode(args.eval_root, model, ordinal, route_id)
        video_rel = f"/media/routes/{model}/{public_route_id(route_id)}.mp4"
        poster_rel = f"/media/contact-sheets/{model}/{route_id}.jpg"
        public_values = {
            "video": video_rel,
            "poster": poster_rel,
            "navErrorM": as_number(row["nav_error_m"]),
            "initialGoalDistanceM": as_number(row["initial_goal_distance_m"]),
            "pathLengthM": as_number(row["path_length_m"]),
            "steps": as_number(row["steps"]),
            "collisions": as_number(row["collisions"]),
            "stopReceived": bool(int(row["stop_received"])),
            "success025m": bool(int(row["primary_success"])),
            "success1m": bool(int(row["legacy_1m_success"])),
            "terminationReason": row["termination_reason"],
        }
        item["models"][model] = public_values

        if args.copy_videos:
            destination = args.public_root / video_rel.lstrip("/")
            export_video(episode / "habitat_omninav_bridge.mp4", destination, args.ffmpeg)

        if args.contact_sheet_root:
            source_poster = args.contact_sheet_root / model / f"{route_id}.jpg"
            if source_poster.exists():
                destination = args.public_root / poster_rel.lstrip("/")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_poster, destination)

    data_dir = args.public_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    route_manifest = {
        "schemaVersion": 1,
        "project": "恐怖如斯·视觉语义注入具身导航巡检方案",
        "disclaimer": "30 个路段均为独立初始化的仿真 episode，不代表一次无重置连续运行。",
        "pointOrder": catalog["point_order"],
        "points": [
            {
                "index": int(p["index"]),
                "scannerXYZ": p["scanner_xyz"],
                "habitatXYZ": p["habitat_xyz"],
            }
            for p in ordered_points
        ],
        "routes": [routes[key] for key in sorted(routes)],
    }
    (data_dir / "routes.json").write_text(json.dumps(route_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (data_dir / "dataset.json").write_text(
        json.dumps(
            {
                "routes": 230,
                "baseSegments": 30,
                "checkpoints": 31,
                "trainRoutes": 200,
                "valRoutes": 30,
                "trainSamples": 6140,
                "valSamples": 930,
                "imagesPerSample": 23,
                "instruction": catalog["instruction_en"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    render_route_map(ordered_points, args.public_root / "media" / "route-map.png")
    print(json.dumps({"routes": len(routes), "points": len(ordered_points), "videosCopied": args.copy_videos}, ensure_ascii=False))


if __name__ == "__main__":
    main()
