#!/usr/bin/env python3
"""Summarize public navigation metrics from evaluator summary.json files."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--success-distance", type=float, default=0.25)
    args = parser.parse_args()
    summaries = [json.loads(path.read_text(encoding="utf-8")) for path in args.root.rglob("summary.json")]
    errors = [float(s["nav_error_m"]) for s in summaries]
    stop = [bool(s.get("stop_received")) for s in summaries]
    success = [did_stop and error <= args.success_distance for did_stop, error in zip(stop, errors)]
    result = {
        "episodes": len(summaries),
        "stopCount": sum(stop),
        "successDistanceM": args.success_distance,
        "successCount": sum(success),
        "successRate": sum(success) / len(success) if success else 0,
        "meanNavErrorM": statistics.fmean(errors) if errors else None,
        "medianNavErrorM": statistics.median(errors) if errors else None,
        "maxNavErrorM": max(errors, default=None),
        "collisions": sum(int(s.get("collisions", 0)) for s in summaries),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
