# Jimeng Video Generation Skill

把技术材料编排为带配音、BGM 和字幕的即梦 / AI 技术解读视频。

核心流程：

```text
环境检查 → 规划三文件 → 用户确认 narration/shot-list → 用户生成 audioN
→ S00 封面循环帧 + 主体视频 + 用户 outro → 素材检查 → 变速
→ 旁白与 BGM 合成 → Whisper → narration 校验 → 字幕烧录
```

固定命名：

- 视频：`materials/MP4/S00.mp4...SNN.mp4`
- 配音：`materials/MP3/audio0.mp3...audioN.mp3`
- BGM：`materials/MP3/bgm.mp3`
- 变速视频：`materials/video_output/S00.mp4...SNN.mp4`
- 成片：`materials/output/final_video_subtitled.mp4`

`S00` 是封面图循环帧，最后一个视频是用户提供的 outro。流程不制作后期图文包装，只在最后烧录已按 narration 校验的字幕。

初始化项目：

```bash
python scripts/scaffold_project.py output/my-video
```

详细行为以 `SKILL.md` 和 `references/` 为准。
