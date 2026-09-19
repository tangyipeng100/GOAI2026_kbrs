import {
  Box,
  BrainCircuit,
  Code2,
  ExternalLink,
  MapPinned,
  Play,
  Route,
  ScanLine,
  ShieldCheck,
} from "lucide-react";
import Image from "next/image";
import { RouteExplorer } from "@/components/route-explorer";

const pipeline = [
  { icon: ScanLine, name: "定位建图", detail: "双激光雷达、IMU 与全局重定位" },
  { icon: Box, name: "数字孪生", detail: "Gaussian 观测、碰撞网格与 NavMesh" },
  { icon: MapPinned, name: "逐站目标", detail: "31 个 checkpoint，按站下发任务" },
  { icon: BrainCircuit, name: "GoalPoint VLN", detail: "视觉、历史、里程计与局部目标融合" },
  { icon: ShieldCheck, name: "执行与安全", detail: "轨迹控制、碰撞约束与 STOP 判定" },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#050607] text-white">
      <section className="hero-stage relative isolate min-h-[92svh] overflow-hidden">
        <video
          className="absolute inset-0 h-full w-full object-cover"
          autoPlay
          muted
          loop
          playsInline
          poster="/media/hero-poster.jpg"
          aria-label="云谷中心 GoalPoint 模型推理演示"
        >
          <source src="/media/goai_yungu_goalnav_teaser_15s.mp4" type="video/mp4" />
          <source src="/media/hero-preview.mp4" type="video/mp4" />
        </video>
        <div className="hero-shade absolute inset-0" />

        <nav className="relative z-10 flex items-center justify-between px-5 py-5 sm:px-10 lg:px-16">
          <a className="brand-lockup" href="#top" aria-label="返回首页">
            <span className="brand-mark">KBRS</span>
            <span className="brand-name">恐怖如斯战队</span>
          </a>
          <div className="hidden items-center gap-7 text-sm text-white/74 md:flex">
            <a href="#scene">数字孪生</a>
            <a href="#route">巡逻路线</a>
            <a href="#evidence">验证结果</a>
            <a href="#opensource">开源方案</a>
          </div>
          <a
            className="icon-link"
            href="https://lcc-viewer.xgrids.cloud/pub/9e0212b2-49ff-419e-8c24-2c8a21e8bcc5"
            target="_blank"
            rel="noreferrer"
            title="打开高斯场景"
          >
            <Box size={18} aria-hidden="true" />
            <span className="hidden sm:inline">进入三维场景</span>
          </a>
        </nav>

        <div id="top" className="relative z-10 flex min-h-[calc(92svh-80px)] items-end px-5 pb-24 sm:px-10 lg:px-16 lg:pb-28">
          <div className="max-w-5xl">
            <p className="event-line">GOAI 2026 总决赛 · 赛道四「具身未来」· 赛题二</p>
            <h1 className="hero-title">
              恐怖如斯<span>·</span>视觉语义注入
              <br />
              具身导航巡检方案
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-white/76 sm:text-lg">
              面向云谷中心产业园区，让云深处山猫 S10 依次经过 31 个目标点，完成定位建图、复杂地形通行与逐站精准停车。
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a className="primary-action" href="#film">
                <Play size={18} fill="currentColor" aria-hidden="true" />
                观看开场影片
              </a>
              <a
                className="secondary-action"
                href="https://www.goaihz.com/tracks?track=embodied"
                target="_blank"
                rel="noreferrer"
              >
                官方赛题 <ExternalLink size={16} aria-hidden="true" />
              </a>
            </div>
          </div>
        </div>

        <div className="hero-proof absolute inset-x-0 bottom-0 z-10 grid grid-cols-2 border-t border-white/15 bg-black/32 backdrop-blur-md sm:grid-cols-4">
          <div><strong>31</strong><span>必经 waypoint</span></div>
          <div><strong>30 / 30</strong><span>epoch2 输出 STOP</span></div>
          <div><strong>0.255 m</strong><span>平均终点误差</span></div>
          <div><strong>230</strong><span>训练与验证轨迹</span></div>
        </div>
      </section>

      <section id="film" className="section-band film-section">
        <div className="section-heading">
          <p className="section-kicker">OPENING FILM / 60 SEC</p>
          <h2>一条路线，看见完整任务</h2>
          <p>数字孪生镜头展示赛题路线，随后切入真实模型仿真推理。二者在片中分别标注，不混淆证据边界。</p>
        </div>
        <video className="feature-film" controls playsInline poster="/media/goai_yungu_goalnav_poster.png">
          <source src="/media/goai_yungu_goalnav_full_60s.mp4" type="video/mp4" />
        </video>
        <p className="media-note">数字孪生路线演示 / Digital Twin Visualization</p>
      </section>

      <section id="scene" className="section-band scene-section">
        <div className="section-heading split-heading">
          <div>
            <p className="section-kicker">01 / DIGITAL TWIN</p>
            <h2>真实云谷中心<br />不从抽象地图开始</h2>
          </div>
          <p>高斯场景承担真实感观测，碰撞网格和 NavMesh 提供可通行几何。两类地图各司其职，不把视觉重建等同于导航地图。</p>
        </div>
        <div className="gaussian-frame">
          <iframe
            src="https://lcc-viewer.xgrids.cloud/pub/9e0212b2-49ff-419e-8c24-2c8a21e8bcc5"
            title="云谷中心 Gaussian 场景"
            loading="lazy"
            allowFullScreen
          />
          <div className="gaussian-label">
            <span>LIVE GAUSSIAN VIEWER</span>
            <a href="https://lcc-viewer.xgrids.cloud/pub/9e0212b2-49ff-419e-8c24-2c8a21e8bcc5" target="_blank" rel="noreferrer">
              独立打开 <ExternalLink size={14} />
            </a>
          </div>
        </div>
      </section>

      <section id="route" className="section-band route-section">
        <div className="section-heading split-heading">
          <div>
            <p className="section-kicker">02 / MODEL EVIDENCE</p>
            <h2>30 段逐站推理<br />每一段都可检查</h2>
          </div>
          <p>选择路段和模型版本，直接查看三视图、俯视轨迹、STOP 与终点误差。route12 和 route25 使用人工核验后的正确路线。</p>
        </div>
        <RouteExplorer />
      </section>

      <section className="section-band system-section">
        <div className="section-heading">
          <p className="section-kicker">03 / SYSTEM</p>
          <h2>从定位到执行的完整闭环</h2>
          <p>视觉语言模型并不替代全部工程系统，它在可靠定位、几何约束和底层运动能力之上提供目标理解与局部导航决策。</p>
        </div>
        <div className="pipeline">
          {pipeline.map(({ icon: Icon, name, detail }, index) => (
            <div className="pipeline-node" key={name}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <Icon size={25} aria-hidden="true" />
              <h3>{name}</h3>
              <p>{detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="evidence" className="section-band evidence-section">
        <div className="section-heading split-heading">
          <div>
            <p className="section-kicker">04 / VERIFIED RESULTS</p>
            <h2>精度提升，也保留<br />严格阈值下的不足</h2>
          </div>
          <p>结果来自同一云谷数字孪生场景、同基础路段的起点扰动验证。下列数字不代表跨场景或真实机器人比赛成绩。</p>
        </div>
        <div className="metric-table" role="table" aria-label="epoch1 和 epoch2 指标对比">
          <div className="metric-row metric-head" role="row">
            <span>指标</span><span>EPOCH 1</span><span>EPOCH 2</span>
          </div>
          <div className="metric-row" role="row"><span>平均终点误差</span><span>0.642 m</span><strong>0.255 m</strong></div>
          <div className="metric-row" role="row"><span>STOP + ≤ 1 m</span><span>27 / 30</span><strong>30 / 30</strong></div>
          <div className="metric-row" role="row"><span>STOP + ≤ 0.25 m</span><span>12 / 30</span><strong>14 / 30</strong></div>
          <div className="metric-row" role="row"><span>碰撞记录</span><span>175</span><strong>41</strong></div>
          <div className="metric-row" role="row"><span>卡住退出</span><span>3</span><strong>0</strong></div>
        </div>
      </section>

      <section className="section-band data-section">
        <div className="data-visual">
          <Image
            src="/media/route-map.png"
            alt="云谷中心 31 个 waypoint 和 30 段巡逻路线"
            width={1600}
            height={1000}
          />
        </div>
        <div className="data-copy">
          <p className="section-kicker">05 / TRAINING DATA</p>
          <h2>30 个基础路段，扩增为 230 条训练轨迹</h2>
          <p>每个路段加入起点位置、朝向和定位噪声扰动；每个样本包含 20 张历史前视图、当前左中右三视图、里程计和局部 GoalPoint。</p>
          <dl className="data-stats">
            <div><dt>训练轨迹</dt><dd>200</dd></div>
            <div><dt>验证轨迹</dt><dd>30</dd></div>
            <div><dt>训练样本</dt><dd>6,140</dd></div>
            <div><dt>每样本图像</dt><dd>23</dd></div>
          </dl>
        </div>
      </section>

      <section id="opensource" className="section-band open-section">
        <div className="section-heading split-heading">
          <div>
            <p className="section-kicker">06 / OPEN SOURCE</p>
            <h2>公开接口和证据，<br />不公开内部基础设施</h2>
          </div>
          <p>首批仓库提供展示页、路线清单、GoalPoint 坐标转换、评测汇总和脱敏样本。完整训练服务、私有路径与模型权重不在首批范围。</p>
        </div>
        <div className="code-surface">
          <div className="code-caption"><Code2 size={18} /> examples/goal_transform.py</div>
          <pre><code>{`dx = goal_x - robot_x\ndy = goal_y - robot_y\n\nforward = cos(yaw) * dx + sin(yaw) * dy\nleft    = -sin(yaw) * dx + cos(yaw) * dy\n\ninput_target = [forward, left]`}</code></pre>
          <div className="repo-actions">
            <span>kbrs-goalnav-demo</span>
            <span>Website · Data schema · Evaluation tools</span>
          </div>
        </div>
      </section>

      <footer>
        <div>
          <strong>恐怖如斯战队</strong>
          <span>2026世界人工智能开源大赛（GOAI）总决赛</span>
        </div>
        <div>
          <Route size={17} aria-hidden="true" />
          <span>赛道四 · 具身未来 / 赛题二 · 产业园区全地形巡逻挑战赛</span>
        </div>
      </footer>
    </main>
  );
}
