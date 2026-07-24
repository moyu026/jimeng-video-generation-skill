# Test Prompts

## 1. 完整规划

Prompt：根据这份技术发布稿生成视频规划。

期望：

- 先检查环境。
- 生成 video-plan.md、narration.md、shot-list.md。
- S00 是封面循环帧，narration 有封面配音，shot-list 有封面 Prompt。
- 最后一个 Shot 是用户 outro，包含固定文案。
- 在用户检查 narration 和 shot-list 前停止。

## 2. 用户要求修改规划

Prompt：把 S02 的配音缩短，并把画面改成更直观的数据流。

期望：

- 同步修改 narration 和 shot-list。
- 重跑配音一致性检查。
- 不修改不相关镜头。

## 3. 用户确认无需修改

Prompt：内容没问题，继续。

期望：

- 不重写规划文件。
- 请用户按 audio0...audioN 生成 MP3，并提供 bgm.mp3。

## 4. 素材缺失

Prompt：素材都在目录里，开始变速。

期望：

- 先运行 check_media_inventory.py。
- 任一 SNN、audioN、bgm.mp3 或最后 outro 缺失时停止。

## 5. 视频生成

Prompt：根据 shot-list 生成所有视频。

期望：

- S00 由封面图循环帧生成。
- 主体镜头优先使用即梦，只为中间 jimeng-video 镜头调用即梦。
- 每个即梦原始视频生成 6–8 秒，最终按对应 audioN 变速。
- HTML 仅在用户提供架构图 / 流程图且即梦无法清楚表达时使用，整条视频最多 3 个。
- 成片总时长以 audio0...audioN 总时长为准。
- 最后 outro 要求用户提供。
- 不制作后期图文包装。

## 6. 合成与字幕

Prompt：素材齐了，完成成片和字幕。

期望：

- 变速输出到 materials/video_output/SNN.mp4。
- 生成 final_voice.mp4、final_video.mp4、narration.mp3。
- Whisper 使用无 BGM 的 narration.mp3。
- 字幕按 narration 校验，固定 outro 文案准确。
- 输出 final_video_subtitled.mp4。

## 7. HTML 动画录屏

Prompt：这个 HTML 已经审核通过，请录制成视频。

期望：

- 先确认用户提供了架构图 / 流程图、即梦无法清楚表达，且本片 HTML 录屏总数不超过 3 个。
- 检查底部 18% 字幕安全区没有关键内容。
- 从 `data-animation-duration` 读取动画时长。
- 只使用 `scripts/record_html_with_ffmpeg.py`，Chrome kiosk 全屏录制。
- 实际录屏时长等于动画时长加 1 秒。
- 回看确认最后 1 秒为稳定终态。
