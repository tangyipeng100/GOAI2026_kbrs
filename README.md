# 恐怖如斯 GoalNav Demo

恐怖如斯战队参加 **2026世界人工智能开源大赛（GOAI）总决赛** 的展示与开源仓库。

- 赛道四：具身未来（Embodied Future）
- 赛题二：产业园区全地形巡逻挑战赛
- 目标平台：云深处山猫 S10
- 方案：Gaussian 数字孪生、SLAM 定位、逐站 GoalPoint 导航、视觉语义提示与安全控制

本仓库优先公开可复用的数据接口、坐标变换、评测汇总、路线播放器和展示网站。完整模型权重、私有训练服务、服务器配置与未经授权的原始数据不在首批开源范围内。

## 已验证结果

| 模型 | STOP | STOP + 误差 <= 1m | STOP + 误差 <= 0.25m | 平均终点误差 | 碰撞记录 |
| --- | ---: | ---: | ---: | ---: | ---: |
| epoch1 | 30/30 | 27/30 | 12/30 | 0.642m | 175 |
| epoch2 | 30/30 | 30/30 | 14/30 | 0.255m | 41 |

这些结果来自同一云谷数字孪生场景中的 30 个独立 episode。每段均独立初始化，并不表示模型一次无重置连续跑完 30 段。数字孪生演示、模型仿真推理和真实 S10 实机结果在页面和视频中分别标注。

## 本地预览

环境要求：Node.js `>=22.13.0`。

```powershell
npm ci
npm run build
npm start
```

默认生产预览地址为 `http://127.0.0.1:8787/`。开发模式可使用 `npm run dev`。

## 公开内容

```text
app/                            展示网站页面与样式
components/route-explorer.tsx   30 段 epoch1/epoch2 回放播放器
examples/goal_transform.py      世界坐标目标到机器人局部 GoalPoint 示例
scripts/prepare_public_assets.py 生成路线、指标和媒体清单
scripts/summarize_eval.py       从逐段 summary 汇总公开指标
scripts/render_opening_film.py  生成 60 秒开场片、15 秒 teaser 和封面
public/data/                    路线、指标与数据集元数据
docs/                           架构、数据格式和第三方边界
```

## 媒体资产

公开部署需要以下目录：

```text
public/media/routes/epoch1/
public/media/routes/epoch2/
public/media/contact-sheets/epoch1/
public/media/contact-sheets/epoch2/
```

每个目录按 `route_001` 到 `route_030` 与 `public/data/routes.json` 对齐。大体积媒体可放在 GitHub Release 或魔搭数据集仓库；页面和代码不依赖 H800、SSH 或本地推理服务。

## 数据与模型接口

模型每一步接收：

1. 20 帧历史 front 图像；
2. 当前 left/front/right 三视图；
3. 里程计与机器人姿态；
4. 英文导航指令；
5. 世界目标转换得到的局部 GoalPoint。

逐站工程控制器只在当前 checkpoint 完成后下发下一目标。训练时每个相邻 checkpoint 形成独立 episode，并对起点、朝向、定位和视觉条件进行小幅扰动。详见 [数据格式](docs/data-format.md) 与 [系统架构](docs/system-architecture.md)。

## 复现工具

```powershell
# 验证坐标变换示例
python examples/goal_transform.py

# 重新汇总逐段评测结果
python scripts/summarize_eval.py --help

# 在拥有授权的本地媒体时重新生成公开资源
python scripts/prepare_public_assets.py --help
```

## 部署

### GitHub Pages / 静态托管

网站不请求私有 API。构建产物可交给支持 Cloudflare Worker/Vinext 的托管服务；如采用纯静态托管，应先将站点导出或改用仓库内的 Docker 方式。

### 魔搭创空间

仓库包含 `Dockerfile`，创空间端口使用 `7860`：

```bash
docker build -t kbrs-goalnav-demo .
docker run --rm -p 7860:7860 kbrs-goalnav-demo
```

## 开源边界

- 本仓库自研代码使用 Apache-2.0 许可证。
- OmniNav、Habitat-Sim/Habitat-GS、Gaussian 场景、山猫 S10 产品素材及第三方字体/图标遵循各自许可证或授权。
- XGRIDS 场景通过原发布链接访问，不在本仓库重新分发原始扫描资产。
- 脱敏样本不得反推出私有服务器地址、账号、真实定位密钥或比赛未公开资料。

详细说明见 [第三方与素材边界](docs/third-party.md)。

## Citation

若本项目中的路线数据格式、GoalPoint 坐标变换或展示组件对你的工作有帮助，请在发布版本提供的 `CITATION.cff` 信息基础上引用本仓库。赛事后的模型卡、数据卡和实机结果会独立追加，不改写已经发布的仿真证据。
