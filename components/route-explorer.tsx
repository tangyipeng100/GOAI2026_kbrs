"use client";

import { Check, ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

type ModelResult = {
  video: string;
  poster: string;
  navErrorM: number;
  initialGoalDistanceM: number;
  pathLengthM: number;
  steps: number;
  collisions: number;
  stopReceived: boolean;
  success025m: boolean;
  success1m: boolean;
  terminationReason: string;
};

type RouteEntry = {
  ordinal: number;
  routeId: string;
  episodeRouteId: string;
  startIndex: number;
  goalIndex: number;
  tier: string;
  corrected: boolean;
  models: Record<"epoch1" | "epoch2", ModelResult>;
};

type Manifest = {
  disclaimer: string;
  pointOrder: number[];
  routes: RouteEntry[];
};

export function RouteExplorer() {
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [selected, setSelected] = useState(0);
  const [model, setModel] = useState<"epoch1" | "epoch2">("epoch2");
  const [playing, setPlaying] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    fetch("/data/routes.json")
      .then((response) => {
        if (!response.ok) throw new Error("route manifest unavailable");
        return response.json();
      })
      .then(setManifest)
      .catch(() => setManifest(null));
  }, []);

  const route = manifest?.routes[selected];
  const result = route?.models[model];
  const title = useMemo(
    () => route && `P${String(route.startIndex).padStart(2, "0")} → P${String(route.goalIndex).padStart(2, "0")}`,
    [route],
  );

  function chooseRoute(index: number) {
    setSelected(index);
    setPlaying(false);
  }

  function togglePlayback() {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) {
      void video.play();
      setPlaying(true);
    } else {
      video.pause();
      setPlaying(false);
    }
  }

  if (!manifest || !route || !result) {
    return <div className="route-loading">正在读取 30 段评测证据…</div>;
  }

  return (
    <div className="route-explorer">
      <div className="route-media">
        <video
          ref={videoRef}
          key={`${model}-${route.routeId}`}
          controls
          playsInline
          preload="metadata"
          poster={result.poster}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)}
        >
          <source src={result.video} type="video/mp4" />
        </video>
        <div className="route-media-label">
          <span>MODEL INFERENCE · {model.toUpperCase()}</span>
          <strong>{title}</strong>
        </div>
      </div>

      <aside className="route-panel">
        <div className="segmented" aria-label="选择模型版本">
          {(["epoch1", "epoch2"] as const).map((value) => (
            <button
              type="button"
              key={value}
              className={model === value ? "active" : ""}
              onClick={() => setModel(value)}
            >
              {value.toUpperCase()}
            </button>
          ))}
        </div>

        <div className="route-head">
          <div>
            <p>SEGMENT {String(route.ordinal).padStart(2, "0")}</p>
            <h3>{title}</h3>
          </div>
          {route.corrected && <span className="corrected-badge">人工校正路线</span>}
        </div>

        <dl className="route-metrics">
          <div><dt>最终误差</dt><dd>{result.navErrorM.toFixed(3)} m</dd></div>
          <div><dt>路径长度</dt><dd>{result.pathLengthM.toFixed(2)} m</dd></div>
          <div><dt>控制步数</dt><dd>{result.steps}</dd></div>
          <div><dt>模型 STOP</dt><dd className={result.stopReceived ? "pass" : "fail"}>{result.stopReceived ? "YES" : "NO"}</dd></div>
          <div><dt>≤ 0.25 m</dt><dd>{result.success025m ? "通过" : "未通过"}</dd></div>
          <div><dt>≤ 1.00 m</dt><dd>{result.success1m ? "通过" : "未通过"}</dd></div>
        </dl>

        <div className="route-controls">
          <button type="button" title="上一段" onClick={() => chooseRoute((selected + 29) % 30)}>
            <ChevronLeft size={18} />
          </button>
          <button type="button" className="play-button" onClick={togglePlayback}>
            {playing ? <Pause size={18} /> : <Play size={18} fill="currentColor" />}
            {playing ? "暂停" : "播放本段"}
          </button>
          <button type="button" title="下一段" onClick={() => chooseRoute((selected + 1) % 30)}>
            <ChevronRight size={18} />
          </button>
        </div>
      </aside>

      <div className="route-strip" aria-label="30 段导航路线">
        {manifest.routes.map((item, index) => {
          const itemResult = item.models[model];
          return (
            <button
              type="button"
              key={item.routeId}
              className={index === selected ? "selected" : ""}
              onClick={() => chooseRoute(index)}
              title={`P${item.startIndex} 到 P${item.goalIndex}，误差 ${itemResult.navErrorM.toFixed(3)} 米`}
            >
              <span>{String(item.ordinal).padStart(2, "0")}</span>
              {itemResult.success025m && <Check size={12} />}
            </button>
          );
        })}
      </div>

      <p className="route-disclaimer">{manifest.disclaimer}</p>
    </div>
  );
}
