# Editing 模块

## 何时读取

当用户需要剪辑合成、音视频对齐、音频拼接、字幕后合成、加 BGM，或需要使用 `scripts/` 下的视频处理脚本时读取。

## 前置依赖

- 本机可运行 `ffmpeg` 和 `ffprobe`。
- Python 版本支持脚本类型标注，建议 Python 3.10+。
- 执行前先检查每个脚本顶部“配置区”，确认输入目录、输出目录、文件名前缀和音量参数符合当前项目。

检查命令：

```bash
ffmpeg -version
ffprobe -version
python --version
```

## 脚本入口

| 需求 | 脚本 | 默认输入 | 默认输出 |
|---|---|---|---|
| 拼接多段配音 | `scripts/merge_audio.py` | `materials/audio*.mp3` | `merge.mp3` |
| 按音频时长调整视频速度 | `scripts/match_video_speed_to_audio.py` | `materials/MP4/videoN.*` + `materials/MP3/audioN.*` | `materials/video_output/videoN.mp4` |
| 合成并拼接编号视频和音频 | `scripts/merge_video_audio_segments.py` | `materials/video_output/videoN.*` + `materials/MP3/audioN.*` | `materials/output/final_video.mp4` |
| 给成片添加 BGM | `scripts/add_bgm_to_video.py` | `final_with_subtitle.mp4` + `materials/bgm.mp3` | `final_with_bgm.mp4` |

## 推荐流程

1. 将镜头视频按编号放入 `materials/MP4/video1.mp4`、`video2.mp4`。
2. 将对应配音按编号放入 `materials/MP3/audio1.mp3`、`audio2.mp3`。
3. 如需要先让每段视频匹配配音时长：

```bash
python scripts/match_video_speed_to_audio.py
```

4. 合成每段视频 + 对应音频，并拼接最终视频：

```bash
python scripts/merge_video_audio_segments.py
```

5. 如需要完整配音文件用于字幕识别，可拼接音频：

```bash
python scripts/merge_audio.py
```

6. 字幕生成和烧录见 `references/SUBTITLES.md`。
7. 如需要加 BGM，在字幕视频完成后运行：

```bash
python scripts/add_bgm_to_video.py
```

## 使用规则

- 编号文件必须成对出现，例如 `video1.mp4` 对应 `audio1.mp3`。
- 脚本会报告缺失编号；缺失时不要假装已完成，应让用户补齐或调整配置。
- 若项目目录不是脚本默认目录，先修改脚本顶部配置区，或把素材整理成默认目录结构。
- `match_video_speed_to_audio.py` 使用 `setpts` 变速；变速过大时应提醒画面可能明显变快或变慢。
- `merge_video_audio_segments.py` 会统一分辨率、帧率、编码和音频采样参数，适合作为最终拼接前的规范化步骤。
- `add_bgm_to_video.py` 默认保留原视频声音并混入循环 BGM，BGM 音量建议保持在 0.12 到 0.25。

## 完成标准

- 目标视频文件存在且可播放。
- 音画同步，无明显截断、黑屏或尾部异常静音。
- `asset-manifest.md` 或 `edit-guide.md` 记录最终视频、字幕视频和 BGM 版本路径。
