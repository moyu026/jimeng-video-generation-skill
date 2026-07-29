# Cover 模块

## 目标

生成视频封面分两步：先用即梦 CLI（命令名 `dreamina`）的图片生成功能生成无字主视觉背景图，再用 `scripts/create_cover_with_text.py` 准确叠加标题、产品 / 技术名称、Logo 和标签等文字内容，最后把它制作成视频第 0 段。调用 `dreamina` 生成背景图前必须先向用户说明 Prompt、输出路径和固定参数并取得确认。

## 两步生成原则

- 第一步：`dreamina` 只负责无字主视觉背景，禁止在 Prompt 中要求生成标题、产品名、Logo 或任何可读文字。
- 第二步：文字和 Logo 由 `scripts/create_cover_with_text.py` 用 Pillow 本地绘制，保证中文、英文技术名和 Logo 准确，不让模型凭空生成或重画。
- 没有通过用户检查前，不生成最终带字封面，也不继续生成视频号尺寸变体。

## 输出

```text
assets/covers/cover-bg-16x9.png      # 无字主视觉背景
assets/covers/cover-16x9.png         # 叠加文字后的主封面
materials/MP4/S00.mp4
```

## 工作步骤

1. 运行 `python scripts/check_environment.py --require-jimeng`；即梦 CLI 缺失或认证失败时先配置并复检，仍不可用则停止。
2. 从 `shot-list.md` 读取封面目标、产品 / 技术名称、主体构图、风格、色彩和禁止内容。
3. 运行 `dreamina --help` 及图片生成子命令帮助，确认实际子命令和参数；不要编造 CLI 子命令，也不要静默改用其他图片工具。
4. 向用户说明封面背景 Prompt、输出路径 `assets/covers/cover-bg-16x9.png` 和固定参数，取得用户确认后调用 `dreamina` 图片生成功能，只生成用户已确认方向的无字主视觉背景，保存为 `assets/covers/cover-bg-16x9.png`。Prompt 必须禁止生成任何可读文字、Logo、品牌标识或真实人物。
5. 使用 `scripts/create_cover_with_text.py` 把标题、产品 / 技术名称、Logo、标签等准确叠加到背景图上：

```bash
python scripts/create_cover_with_text.py \
  --background assets/covers/cover-bg-16x9.png \
  --logo assets/original/openJiuwen-logo.png \
  --brand openJiuwen \
  --badge "<技术标签>" \
  --title-line1 "<主标题>" \
  --title-line2 "<副标题>" \
  --subtitle "<产品 / 技术名称 + 一句话定义>" \
  --footer "<页脚>" \
  --theme dark \
  --out-dir assets/covers
```

6. 让用户检查 `assets/covers/cover-16x9.png`；需要修改时判断问题来源：主视觉问题调整 Prompt / 背景图并重新请求确认后调用 `dreamina`；文字、Logo、标题层级问题调整 `create_cover_with_text.py` 参数。修复后再次请用户检查，不需要修改时保持结果不变。
7. 用户确认封面后，使用 `audio0.mp3` 的时长生成循环帧视频：

```bash
python scripts/create_cover_video.py --image assets/covers/cover-16x9.png --audio materials/MP3/audio0.mp3 --output materials/MP4/S00.mp4 --orientation <landscape|portrait>
```

8. 检查 `S00.mp4` 是否为横屏 `1920×1080` 或竖屏 `1080×1260`，并检查可播放性和时长。

## 规则

- `S00` 是正式时间线第 0 段，不是时间线外缩略图。
- 封面背景图来源必须是 `dreamina` 图片生成；可读文字和 Logo 必须由 `create_cover_with_text.py` 后期叠加。
- `narration.md` 必须有 S00 封面配音，文件为 `audio0.mp3`。
- 不添加后期图文包装；封面需要的视觉信息应在确认后的封面图中完成。
- 禁止错误文字、第三方 Logo、水印和真实人物。
