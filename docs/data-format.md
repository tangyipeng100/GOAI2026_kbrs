# 数据格式

## 路段

每个相邻 checkpoint 形成一条基础路段，例如 `route_012_p12_to_p13`。每个路段至少包含：

```json
{
  "route_id": "route_012_p12_to_p13",
  "start": {"position": [0.0, 0.0, 0.0], "yaw": 0.0},
  "goal": {"position": [1.0, 0.0, 2.0]},
  "instruction": "Proceed to the goal and stop on the visual marker when it is visible.",
  "frames": []
}
```

## 单帧监督

训练样本使用历史 front 图像、当前 left/front/right、odom、局部 GoalPoint、未来 waypoint、航向和 STOP 标签。终点附近帧保留视觉红心，并用 STOP 样本覆盖停车阶段。

```json
{
  "images": ["history_front_*.jpg", "left.jpg", "front.jpg", "right.jpg"],
  "odom": {"x": 0.0, "y": 0.0, "yaw": 0.0},
  "input_target": [1.0, 0.0],
  "future_waypoints": [[0.3, 0.0], [0.6, 0.1]],
  "arrive": false
}
```

`input_target` 的轴定义、单位和归一化必须与训练脚本一致。参考实现见 `examples/goal_transform.py`。

## 扰动

- 起点位置小幅横向/纵向偏移；
- 初始 yaw 小幅旋转；
- odom 与目标坐标加入受控噪声；
- 保持语义路线、障碍侧和终点视觉目标不被扰动破坏；
- route12 与 route25 使用人工修正后的基准轨迹，分别规避石头和保持穿越草地的路线意图。

## 公开脱敏

公开样本只保留通用字段、相对坐标和授权图片。账号、绝对服务器路径、密钥、未授权原始扫描以及完整模型权重不得写入公开仓库。
