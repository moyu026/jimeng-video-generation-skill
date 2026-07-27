# Cover 模块

## 目标

根据 `shot-list.md` 中已确认的画面方向，生成横屏 `16:9` 或竖屏 `6:7` 封面图，并把它制作成视频第 0 段。

## 输出

```text
assets/covers/cover.png
materials/MP4/S00.mp4
```

## 工作步骤

1. 从 `shot-list.md` 读取封面目标、产品 / 技术名称、主体构图、风格、色彩和禁止内容。
2. 只生成用户已确认方向的封面图并让用户检查；不要同时生成横竖屏两套封面。
3. 用户确认封面后，使用 `audio0.mp3` 的时长生成循环帧视频：

```bash
python scripts/create_cover_video.py --image assets/covers/cover.png --audio materials/MP3/audio0.mp3 --output materials/MP4/S00.mp4 --orientation <landscape|portrait>
```

4. 检查 `S00.mp4` 是否为横屏 `1920×1080` 或竖屏 `1080×1260`，并检查可播放性和时长。

## 规则

- `S00` 是正式时间线第 0 段，不是时间线外缩略图。
- `narration.md` 必须有 S00 封面配音，文件为 `audio0.mp3`。
- 不添加后期图文包装；封面需要的视觉信息应在确认后的封面图中完成。
- 禁止错误文字、第三方 Logo、水印和真实人物。
