# Goal Point 推理代码

`inference/runtime.py` 与 `inference/qwen_backend.py` 公开在线评测中的核心推理链路，不包含模型权重、私有服务、仿真器或机器人控制驱动。它们分别负责：

- 把世界目标投影到 episode 坐标，再按实时定位位姿转换成当前机器人局部 `<input_target>`；目标 world position 不随机器人移动而改变。
- 采样多帧历史 front，并按 checkpoint 配置附加当前 front 或 left/front/right；历史图像与当前图像保持训练时的尺寸和顺序。
- 打包四个历史 odom、当前 odom 和动态 Goal Point，共六个归一化坐标；归一化尺度为 0.3 m。
- 生成训练格式的语义 prompt，将图像 token 和结构化 waypoint 输入模型前向。
- 将模型预测的局部 waypoint 转为机器人 `[forward, left, heading]`；五个到达 logit 达到阈值后输出 STOP，并支持连续多次确认。

公开运行时通过 `GoalPointSession` 注入后端：

```python
from inference.runtime import GoalPointSession, Pose, WorldPoint
from inference.qwen_backend import QwenWaypointBackend

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
    num_views=3,
)
result = session.step(
    front=front_pil,
    left=left_pil,
    right=right_pil,
    pose=Pose(odom_forward, odom_left, odom_yaw),
    instruction="Proceed to the goal and stop when you reach it.",
)
```

`loaded_waypoint_model` 必须是兼容结构化 `input_waypoints` 和 waypoint/arrive/heading 输出的模型实现；普通视觉语言模型不能直接替代。模型类、权重和预处理器的安装及授权由使用者自行提供。`GoalPointSession.reset()` 清空历史与 STOP 状态，保留冻结的 world goal。机器人控制与碰撞安全层仍须独立实现。

运行不依赖权重的坐标、历史帧和 STOP 单测：

```bash
python -m unittest discover -s inference/tests -v
```
