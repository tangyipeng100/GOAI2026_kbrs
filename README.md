# 恐怖如斯战队 | GOAI 2026 园区巡检

**2026 世界人工智能开源大赛（GOAI）总决赛 · 赛道四「具身未来」· 赛题二「产业园区全地形巡逻挑战赛」**

可靠定位助力视觉语言导航落地园区巡检。我们以真实扫描构建高保真高斯场景，结合地图定位、语义指令与局部 Goal Point，让山猫 S10 按顺序完成园区内的逐站导航任务。VLN 模型支持前向单视图或左／前／右三视图纯视觉观测，并利用多帧信息决策；精确到点所需的地图位姿由定位模块提供。

**[打开展示主页](https://tangyipeng100.github.io/GOAI2026_kbrs/)** · **[查看高斯场景](https://lcc-viewer.xgrids.cloud/pub/9e0212b2-49ff-419e-8c24-2c8a21e8bcc5)** · **[观看完整方案视频](public/media/goai_yungu_vln_overview_v2_64s.mp4)** · **[魔搭版图文说明](modelscope_release/README.md)**

[![园区赛场与方案视频封面](public/media/goai_yungu_vln_overview_v2_poster.jpg)](public/media/goai_yungu_vln_overview_v2_64s.mp4)

## 导航方案

![定位、高斯场景训练、Goal Point VLN 与安全执行的系统框架](public/media/kbrs-vln-architecture-academic-dark-v1.png)

1. **场景与训练：**实景扫描生成高斯地图，结合碰撞网格与可通行区域构建仿真环境；按逐站目标采样并校正训练轨迹。
2. **可靠定位：**多传感器融合定位持续输出地图坐标与机器人位姿，将世界目标转换为局部 Goal Point。
3. **视觉语言导航：**利用单视图或三视图、多帧观测、语义指令和 Goal Point 决策路径与 STOP。
4. **安全执行：**控制与避障层执行动作，确认当前站到点后再下发下一目标。方案面向平地、石子路、高台与楼梯等复杂地形。

本仓库的 31 个 waypoint 构成 30 段相邻站点任务。展示页可选择每个路段，回放两个模型版本的推理视频及轨迹、STOP、误差等结果。

## 仿真评测

| 指标（30 段） | Epoch 1 | Epoch 2 |
| --- | ---: | ---: |
| 模型输出 STOP | 27 / 30 | 30 / 30 |
| STOP 且终点误差 ≤ 1 m | 27 / 30 | 30 / 30 |
| STOP 且终点误差 ≤ 0.25 m | 12 / 30 | 14 / 30 |
| 平均终点误差 | 0.642 m | 0.255 m |
| 碰撞记录 | 175 | 41 |

结果来自同一云谷高斯仿真场景中的 **30 个独立初始化 episode**，并非一次无重置连续巡逻，也不代表实机比赛成绩。页面将场景展示、模型推理与后续实机验证分开呈现。

## 仓库内容

| 目录 | 内容 |
| --- | --- |
| `app/`, `components/` | 响应式展示站与逐路段回放播放器 |
| `public/media/`, `public/data/` | 框架图、讲解视频、路线视频、海报与公开指标 |
| `modelscope_release/` | 可独立上传魔搭的图文说明和配套媒体 |
| `examples/goal_transform.py` | 世界目标到机器人局部 Goal Point 的坐标转换示例 |
| `inference/` | [多帧与三视图打包、Goal Point 输入、模型前向和 STOP 判定](docs/inference.md) |
| `scripts/` | 公开资源准备、评测汇总、视频制作及校验工具 |
| `docs/` | 数据格式、系统设计和第三方素材说明 |

原始高斯扫描资产、完整模型权重、私有训练与推理服务不包含在本仓库。媒体与第三方组件的使用边界见 [第三方说明](docs/third-party.md)。

推理模块可用 `python -m unittest discover -s inference/tests -v` 测试，不需要模型权重；实际加载 checkpoint 时需提供兼容的模型定义、预处理器及其授权依赖。

## 本地运行

需要 Node.js 22 及以上版本。

```bash
npm ci
npm run dev
```

开发服务器的地址以终端输出为准。若要本地核验 GitHub Pages 版本：

```bash
npm run build:pages
```

这会在 `out/` 生成带 `/GOAI2026_kbrs` 子路径的静态站。默认 `npm run build` 仍是原有的 Vinext/Cloudflare 构建，魔搭 Docker 入口仍可使用。

## GitHub Pages 部署

推送 `main` 后，[部署工作流](.github/workflows/deploy-pages.yml) 会自动导出并发布网站。首次发布需在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。发布完成后访问 [展示主页](https://tangyipeng100.github.io/GOAI2026_kbrs/)。

仓库代码按 [Apache-2.0](LICENSE) 许可发布；第三方模型、场景与产品素材遵守各自授权。
