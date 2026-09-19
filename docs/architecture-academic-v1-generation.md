# Academic Architecture Figure v1

- Output: `public/media/kbrs-vln-architecture-academic-v1.png`
- Generation: built-in image generation/editing tool.
- Use: overview diagram for the project presentation; homepage not changed.
- Reference: previous architecture diagram and the supplied S10 product image.
- Scene insets are illustrative, not evaluation screenshots or evidence of measured performance.

## Initial Restyling Prompt

Use case: style-transfer / infographic-diagram.
Edit the FIRST reference architecture graphic into a CLEAN MINIMAL ACADEMIC SYSTEM FIGURE, preserving the technical meaning but substantially simplifying its presentation. SECOND reference is the accurate S10 hardware shape. This is a figure for a robotics paper and technical presentation, not an advertising poster.

STYLE:
White background, generous whitespace, precise thin gray orthogonal connectors, flat rectangular nodes, consistent grid alignment, small modest corner radius. Low-saturation accents: muted teal for localization, subdued blue for VLN, warm gray for execution, muted sage for simulation training. Black/dark-gray typography, standard clean Chinese sans-serif, mathematical formula in serif. No dark background, NO neon, glow, gradients, metallic UI borders, skyline banner, cinematic scenery, 3D text, marketing slogans or ornamental icons. NO huge red box. Keep a few small informative campus observation thumbnails and a modest clean S10 cutout as research figure insets. High-resolution landscape 16:9, crisp Chinese. Design should be much calmer and simpler than the reference.

TITLE:
"高保真高斯场景与 VLN 导航框架"
Small subtitle: "恐怖如斯战队 · GOAI 2026 · 赛道四 / 赛题二"
Do not repeat title/subtitle elsewhere.

CONTENT / LAYOUT:
Two main horizontal bands: upper two-thirds ONLINE SYSTEM, lower one-quarter OFFLINE SIMULATION & TRAINING. Four clearly identified sections with simple labels "(a) 可信定位", "(b) VLN 模型", "(c) 执行与任务管理", "(d) 高斯仿真与训练". VLN section is slightly wider, visual center. Keep text concise, avoid nested mini-cards everywhere.

(a) LEFT LOCALIZATION:
Small top inputs "双激光雷达 + IMU" and "先验点云地图".
Sequential compact vertical chain:
"时空标定与预处理"
"BBS3D 全局搜索"
"GICP 精配准与一致性验证"
"NDT-OMP + IMU 连续定位"
output "地图位姿 / 定位质量".
Separate short line "健康监督：跟踪 / 退化 / 重定位".
Arrow from map pose output into center's goal-coordinate conversion with label "可信位姿".
Health output is labelled port "定位健康 → 安全仲裁", not connected to VLN predictions.

(b) CENTER VLN:
At top compact two-input goal adapter:
"世界目标点" + trusted pose from (a) → "局部 Goal Point"
a small mathematical line "g_robot = T_robot←map · g_map".
Below, a clear collection of inputs leading down into one simple central model box:
- two tiny camera illustrations with exact labels "左 / 前 / 右三视图" OR "前向单视图" (show the word "或", two alternative input modes, NOT both mandatory)
- "多帧历史观测"
- "运动状态 odom"
- "语义输入"
- local Goal Point from adapter.
ONE prominent rectangle "VLN 模型", smaller subtitle "Goal Point + 语义输入".
Small red-heart symbol only in camera observation inset, caption "可见红心辅助精停".
Output "局部轨迹 + STOP".
CRITICAL naming: ONLY VLN 模型, never OmniNav or SlowFast. No "20帧" or any fixed frame count. No "待联调" or deployment-status disclaimers.

(c) RIGHT EXECUTION:
Arrow from VLN output into "轨迹跟踪与避障", then "安全仲裁", then actual wheeled-legged S10 cutout, then "到点确认".
Safety incoming labelled small port "定位健康".
S10 must match SECOND reference: four articulated legs ending in four RUBBER WHEELS, never paws. Neutral studio cutout, not giant hero robot.
Robot label "山猫 S10 轮足机器人".
Arrival sublabel "STOP + 距离阈值 + 连续稳定".
Separate concise task line "31 个必经点 / 30 段任务" and "完成确认 → 下发下一站".
If arrows cannot be routed cleanly, use explicitly paired labelled ports; do NOT create incorrect loops into headers. Output of arrival returns logically to task manager, whose NEXT WORLD GOAL is fed to goal adapter.
Small bottom row four simple gray terrain profile sketches with exact labels "高台", "楼梯", "平地", "石子路"; caption "复杂地形适应". These are schematic profiles, not fake performance evidence.

(d) OFFLINE FULL-WIDTH BAND:
A minimal horizontal pipeline with one small high-fidelity campus Gaussian-render inset and one little sampled-path illustration, no decorative panorama:
"实景扫描与测量路点"
→ "高清高保真 3D Gaussian 地图"
→ "高斯仿真环境"
→ "轨迹采样与模型训练"
Under Gaussian map: "纹理 / 几何 / 高程".
Under simulation: "碰撞网格 + NavMesh".
Under training: "人工修正 / 姿态扰动 / 仿真评测".
A thin UP arrow from training to VLN model, labelled "数据与策略优化". Keep this offline arrow distinct (dashed); other normal online dataflow solid.
Small footer only: "俯视图用于选点与可视化，不直接输入模型。"

CONNECTION INVARIANTS:
Language/semantics bypass coordinate transform and enters VLN directly.
Coordinate transform receives world goal plus trusted map pose, outputs local Goal Point.
Health status gates safety, never enters trajectory output.
VLN trajectory output enters tracking, not arrival verdict.
Model STOP and localization distance are used for arrival confirmation.
Use few clean arrows and no intersections across text; whitespace is more important than fitting excess text.

Simplify reference aesthetics aggressively; retain necessary information without duplications. Academic, restrained, light, diagram-first. No new factual claims, numbers, success rates or exaggerated adjectives besides the user's established high-fidelity Gaussian map terminology.

## Connector Review Prompt

Precisely edit ONLY the erroneous connectors in this otherwise approved light academic diagram. Preserve all white/low-saturation design, layout, title, Chinese labels, campus thumbnails, four-wheel S10 robot, VLN 模型, Goal Point + 语义输入, 多帧历史观测, and three-view OR single-view modes. Do not redesign. Make the final graphic an accurate clean academic schematic.

Use NAMED INTERFACE PORTS between the four panels, NOT long cross-panel arrows. Exactly:
1. DELETE the horizontal arrow exiting the left "地图位姿 / 定位质量" across the boundary. Keep label under that box "可信位姿 → (b)". The existing center top "可信位姿（来自 a）" is the corresponding input port; it continues downward into coordinate transform.
2. DELETE the long bottom-left "定位健康 → 安全仲裁" arrow crossing into middle. Replace with small stationary text inside left panel below health box "定位健康 → (c) 安全仲裁". Keep the right panel small "定位健康（来自 a）" input with ONE short right-pointing arrow into safety mux.
3. DELETE BOTH blue horizontal arrows from central model/model-output to right panel, and delete any blue vertical line in their column boundary. Currently one points at arrival and another at terrain: both are WRONG. Instead add small output label INSIDE center panel beneath "局部轨迹 + STOP" box: "输出至 (c) 轨迹跟踪". At right tracking box, add small blue text just above it "局部轨迹 + STOP（来自 b）", with a short DOWN arrow into tracking.
4. At RIGHT TOP, delete every old connecting line between task manager, tracking and complete-confirm box. Task manager must NOT output goals into tracking. Just keep top task manager box and completion box. One LEFT-pointing arrow from "完成确认 → 下发下一站" small box into "任务管理：31个必经点 / 30段任务" is correct. Under task manager add static caption "下一个世界目标点 → (b)" with NO down arrow or line into tracking.
5. Keep vertical execution chain tracking → safety → S10 → 到点确认. Do not draw arrival to terrain arrow. The destination below is merely terrain illustrations.
6. DELETE the bottom dashed data-training arrow that currently points at the model OUTPUT. Use a static caption underneath training pipeline last box instead "训练模型 → (b)". A named port is clearer than an incorrect arrow. Remove "数据与策略优化" floating label where the wrong dashed arrow was. Keep bottom pipeline horizontal arrows.
7. All other within-panel downward arrows, coordinate equation, input groups, model→prediction arrow remain unchanged.

Ensure no leftover dangling cross-panel arrows. This edit corrects connection semantics ONLY. No new content, model brands, frame counts, disclaimers, ornaments or performance claims.

## Final Label Correction

Make exactly ONE text replacement in this approved white academic architecture figure. In panel (c), the wide rectangular control box directly above the S10 robot currently says "轨迹跟踪与避障". Replace that label with exactly "轨迹跟踪 · 避障 · 安全仲裁", using a slightly smaller font if needed so the line fits. This combined module receives both VLN trajectories and localization health. Preserve every other pixel, layout, color, label, arrow, photo, title and illustration unchanged. In particular keep four-wheel S10, VLN 模型, 多帧历史观测, Goal Point + 语义输入, three-view or single-view input. No other additions or removals.
