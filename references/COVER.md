# Cover 模块

## 目标

使用即梦 CLI 的图片生成功能，根据 `shot-list.md` 中已确认的画面方向生成横屏 `16:9` 或竖屏 `6:7` 封面图，并把它制作成视频第 0 段。

## 输出

```text
assets/covers/cover.png
materials/MP4/S00.mp4
```

## 工作步骤

1. 运行 `python scripts/check_environment.py --require-jimeng`；即梦 CLI 缺失或认证失败时先配置并复检，仍不可用则停止。
2. 从 `shot-list.md` 读取封面目标、产品 / 技术名称、主体构图、风格、色彩和禁止内容。
3. 查看当前即梦 CLI 的帮助或实际文档，调用其图片生成功能。只生成用户已确认方向的封面图，保存为 `assets/covers/cover.png`；不要编造 CLI 子命令，也不要静默改用其他图片工具。
4. 让用户检查封面；需要修改时调整 Prompt 并重新调用即梦 CLI，不需要修改时保持结果不变。
5. 用户确认封面后，使用 `audio0.mp3` 的时长生成循环帧视频：

```bash
python scripts/create_cover_video.py --image assets/covers/cover.png --audio materials/MP3/audio0.mp3 --output materials/MP4/S00.mp4 --orientation <landscape|portrait>
```

6. 检查 `S00.mp4` 是否为横屏 `1920×1080` 或竖屏 `1080×1260`，并检查可播放性和时长。

## 规则

- `S00` 是正式时间线第 0 段，不是时间线外缩略图。
- 封面图片来源必须是即梦 CLI 图片生成。
- `narration.md` 必须有 S00 封面配音，文件为 `audio0.mp3`。
- 不添加后期图文包装；封面需要的视觉信息应在确认后的封面图中完成。
- 禁止错误文字、第三方 Logo、水印和真实人物。
