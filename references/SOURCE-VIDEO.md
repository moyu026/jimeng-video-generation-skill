# Source Video 模块

## 适用场景

当某个镜头的素材类型为 `source-video`，且用户提供的原始素材视频是**横屏**，而已确认的画面方向是竖屏 `6:7`（或需要把横屏素材嵌入品牌化竖屏画面）时，使用本模块。目的是把横屏素材视频嵌入到一张先生成的背景图里，并叠加 Logo 和基于该镜头配音稿生成的文字内容，输出与已确认画面方向一致的视频。

若素材视频的方向已与已确认画面方向一致，直接按 Shot ID 复制到 `materials/MP4/<Shot ID>.mp4`，不需要本模块。

## 两步生成原则

- 第一步：用 `dreamina` 生成无字背景图，禁止在 Prompt 中要求生成标题、产品名、Logo 或任何可读文字。调用前必须先向用户说明 Prompt、输出路径和固定参数，取得确认后再执行。
- 第二步：用 `scripts/create_branded_video.py` 把横屏素材视频嵌入背景图，并叠加 Logo、标题、副标题、关键词等文字。文字内容根据该镜头在 `narration.md` 中的配音稿生成。

## 输入

- `shot-list.md` 中素材类型为 `source-video` 的镜头，及其横屏原始素材路径（放在 `assets/original/`）。
- 该镜头在 `narration.md` 中对应的配音稿，用于生成标题、副标题和关键词。
- 已确认的画面方向（本模块用于竖屏 `6:7`，即 `1080×1260`）。
- 自有 / 授权 Logo 文件。

## 输出

```text
assets/original/<shot-id>-bg.png        # 无字背景图（可选保留）
materials/MP4/<Shot ID>.mp4             # 嵌入素材后的品牌化视频
asset-manifest.md 更新项
```

## 工作步骤

1. 从 `shot-list.md` 读取该 `source-video` 镜头的原始素材路径，确认素材是横屏；若已是竖屏则直接复制到 `materials/MP4/<Shot ID>.mp4`，不使用本模块。
2. 从 `narration.md` 读取该镜头的配音稿，提炼主标题、副标题和最多 4 个关键词标签。
3. 编写背景图 Prompt，指定生成与已确认画面方向一致的无字背景（竖屏 `1080×1260`），禁止生成任何可读文字、Logo、品牌标识或真实人物。
4. 向用户说明背景 Prompt、输出路径和固定参数，取得确认后调用 `dreamina` 生成无字背景图，保存为 `assets/original/<shot-id>-bg.png`。
5. 使用 `scripts/create_branded_video.py` 把横屏素材嵌入背景图并叠加文字 / Logo：

```bash
python scripts/create_branded_video.py \
  --background assets/original/<shot-id>-bg.png \
  --logo assets/original/openJiuwen-logo.png \
  --video assets/original/<原始素材文件> \
  --output materials/MP4/<Shot ID>.mp4 \
  --title "<主标题，来自配音稿>" \
  --subtitle "<副标题，来自配音稿>" \
  --keywords "<关键词1>" "<关键词2>" "<关键词3>" \
  --theme dark
```

6. 检查输出视频的方向、可播放性和时长；让用户检查嵌入效果和文字是否准确。
7. 需要修改时判断问题来源：背景主视觉问题调整 Prompt 并重新请求确认后调用 `dreamina`；文字 / Logo / 嵌入位置问题调整 `create_branded_video.py` 参数。修复后再次请用户检查。
8. 把路径、来源、状态写入 `asset-manifest.md`。

## 文字内容生成规则

- 主标题（`--title`）：从该镜头配音稿中提炼核心卖点或主题，简短有力。
- 副标题（`--subtitle`）：产品 / 技术名称 + 一句话定义，或配音稿中的关键补充。
- 关键词（`--keywords`）：从配音稿中提取最多 4 个技术关键词或标签。
- 文字必须与该镜头配音稿内容相关，不得照搬其他镜头的文案。

## 完成标准

- 横屏 `source-video` 镜头都有与已确认画面方向一致的视频文件。
- 背景图由 `dreamina` 生成无字主视觉，文字 / Logo 由 `create_branded_video.py` 后期叠加。
- 文字内容基于该镜头配音稿生成。
- 每次调用 `dreamina` 生成背景图前都已取得用户确认。
- 输出可被素材完整性检查识别。
