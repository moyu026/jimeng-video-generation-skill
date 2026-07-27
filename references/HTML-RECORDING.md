# HTML Recording 模块

## 前置条件

- HTML 已人工验证并记录 `HTML Review: approved`。
- HTML `.stage` 带有 `data-animation-duration="<秒数>"`。
- 页面已预留底部字幕安全区，核心图形和文字不能进入该区域。
- 已确认画面方向：横屏 16:9（1920×1080）或竖屏 6:7（1080×1260）。
- Windows 上的 Chrome、系统 PATH 中的 ffmpeg 和 `scripts/record_html_with_ffmpeg.py` 可用。环境检查必须先保证 `ffmpeg -version` 成功。

## 固定时长规则

```text
录屏时长 = HTML 动画时长 + 1 秒
```

额外的 1 秒用于保留动画终态。不要把 `shot-list.md` 中的录屏时长直接写成动画时长；必须分别登记：

```text
动画时长：8 秒
录屏时长：9 秒
```

## HTML 时长声明

在 `.stage` 上声明动画时长：

```html
<main class="stage" id="stage" data-animation-duration="8">
```

`data-animation-duration` 只表示动画本身的时长，不包含额外 1 秒终态。

## 唯一录屏脚本

统一使用：

```text
E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py
```

从 HTML 自动读取动画时长：

```bash
python E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py assets/html/<diagram-id>.html --orientation <landscape|portrait>
```

临时覆盖动画时长：

```bash
python E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py assets/html/<diagram-id>.html --duration 8 --orientation <landscape|portrait>
```

这里的 `--duration 8` 表示动画时长，脚本实际录制 9 秒。统一使用该脚本完成 HTML 全屏录制。

## 脚本行为

1. 用 Chrome `--kiosk` 全屏打开 HTML 的 `?record=1&orientation=<方向>` 模式。
2. 等待页面完成首次渲染。
3. 横屏录制 1920×1080 全屏；竖屏在 1920×1080 桌面中央录制 926×1080 的近似 6:7 区域，并输出为 1080×1260。
4. 录制启动后自动向 Chrome 发送 `R`，从头播放动画。
5. 按“动画时长 + 1 秒”录制并保留终态。
6. 关闭本次 Chrome 窗口并输出 `assets/recordings/<diagram-id>.mp4`。

## 字幕安全区

- 按所选画面方向布局，底部至少预留 18% 高度作为字幕安全区。
- 标题、节点、箭头、图例、说明文字和关键动画不得进入字幕安全区。
- 普通审核模式显示字幕安全区参考线；`?record=1` 时必须隐藏参考线和提示文字。
- 字幕安全区只为最终字幕留白，不要在 HTML 内绘制字幕。

## 录屏前检查

- HTML Review 为 `approved`。
- Chrome kiosk 全屏后无地址栏、标签栏和任务栏。
- `.stage` 填满所选横屏或竖屏画面。
- `data-animation-duration` 与实际最后一个动画结束时间一致。
- 底部字幕安全区内没有关键内容。
- 按 `R` 可以从初始状态重播。

## 录屏后检查

- 视频时长等于动画时长加 1 秒，允许编码造成不超过 0.1 秒误差。
- 动画从初始状态完整播放到终态。
- 最后约 1 秒保持稳定终态。
- 无浏览器 UI、鼠标、Replay、字幕安全区参考线或其他浮层。
- 底部留白足够容纳最终两行字幕。
- 将动画时长、录屏时长、分辨率和输出路径写入 `asset-manifest.md`。

## 失败处理

- 缺少 `data-animation-duration`：补充属性，或明确传入 `--duration`。
- 底部内容被字幕覆盖：回到 HTML Diagram 模块调整布局后重新人工验证。
- 录屏时长不等于动画时长 + 1：检查命令传入的是动画时长，而不是录屏总时长。
- 无法全屏：检查 Chrome 路径、kiosk 参数和 Windows 缩放比例；录屏桌面要求 1920×1080、100% DPI。
- QSV 编码失败：脚本自动回退 `h264_mf`。

## 完成标准

- 使用 `record_html_with_ffmpeg.py` 全屏录制。
- 录屏时长严格为动画时长 + 1 秒。
- HTML 底部字幕安全区有效。
- 输出比例和分辨率与用户确认的画面方向一致。
- 输出视频通过人工回看并登记到资产清单。
