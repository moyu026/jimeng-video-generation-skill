# Jimeng CLI 模块

## CLI 命令

即梦 CLI 的实际命令名是 `dreamina`。所有图片生成和视频生成都通过 `dreamina` 调用；不要使用 `jimeng` 或其他命令名。当前 CLI 的子命令或参数不明确时先查看 `dreamina --help` 或对应子命令的帮助，不编造命令。

## 固定生成参数

- 视频分辨率：`720p`。
- 视频生成模型：`seedance2.0 vip`。
- 图片生成按用户已确认的画面方向（横屏 `16:9` 或竖屏 `6:7`）指定比例。

## 用户确认要求

在调用 `dreamina` 生成任何图片或视频前，必须先向用户说明即将执行的命令、目标 Prompt、输出路径和固定参数（分辨率、模型），并等待用户确认后再执行。不得未经确认直接调用 `dreamina` 生成图片或视频。用户要求修改时调整后重新请求确认。

## 输入

读取用户确认后的 `shot-list.md`，处理 `S00` 封面图片和素材类型为 `jimeng-video` 的 `S01...` 主体镜头。不要生成最后的用户 outro。

## 工作步骤

1. 运行 `python scripts/check_environment.py --require-jimeng`。
2. 运行 `dreamina --help` 及相关子命令帮助，确认图片生成和视频生成的实际子命令、参数及可用模型；不要编造命令。
3. 向用户说明封面背景 Prompt、输出路径 `assets/covers/cover-bg-16x9.png` 和固定参数，取得用户确认后，使用 `dreamina` 图片生成功能生成无字主视觉背景，比例必须与用户选择一致。`dreamina` 只生成无字背景，禁止在 Prompt 中要求生成标题、产品名、Logo 或任何可读文字；文字和 Logo 由 `scripts/create_cover_with_text.py` 后期叠加。再让用户检查生成结果。
4. 检查每个主体视频 Prompt 是否写明用户确认的横屏 `16:9` 或竖屏 `6:7`，原始生成时长是否为 6–8 秒，并包含逐 1–2 秒时间轴、镜头运动、结尾状态、风格和禁止内容。
5. 对每个主体镜头，向用户说明即将执行的 `dreamina` 命令、Prompt、固定参数（`720p`、`seedance2.0 vip`）和输出路径，取得用户确认后，使用视频生成功能生成主体镜头，将结果保存为 `materials/MP4/<Shot ID>.mp4`，例如 `S01.mp4`。
6. 认证或环境缺失时先配置并复检；失败时记录原因并重试，不要切换工具或用占位空文件冒充成功结果。
7. 不添加后期图文包装，不生成可读文字、字幕、Logo 或真实代码。

## 完成标准

- `assets/covers/cover-bg-16x9.png` 由 `dreamina` 的图片生成功能生成，为无字主视觉背景，比例正确且已通过用户检查；最终带字封面 `assets/covers/cover-16x9.png` 由 `create_cover_with_text.py` 叠加文字 / Logo 生成。
- 所有 `jimeng-video` 镜头均有同 Shot ID 视频文件，比例与用户选择一致，原始生成时长均为 6–8 秒，分辨率均为 `720p`，模型均为 `seedance2.0 vip`。
- 每次调用 `dreamina` 生成图片或视频前都已取得用户确认。
- 即梦原始视频时长不决定成片时长；后续按对应 audioN 变速。
- `S00` 由已确认的即梦封面图和封面脚本生成，最后一个 outro 由用户提供。
- 输出可被素材完整性检查识别。
