# Test Prompts

用于轻量验证 `jimeng-video-generation` 的路由和行为。

## 1. 只生成规划

Prompt：请基于 inputs/xxx 生成即梦视频脚本和配音稿，不要生成 SRT。

期望：
- 只进入 Planning。
- 产出 `video-plan.md`、`narration.md`、`shot-list.md`。
- 不生成 `subtitles.srt`。
- 不调用即梦 / 录屏，不生成配音音频。

## 2. 原图处理方式确认

Prompt：请基于这篇文章生成视频，里面有多张架构图。

期望：
- 在最终规划前必须询问：
  1）复用原图 + 生成统一背景图
  2）将原图按原结构重绘为 HTML 动态图解

## 3. HTML 动态图解

Prompt：请把这张架构图按原结构重绘为 HTML。

期望：
- 只读取 `HTML-DIAGRAM.md`。
- 输出 16:9 单 HTML。
- 保留原图结构和文字。
- Replay 默认隐藏，按 R 重播。

## 4. HTML 调试

Prompt：这个 HTML 里箭头挡住文字了，整体底部说明也太低。

期望：
- 不重写整份 HTML。
- 优先局部修改 CSS / 少量 DOM。
- 保持原图结构和动画逻辑。

## 5. 即梦生成

Prompt：请根据 shot-list.md 里的 AI 视频镜头调用即梦 CLI。

期望：
- 读取 `JIMENG-CLI.md`。
- 只处理 AI 视频镜头。
- 生成结果或任务清单写入 `asset-manifest.md`。
- CLI 不存在时不假装成功。

## 6. 音频后字幕

Prompt：请根据用户提供的 merge.mp3 生成 SRT。

期望：
- 读取 `SUBTITLES.md`。
- 不重新生成视频规划。
- 根据用户提供的最终音频和镜头时长生成 `subtitles/subtitles.srt`。

## 7. 完整端到端

Prompt：请基于这个发布稿做完整即梦技术解读视频。

期望：
- 先进入 Planning。
- 生成三份规划文件。
- 到 Checkpoint Plan 停下。
- 用户确认后再进入素材生产。

## 8. Skill 优化

Prompt：把这次 HTML 调试经验沉淀进 Skill。

期望：
- 先给修改计划或草案。
- 用户确认后再修改 Skill 文件。


## 9. HTML Recording / ffmpeg

Prompt：这个 HTML 已经人工验证通过，请用 ffmpeg 录屏。

期望：
- 读取 `references/HTML-RECORDING.md`。
- 确认 `HTML Review: approved`。
- 优先使用 Chrome / Edge + ffmpeg `gdigrab` 或 `scripts/record_html_with_ffmpeg.py`。
- 输出到 `assets/recordings/<diagram-id>.mp4`。
- 更新 `asset-manifest.md`。


## 10. Cover / 视频号封面

Prompt：请根据这篇文章生成视频封面，并输出视频号封面尺寸。

期望：
- 读取 `references/COVER.md`。
- 先生成 16:9 主封面，突出当前文章产品 / 技术名称。
- 16:9 主封面生成后必须停下，要求人工检查 `Cover Review`。
- 人工确认 `Cover Review: approved` 前，不生成 1080×608 和 1080×1260。
- 视频号尺寸必须基于已确认的 16:9 主封面生成，不重新发散设计。
