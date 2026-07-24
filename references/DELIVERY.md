# Delivery 模块

`asset-manifest.md` 必须随生产过程增量更新，不要等到交付阶段集中补写：

- 初始化时按 Shot 建立记录。
- 音频、outro 或原视频到位后更新路径、来源和状态。
- 变速视频、合成视频、SRT、字幕成片生成后更新对应路径和状态。
- 状态只使用 `planned`、`waiting-user`、`ready`；Notes 只写必要说明。

## 输入

- `video-plan.md`、`narration.md`、`shot-list.md`
- `materials/MP4/S00...SNN`
- `materials/MP3/audio0...audioN` 与 `bgm.mp3`
- `materials/video_output/S00...SNN`
- `materials/output/final_voice.mp4`
- `materials/output/final_video.mp4`
- `materials/output/final_video_subtitled.mp4`
- `subtitles/subtitles.srt`

## 工作步骤

1. 复核 `asset-manifest.md` 中每个 Shot 的原视频、音频、变速视频和状态。
2. 确认 `S00` 为封面循环帧，最后一个 Shot 为用户提供的 outro。
3. 确认 BGM、无 BGM 旁白、无字幕成片、SRT 和字幕成片均已登记。
4. 在 `edit-guide.md` 记录实际拼接顺序、分辨率、帧率、字幕样式和最终文件路径。
5. 不写后期图文包装说明。

## 完成标准

- 素材编号连续且一一对应。
- 环境、素材、配音、字幕校验均有通过状态。
- 最终交付文件存在且可播放。
- `asset-manifest.md` 和 `edit-guide.md` 足以复现合成顺序。
