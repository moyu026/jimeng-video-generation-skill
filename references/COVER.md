# Cover 模块

## 目标

根据 `shot-list.md` 的封面 Prompt 生成 16:9 封面图，并把它制作成视频第 0 段。

## 输出

```text
assets/covers/cover-16x9.png
materials/MP4/S00.mp4
```

## 工作步骤

1. 从 `shot-list.md` 读取封面目标、产品 / 技术名称、主体构图、风格、色彩和禁止内容。
2. 生成 16:9 封面图并让用户检查；不需要的内容不要扩展为多尺寸封面工作流。
3. 用户确认封面后，使用 `audio0.mp3` 的时长生成循环帧视频：

```bash
python scripts/create_cover_video.py --image assets/covers/cover-16x9.png --audio materials/MP3/audio0.mp3 --output materials/MP4/S00.mp4
```

4. 检查 `S00.mp4` 分辨率、可播放性和时长。

## 规则

- `S00` 是正式时间线第 0 段，不是时间线外缩略图。
- `narration.md` 必须有 S00 封面配音，文件为 `audio0.mp3`。
- 不添加后期图文包装；封面需要的视觉信息应在确认后的封面图中完成。
- 禁止错误文字、第三方 Logo、水印和真实人物。
