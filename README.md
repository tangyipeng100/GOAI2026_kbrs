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

## 导航推理运行

公开推理代码位于 `inference/`，用于复现多帧视觉观测、单视图或左／前／右三视图、里程计、语义指令和局部 Goal Point 到 waypoint 与 STOP 的核心链路。模型结构、checkpoint、仿真器和机器人驱动需由使用者另行准备。

建议使用支持 CUDA 的 Python 环境，并安装与 checkpoint 对应版本的 PyTorch、Transformers、Pillow 和视觉预处理依赖。首先运行不依赖权重的测试，确认坐标变换与状态管理正常：

```bash
python -m unittest discover -s inference/tests -v
```

随后加载兼容 `input_waypoints` 的 VLN checkpoint、processor 和视觉预处理函数，并构造推理后端：

```python
from inference.qwen_backend import QwenWaypointBackend
from inference.runtime import GoalPointSession, Pose, WorldPoint

# 由实际模型工程提供以下三个对象：
# loaded_waypoint_model = ...
# loaded_processor = ...
# vision_preprocessor = ...

backend = QwenWaypointBackend(
    model=loaded_waypoint_model,
    processor=loaded_processor,
    process_vision_info=vision_preprocessor,
    device="cuda",
)

session = GoalPointSession(
    backend,
    start=WorldPoint(start_x, start_y, start_z),
    start_yaw=start_yaw_rad,
    goal=WorldPoint(goal_x, goal_y, goal_z),
    num_views=3,  # 改为 1 可使用前向单视图
)

result = session.step(
    front=front_pil,
    left=left_pil,
    right=right_pil,
    pose=Pose(odom_forward, odom_left, odom_yaw),
    instruction="Proceed to the goal and stop when you reach it.",
)

if result.stop:
    stop_robot()
else:
    execute_local_trajectory(result.trajectory)
```

真实运行时，每个控制周期都要传入最新图像和定位位姿，但 world goal 保持不变；运行时会重新计算局部 `<input_target>`。开始新的导航任务前调用 `session.reset()` 清空多帧历史和 STOP 状态。机器人端还应独立实现轨迹跟踪、避障、速度限制和急停。完整字段和接口说明见 [Goal Point 推理代码](docs/inference.md)。

## GitHub Pages 部署

推送 `main` 后，[部署工作流](.github/workflows/deploy-pages.yml) 会自动导出并发布网站。首次发布需在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。发布完成后访问 [展示主页](https://tangyipeng100.github.io/GOAI2026_kbrs/)。

仓库代码按 [Apache-2.0](LICENSE) 许可发布；第三方模型、场景与产品素材遵守各自授权。
