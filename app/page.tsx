import {
  ArrowDown,
  Box,
  ExternalLink,
  GitFork,
  Play,
  Route,
  ScanLine,
  ShieldCheck,
  Target,
} from "lucide-react";
import Image from "next/image";
import { RouteExplorer } from "@/components/route-explorer";
import { publicPath } from "@/lib/public-path";

const sceneUrl = "https://lcc-viewer.xgrids.cloud/pub/9e0212b2-49ff-419e-8c24-2c8a21e8bcc5";
const repositoryUrl = "https://github.com/tangyipeng100/GOAI2026_kbrs";

export default function Home() {
  return (
    <div className="site-shell">
      <header className="site-nav">
        <a className="brand-lockup" href="#top" aria-label="返回首页">
          <span className="brand-mark">KBRS</span>
          <span>
            <strong>恐怖如斯战队</strong>
            <small>GOAI 2026 · Embodied Future</small>
          </span>
        </a>
        <nav aria-label="页面导航">
          <a href="#system">方案</a>
          <a href="#film">影片</a>
          <a href="#scene">场景</a>
          <a href="#route">推理</a>
          <a href="#opensource">开源</a>
        </nav>
        <a className="nav-scene-link" href={sceneUrl} target="_blank" rel="noreferrer">
          <Box size={17} aria-hidden="true" />
          <span>三维场景</span>
          <ExternalLink size={14} aria-hidden="true" />
        </a>
      </header>

      <main>
        <section id="top" className="hero-stage">
          <video autoPlay muted loop playsInline poster={publicPath("/media/goai_yungu_vln_overview_v2_poster.jpg")} aria-label="云谷中心赛场俯视">
            <source src={publicPath("/media/goai_yungu_vln_overview_v2_teaser_15s.mp4")} type="video/mp4" />
          </video>
          <div className="hero-shade" />
          <div className="hero-copy">
            <p className="event-line">赛道四 · 具身未来 / 赛题二 · 产业园区全地形巡逻挑战赛</p>
            <h1>视觉语言导航<br />园区巡检系统</h1>
            <p className="hero-statement">让视觉语言导航真正落地园区巡检</p>
            <p className="hero-description">
              面向云谷中心真实赛场，以可信定位、高保真高斯场景和 Goal Point VLN，驱动山猫 S10 完成 31 个必经点的逐站导航。
            </p>
            <div className="hero-actions">
              <a className="primary-action" href="#film">
                <Play size={18} fill="currentColor" aria-hidden="true" />
                播放完整影片
              </a>
              <a className="secondary-action" href="#system">
                查看导航方案 <ArrowDown size={17} aria-hidden="true" />
              </a>
            </div>
          </div>
          <div className="hero-proof" aria-label="方案关键数据">
            <div><strong>31</strong><span>必经目标点</span></div>
            <div><strong>30</strong><span>逐站导航任务</span></div>
            <div><strong>30 / 30</strong><span>模型输出 STOP</span></div>
            <div><strong>0.255 m</strong><span>平均终点误差</span></div>
          </div>
        </section>

        <section id="system" className="section-band system-section">
          <div className="section-heading system-heading">
            <div>
              <p className="section-kicker">01 / NAVIGATION SYSTEM</p>
              <h2><span>可靠定位助力</span><wbr /><span>视觉语言导航</span><wbr /><span>落地园区巡检</span></h2>
            </div>
            <p>VLN 支持单视图或三视图纯视觉观测部署；逐站精确到点时，可靠定位提供地图坐标与机器人位姿，将目标转换为局部 Goal Point，交由模型决策和安全层执行。</p>
          </div>
          <a className="architecture-diagram" href={publicPath("/media/kbrs-vln-architecture-academic-dark-v1.png")} target="_blank" rel="noreferrer" title="查看完整导航方案图">
            <Image src={publicPath("/media/kbrs-vln-architecture-academic-dark-v1.png")} width={1672} height={941} alt="高保真高斯场景训练、可信三维定位、Goal Point 与语义输入的 VLN 模型，以及山猫 S10 执行框架" />
          </a>
          <div className="system-ledger">
            <div><ScanLine size={22} /><span>可信定位</span><p>双激光雷达、IMU、全局搜索与连续定位。</p></div>
            <div><Target size={22} /><span>VLN 决策</span><p>单视图或三视图纯视觉观测，结合多帧、Goal Point 与语义输入。</p></div>
            <div><ShieldCheck size={22} /><span>安全执行</span><p>局部轨迹、避障、安全仲裁与逐站 STOP。</p></div>
          </div>
        </section>

        <section id="film" className="section-band film-section">
          <div className="section-heading film-heading">
            <div>
              <p className="section-kicker">02 / OVERVIEW FILM</p>
              <h2>完整方案讲解</h2>
            </div>
            <p>64 秒串联赛场俯视、山猫 S10、定位与 VLN 框架，以及阶梯、绕石、穿草三段完整模型仿真推理。</p>
          </div>
          <div className="film-stage">
            <video className="feature-film" controls playsInline preload="metadata" poster={publicPath("/media/goai_yungu_vln_overview_v2_poster.jpg")}>
              <source src={publicPath("/media/goai_yungu_vln_overview_v2_64s.mp4")} type="video/mp4" />
              <track kind="captions" src={publicPath("/media/goai_yungu_vln_overview_v2.zh.vtt")} srcLang="zh" label="中文讲解" />
            </video>
          </div>
          <div className="film-ledger">
            <span>中文配音与字幕</span>
            <span>完整 16:9 画面</span>
            <span>三段 VLN 仿真推理</span>
            <span>各路段独立初始化</span>
          </div>
        </section>

        <section className="section-band mission-section">
          <div className="mission-copy">
            <p className="section-kicker">03 / PATROL MISSION</p>
            <h2>把长路线，拆成可确认的逐站任务</h2>
            <p>
              比赛要求机器人依次经过全部目标点。工程系统只在当前站完成并确认停车后，才下发下一站，从而把 31 点巡逻转化为 30 段可验证导航任务。
            </p>
            <ol className="mission-steps">
              <li><span>01</span><div><strong>定位当前位姿</strong><p>持续输出地图坐标与定位质量。</p></div></li>
              <li><span>02</span><div><strong>下发局部 Goal Point</strong><p>结合语义指令生成局部导航决策。</p></div></li>
              <li><span>03</span><div><strong>停车并确认到点</strong><p>模型输出 STOP 后进入下一站任务。</p></div></li>
            </ol>
          </div>
          <figure className="route-map-figure">
            <Image src={publicPath("/media/route-map.png")} alt="云谷中心 31 个必经点和 30 段导航路线" width={1600} height={1000} priority />
            <figcaption>云谷中心巡逻点序列 · 起点与终点以红色标记</figcaption>
          </figure>
        </section>

        <section id="scene" className="section-band scene-section">
          <div className="section-heading scene-heading">
            <div>
              <p className="section-kicker">04 / GAUSSIAN SCENE</p>
              <h2>从真实扫描，建立高保真训练与验证场景</h2>
            </div>
            <p>高斯地图提供接近真实赛场的视觉观测；碰撞网格和 NavMesh 提供可通行几何，共同支撑轨迹采样、模型训练与仿真验证。</p>
          </div>
          <div className="gaussian-frame">
            <iframe src={sceneUrl} title="云谷中心 Gaussian 场景" loading="lazy" allowFullScreen />
            <div className="gaussian-label">
              <span>云谷中心 · 高斯场景</span>
              <a href={sceneUrl} target="_blank" rel="noreferrer">
                全屏打开 <ExternalLink size={14} aria-hidden="true" />
              </a>
            </div>
          </div>
        </section>

        <section id="route" className="section-band route-section">
          <div className="section-heading route-heading">
            <div>
              <p className="section-kicker">05 / INFERENCE REPLAYS</p>
              <h2>逐路段模型推理回放</h2>
            </div>
            <p>选择路段和模型版本，查看前视画面、俯视轨迹、STOP、终点误差与完整执行过程。</p>
          </div>
          <RouteExplorer />
        </section>

        <section id="evidence" className="section-band evidence-section">
          <div className="section-heading evidence-heading">
            <div>
              <p className="section-kicker">06 / QUANTITATIVE RESULTS</p>
              <h2>模型推理量化结果</h2>
            </div>
            <p>结果来自同一云谷高斯仿真场景、同基础路段的起点扰动验证，不代表跨场景或实机比赛成绩。</p>
          </div>
          <div className="proof-metrics">
            <div><strong>30 / 30</strong><span>模型输出 STOP</span></div>
            <div><strong>0.255 m</strong><span>平均终点误差</span></div>
            <div><strong>30 / 30</strong><span>STOP + 终点误差 ≤ 1 m</span></div>
          </div>
          <div className="metric-table" role="table" aria-label="epoch1 和 epoch2 指标对比">
            <div className="metric-row metric-head" role="row"><span>指标</span><span>EPOCH 1</span><span>EPOCH 2</span></div>
            <div className="metric-row" role="row"><span>平均终点误差</span><span>0.642 m</span><strong>0.255 m</strong></div>
            <div className="metric-row" role="row"><span>STOP + ≤ 1 m</span><span>27 / 30</span><strong>30 / 30</strong></div>
            <div className="metric-row" role="row"><span>STOP + ≤ 0.25 m</span><span>12 / 30</span><strong>14 / 30</strong></div>
            <div className="metric-row" role="row"><span>碰撞记录</span><span>175</span><strong>41</strong></div>
            <div className="metric-row" role="row"><span>卡住退出</span><span>3</span><strong>0</strong></div>
          </div>
        </section>

        <section className="section-band data-section">
          <div className="data-copy">
            <p className="section-kicker">07 / TRAINING DATA</p>
            <h2>从 30 个基础路段，扩增为 230 条训练与验证轨迹</h2>
            <p>每段加入起点位置、朝向和定位噪声扰动。训练样本包含多帧历史观测、当前单视图或左／前／右三视图、里程计、语义指令与局部 Goal Point。</p>
          </div>
          <dl className="data-stats">
            <div><dt>训练轨迹</dt><dd>200</dd></div>
            <div><dt>验证轨迹</dt><dd>30</dd></div>
            <div><dt>训练样本</dt><dd>6,140</dd></div>
            <div><dt>基础路段</dt><dd>30</dd></div>
          </dl>
        </section>

        <section id="opensource" className="section-band open-section">
          <div className="open-repo">
            <div>
              <p className="section-kicker">08 / REPOSITORY</p>
              <h2>项目开源仓库</h2>
              <p>展示页面、数据格式、Goal Point 坐标转换与评测工具统一收录于项目仓库。</p>
            </div>
            <a className="repo-link" href={repositoryUrl} target="_blank" rel="noreferrer" aria-label="打开 GOAI2026_kbrs GitHub 仓库">
              <GitFork size={28} aria-hidden="true" />
              <span><small>GitHub Repository</small><strong>GOAI2026_kbrs</strong></span>
              <ExternalLink size={18} aria-hidden="true" />
            </a>
          </div>
        </section>
      </main>

      <footer>
        <div><strong>恐怖如斯战队</strong><span>让视觉语言导航真正落地园区巡检</span></div>
        <div><Route size={17} aria-hidden="true" /><span>GOAI 2026 · 产业园区全地形巡逻挑战赛</span></div>
      </footer>
    </div>
  );
}
