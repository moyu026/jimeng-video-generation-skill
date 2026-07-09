# HTML Recording 模块

## 何时读取

当 HTML 动态图解已经生成，用户要求把它录制成视频素材时读取。

## 输入

- `assets/html/<diagram-id>.html`
- 目标分辨率，默认 16:9 / 1920×1080
- 录屏工具：OBS、系统录屏、浏览器录制或用户自有工具

## 输出

```text
assets/recordings/<diagram-id>.mp4
asset-manifest.md 更新项
```

## 工作步骤

1. 用浏览器打开 HTML 文件。
2. 浏览器全屏，确保 stage 以 16:9 显示。
3. 鼠标不要放在右下角，避免 Replay 按钮显示。
4. 开始录屏。
5. 按 `R` 重播动画。
6. 等动画播放到终态后停止录屏。
7. 保存到 `assets/recordings/`，并更新 `asset-manifest.md`。

## 完成标准

- 录屏没有浏览器地址栏、鼠标、控制按钮干扰。
- 画面完整，没有边缘裁切。
- 动画从初始状态完整播放到终态。
- 文件路径和时长写入 `asset-manifest.md`。

## 失败 / 退化路径

- 录屏画面裁切：调整浏览器窗口或 HTML stage。
- Replay 按钮被录进去：鼠标移开右下角，重新录制。
- 动画过快 / 过慢：回到 HTML Diagram 模块调整动画时长。

## 自检清单

- [ ] 是否 16:9？
- [ ] 是否无控制项遮挡？
- [ ] 是否完整录到动画？
- [ ] 是否更新 manifest？
