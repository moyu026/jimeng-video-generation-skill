# HTML Recording 模块

## 何时读取

当 HTML 动态图解已经生成，并且已经通过人工验证，用户要求把它录制成视频素材时读取。

本模块只负责：

```text
已验证 HTML 动态图解
→ Chrome / Edge 以 record 模式打开
→ ffmpeg 录制为视频素材
→ 写入 asset-manifest.md / edit-guide.md
```

硬前置条件：对应 HTML 必须已经完成人工验证，并记录 `HTML Review: approved`。没有人工确认前，不进入录屏。

## 输入

- `assets/html/<diagram-id>.html`
- `HTML Review: approved` 的人工验证结论。
- `shot-list.md` 中对应镜头的录屏时长、动画顺序、配音节奏和后期建议。
- 目标分辨率，默认 16:9 / 1920×1080。
- 录屏工具：默认优先 Chrome / Edge + ffmpeg `gdigrab` 半自动录屏；OBS / 系统录屏作为人工兜底。
- 前置依赖：`ffmpeg` 必须可用；如需要探测时先执行 `ffmpeg -version`。

## 输出

```text
assets/recordings/<diagram-id>.mp4
asset-manifest.md 更新项
edit-guide.md 更新项（如需要）
```

## 录屏方案选择

### V1 默认方案：Chrome / Edge + ffmpeg 半自动录屏（当前推荐）

当前 Skill 默认优先使用浏览器 + ffmpeg 方案，因为后续音频拼接、变速对齐、字幕烧录和合成都已经依赖 ffmpeg，复用同一套本机工具链最轻量。

推荐流程：

```text
已验证 HTML → Chrome / Edge 打开 ?record=1 → 人工确认画面
→ ffmpeg gdigrab 录制桌面 / 指定区域 → 输出 mp4
```

优点：

- 与后续音频 / 剪辑流程共用 ffmpeg，减少工具栈。
- 不强依赖 OBS。
- 可脚本化，输出路径和时长可控。
- 保留人工确认步骤，避免 DPI、窗口焦点、浏览器缩放导致录错画面。

推荐脚本：

```bash
python scripts/record_html_with_ffmpeg.py assets/html/<diagram-id>.html --duration 8
```

脚本默认输出：

```text
assets/recordings/<diagram-id>.mp4
```

脚本行为：

1. 自动用 Chrome / Edge 打开 `assets/html/<diagram-id>.html?record=1`。
2. 等待人工确认浏览器窗口 / 全屏 / 画面构图。
3. 用户按 Enter 后启动 ffmpeg。
4. 用户立即在浏览器中按 `R`，让动画从头重播。
5. ffmpeg 录制指定秒数后自动停止。
6. 输出 H.264 MP4。

> 注意：`?record=1` 只是让页面进入录屏准备状态，隐藏鼠标和 Replay 控制项；真正录制由 ffmpeg 完成。

### V1 兜底：人工 OBS / 系统录屏

如果 ffmpeg `gdigrab` 在当前机器上失败，或录屏区域 / DPI 难以稳定控制，可以退回人工 OBS / 系统录屏。

OBS 仍适合稳定批量人工录制，但不是当前默认依赖。

### V2 后续增强：Playwright + ffmpeg 自动录屏

当 HTML 模板、字体、动画时长和输出目录稳定后，可以再引入更自动化方案：

```text
Playwright 打开 HTML → 设置 viewport 1920×1080 → 触发 R / 自动 replay → ffmpeg 录制 → 输出 mp4
```

该方案优点是可复现、适合批量；缺点是依赖更多，且 Windows 窗口捕获、DPI 缩放和浏览器焦点仍需要调试。

### V3 不推荐作为默认：HTML 内置 MediaRecorder

HTML 自带录制逻辑看似方便，但 DOM/CSS 页面没有稳定通用的浏览器原生“录制当前页面为 mp4”能力。`getDisplayMedia()` 也需要用户手动授权，不能静默录屏。因此不作为默认路径。

## ffmpeg 半自动录屏标准流程

1. **确认前置状态**：检查对应 HTML 已记录 `HTML Review: approved`。
2. **执行脚本**：

   ```bash
   python scripts/record_html_with_ffmpeg.py assets/html/<diagram-id>.html --duration <秒数>
   ```

3. **进入录制模式**：脚本会用 Chrome / Edge 打开 `?record=1` 页面。录制模式应隐藏鼠标和 Replay 控制项。
4. **人工确认画面**：确认浏览器窗口 / 全屏状态、16:9 stage、缩放比例和构图都正确。
5. **启动录制**：回到命令行按 Enter，ffmpeg 开始录制。
6. **重播动画**：录制开始后立刻在浏览器中按 `R`，避免录到页面加载过程。
7. **完整播放**：录到动画终态，并让终态停留 1–2 秒，方便剪辑衔接和配音对齐。
8. **自动停止录屏**：ffmpeg 到达指定时长后自动保存为：

   ```text
   assets/recordings/<diagram-id>.mp4
   ```

9. **回看检查**：播放录屏文件，确认无地址栏、无鼠标、无控制按钮、无裁切、动画完整。
10. **更新清单**：把输出路径、时长、分辨率、状态写入 `asset-manifest.md`；需要剪辑注意事项时写入 `edit-guide.md`。

## 脚本用法

基础用法：

```bash
python scripts/record_html_with_ffmpeg.py assets/html/memory-turbo-grid.html --duration 8
```

指定输出路径：

```bash
python scripts/record_html_with_ffmpeg.py assets/html/memory-turbo-grid.html \
  --duration 8 \
  --output assets/recordings/memory-turbo-grid.mp4
```

录制指定区域，例如 1920×1080：

```bash
python scripts/record_html_with_ffmpeg.py assets/html/memory-turbo-grid.html \
  --duration 8 \
  --offset-x 0 --offset-y 0 --width 1920 --height 1080
```

如果浏览器已经手动打开并全屏，只让脚本录当前屏幕：

```bash
python scripts/record_html_with_ffmpeg.py assets/html/memory-turbo-grid.html \
  --duration 8 \
  --skip-browser
```

## 录屏参数建议

- 分辨率：1920×1080。
- 帧率：30fps 默认；动画速度快或有细线移动时可用 60fps。
- 编码：H.264 MP4，便于剪辑软件兼容。
- 音频：默认不录系统声音；配音和 BGM 在后期合成。
- 色彩：使用浏览器默认色彩管理即可。
- 采集方式：Windows 默认使用 ffmpeg `gdigrab`；必要时可录制整个 desktop，再在后期裁剪。
- 文件命名：与 HTML `diagram-id` 保持一致，例如：

```text
assets/html/memory-turbo-grid.html
assets/recordings/memory-turbo-grid.mp4
```

## 录屏前检查清单

录制前必须检查：

- HTML Review 是否为 `approved`。
- 页面是否 16:9 居中显示。
- 地址栏、书签栏、标签栏是否隐藏，或浏览器是否以 app / kiosk 风格打开。
- `?record=1` 是否隐藏鼠标和 Replay 控制项。
- 按 `R` 是否能从初始状态重播动画。
- 动画总时长是否接近 `shot-list.md` 中规划的录屏时长。
- 终态是否有 1–2 秒停留。
- ffmpeg 命令行窗口是否不会遮挡录制区域。

## 录屏后检查清单

录制后必须回看输出视频：

- 是否从动画初始状态开始，而不是从中途开始。
- 是否完整录到终态。
- 是否有浏览器 UI、鼠标、Replay 按钮、命令行窗口或其他浮层。
- 是否有边缘裁切、黑边异常、缩放模糊。
- 文字是否在视频中仍然清晰可读。
- 箭头、连线、扫光、高亮是否与 HTML 中一致。
- 时长是否适合对应分镜；如差异较大，需要在 `shot-list.md` 或剪辑说明中标注。

## asset-manifest.md 更新格式

建议写入：

```markdown
| Asset ID | Type | Source | Path | Status | Duration | Notes |
|---|---|---|---|---|---:|---|
| rec-<diagram-id> | HTML recording | assets/html/<diagram-id>.html | assets/recordings/<diagram-id>.mp4 | done | <秒数> | ffmpeg gdigrab, 1920×1080, 30fps, HTML Review approved |
```

## edit-guide.md 更新格式

如果该录屏需要和配音 / 后期标注对齐，写入：

```markdown
- Shot ID: S04
- Video: assets/recordings/<diagram-id>.mp4
- Use: 从 00:00 开始使用完整动画；终态可根据配音延长 0.5–1s
- Overlay: 后期标题 / 框选 / 箭头 / 局部放大说明
- Notes: 不使用录屏原声；必要时裁掉开头 0.2s 空白
```

## 完成标准

- 录屏前已确认 `HTML Review: approved`。
- 使用 Chrome / Edge 打开 `?record=1` 页面。
- 使用 ffmpeg 录制并输出 H.264 MP4。
- 录屏没有浏览器地址栏、鼠标、控制按钮、命令行窗口或录屏工具浮层干扰。
- 画面完整，没有边缘裁切或异常黑边。
- 动画从初始状态完整播放到终态。
- 终态有足够停留，便于剪辑。
- 输出文件路径为 `assets/recordings/<diagram-id>.mp4`。
- 文件路径、时长、分辨率和状态写入 `asset-manifest.md`。

## 失败 / 退化路径

- HTML 未人工验证：停止录屏，回到 HTML Diagram 模块执行 `Checkpoint HTML Review`。
- ffmpeg 不可用：先安装或修复 ffmpeg；如果只是少量素材，可退回人工 OBS / 系统录屏。
- 录屏画面裁切：调整浏览器全屏、ffmpeg `gdigrab` 区域参数或 HTML stage。
- Replay 按钮被录进去：确认使用 `?record=1` 后重新录制。
- 动画从中途开始：先启动 ffmpeg 录屏，再按 `R` 重播。
- 动画过快 / 过慢：回到 HTML Diagram 模块调整动画时长，再重新人工验证和录屏。
- 文字录屏后不清晰：提高录屏分辨率、调整字体大小或模块布局，再重新验证。
- ffmpeg 录屏失败：检查 `ffmpeg -version`、`gdigrab` 支持、浏览器窗口和录制区域；仍失败则退回人工 OBS / 系统录屏，不阻塞项目交付。

## 自检清单

- [ ] HTML 是否已经人工验证通过？
- [ ] 是否 16:9 / 1920×1080？
- [ ] 是否用 Chrome / Edge 打开 `?record=1`？
- [ ] 是否无地址栏、鼠标、控制项遮挡？
- [ ] 是否先启动 ffmpeg 录屏再按 R 重播？
- [ ] 是否完整录到动画和终态停留？
- [ ] 是否回看确认视频无裁切、无命令行浮层、无异常黑边？
- [ ] 是否更新 asset-manifest.md？
- [ ] 是否把剪辑注意事项写入 edit-guide.md（如需要）？
