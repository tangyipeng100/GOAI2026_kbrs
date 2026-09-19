# 导航方案影片 v2

输出为 1920 × 1080、24 fps、64 秒，H.264 / AAC。配音为中文合成语音，配乐为脚本生成的原创轻节拍。

## 分镜

| 时间 | 内容 |
| --- | --- |
| 0–7 秒 | 用户提供的赛场俯视图，轻微推近，赛事与队伍信息 |
| 7–10 秒 | 用户提供的山猫 S10 轮足机器人产品图片 |
| 10–13 秒 | 完整导航框架图 |
| 13–17 秒 | 在完整框架图中突出高保真高斯仿真与训练 |
| 17–21 秒 | 突出可信定位与局部目标转换 |
| 21–27 秒 | 突出 VLN、三视图或单视图、多帧观测及语义输入 |
| 27–32 秒 | 突出安全执行与逐站到点确认 |
| 32–38 秒 | epoch2 route02：阶梯路段，全部原始帧与结束帧 |
| 38–47 秒 | epoch2 route12：绕石路段，全部原始帧与结束帧 |
| 47–54 秒 | epoch2 route25：穿草路段，全部原始帧与结束帧 |
| 54–60 秒 | 30 个独立仿真 episode 的结果与严格阈值 |
| 60–64 秒 | 队伍与方案收束 |

## 文件

- `public/media/goai_yungu_vln_overview_v2_64s.mp4`：完整配音配乐版。
- `public/media/goai_yungu_vln_overview_v2_clean.mp4`：相同画面的无音轨版。
- `public/media/goai_yungu_vln_overview_v2_teaser_15s.mp4`：仅赛场俯视镜头的首屏循环版，不含会被背景布局遮挡的技术图或推理界面。
- `public/media/goai_yungu_vln_overview_v2.zh.vtt`：中文讲解字幕。
- `public/media/goai_yungu_vln_overview_v2_poster.jpg`：影片封面。

旧版影片文件保留，但页面不再引用。

高清母版位于本地忽略目录 `assets-private/film-v2/masters/`。网页播放版保持相同的 1080p 构图与内容，通过限定编码码率控制在预览托管的单文件 25 MiB 上限内。

## 构图与证据

原始回放为 1920 × 852 的前视画面和俯视轨迹，新版原尺寸放置于 `(0, 96)`，不裁切、不拉伸、不以循环补时。标题与说明放在视频区域之外。保留模型原始结束帧与指标。回放中的 5 fps 为素材记录帧率，不宣称是实际运行速度。

片头使用用户提供的两张静态俯视图进行镜头动画，不冒充实机航拍视频。产品图片只介绍平台；模型推理持续标注为仿真，三个片段分别初始化，不表示一次连续实机运行。

## 复现

使用 Python、Pillow、NumPy、imageio-ffmpeg 和 edge-tts。语音生成使用 [edge-tts](https://github.com/rany2/edge-tts) 的 `zh-CN-YunxiNeural`；支持从 `HTTPS_PROXY` 或 `HTTP_PROXY` 读取当前会话代理，不把机器私有配置写入公开源码。

```powershell
python scripts/render_overview_film_v2.py --project-root . --video-tools <依赖目录> --aerial1 <俯视图1.png> --aerial2 <俯视图2.png> --robot <S10产品图.png>
python scripts/test_film_v2.py
python scripts/verify_overview_film_v2.py --project-root . --video-tools <依赖目录>
```

验收产物保存在本地忽略目录 `assets-private/film-v2/qa/`：分镜接触表、编码后帧、原始帧完整性与 PSNR、音轨检查、桌面和手机页面截图。

本地预览使用 README 中的双端口入口。Wrangler 本地静态媒体响应未提供正确的 Range 行为，`scripts/preview-media.mjs` 为公开媒体提供 HTTP 206，保证播放器拖动进度不会回到开头。可用 `node --test scripts/test_preview_media.mjs` 验证范围请求与路径边界；浏览器验收还会实际播放、跳至 42 秒并检查桌面和手机布局。
