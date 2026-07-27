# Editing 模块

## 前置条件

- 环境检查通过。
- `scripts/check_media_inventory.py` 检查通过。
- 原视频位于 `materials/MP4/S00.mp4...SNN.mp4`。
- 音频位于 `materials/MP3/audio0.mp3...audioN.mp3`，并有 `bgm.mp3`。

## 画面尺寸

- 所有 `S00...SNN` 必须与用户确认的方向一致：横屏 16:9（1920×1080）或竖屏 6:7（1080×1260）。
- 合成沿用 S00 的尺寸，不在剪辑阶段改变画面方向。

## 固定流程

### 1. 按音频变速

```bash
python scripts/match_video_speed_to_audio.py
```

输入 `materials/MP4/SNN.*` 与 `materials/MP3/audioN.*`，输出 `materials/video_output/SNN.mp4`。即梦原始视频通常为 6–8 秒，但最终片段时长完全由对应 audioN 决定；允许通过变速对齐。变速比例异常时先回看画面，不盲目接受。

### 2. 合成分段旁白视频

```bash
python scripts/merge_video_audio_segments.py
```

输入变速视频和分段音频，按编号顺序合成为：

```text
materials/output/final_voice.mp4
```

合成前再次要求视频和音频编号集合完全一致，不允许缺项后继续。

### 3. 混入 BGM

```bash
python scripts/add_bgm_to_video.py
```

输入 `final_voice.mp4` 和 `materials/MP3/bgm.mp3`，输出：

```text
materials/output/final_video.mp4
```

BGM 默认循环到视频结束并做淡入淡出；旁白必须清晰可辨。

### 4. 合并无 BGM 旁白

```bash
python scripts/merge_audio.py
```

按 `audio0...audioN` 顺序生成：

```text
materials/output/narration.mp3
```

该文件用于 Whisper，避免 BGM 降低识别准确率。

## 完成标准

- 变速视频目录包含连续的 `S00...SNN`，且每段与对应 audioN 等长。
- 最终视频总时长等于 audio0...audioN 的总时长，允许编码造成轻微误差。
- 最终视频的方向、比例和分辨率与规划一致。
- `final_voice.mp4` 含完整旁白。
- `final_video.mp4` 含完整旁白和 BGM。
- `narration.mp3` 只含按编号拼接的旁白，不含 BGM。
- 不存在后期图文包装版本。
