# Asset Manifest

> 生产过程中随素材生成增量更新。只填写路径、来源、状态和必要备注；状态使用 `planned`、`waiting-user`、`ready`。

| Shot ID | Role | Raw Video | Audio | Speed-matched Video | Source | Status | Notes |
|---|---|---|---|---|---|---|---|
| S00 | cover | materials/MP4/S00.mp4 | materials/MP3/audio0.mp3 | materials/video_output/S00.mp4 | cover still loop | planned | |
| S01 | outro | materials/MP4/S01.mp4 | materials/MP3/audio1.mp3 | materials/video_output/S01.mp4 | user provided | waiting-user | Renumber after adding body shots |

## Final Assets

| Asset | Path | Status | Notes |
|---|---|---|---|
| BGM | materials/MP3/bgm.mp3 | waiting-user | |
| Narration mix | materials/output/narration.mp3 | planned | No BGM; Whisper input |
| Voice video | materials/output/final_voice.mp4 | planned | |
| Final video | materials/output/final_video.mp4 | planned | Voice + BGM |
| SRT | subtitles/subtitles.srt | planned | Validated against narration |
| Subtitled video | materials/output/final_video_subtitled.mp4 | planned | Final delivery |
