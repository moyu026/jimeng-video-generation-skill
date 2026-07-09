# Subtitles 模块

## 何时读取

当配音音频已生成、用户提供最终音频或最终视频，并确认需要生成 / 校准 SRT 字幕、从音频 / 视频转字幕，或将字幕烧录进视频时读取。

## 输入

- `narration.md`
- `assets/audio/voiceover.mp3`、`merge.mp3`、用户提供的最终音频，或最终视频文件
- 最终镜头时长、剪辑时间线或 `shot-list.md`

## 前置依赖

- `whisper` CLI：由 Python 包 `openai-whisper` 提供，可用 `pip install -r requirements.txt` 安装。
- `ffmpeg` 和 `ffprobe`：系统命令，Whisper 读取音视频和 ffmpeg 烧录字幕都依赖它们。
- 中文字体：烧录中文 SRT 时，`force_style` 中的 `FontName` 必须是本机可用字体。

检查命令：

```bash
whisper --help
ffmpeg -version
ffprobe -version
```

## 输出

```text
subtitles/subtitles.srt
```

可选输出：

```text
final_with_subtitle.mp4
```

## 工作步骤

1. 确认最终音频或最终视频已经存在。
2. 获取音频总时长；必要时使用 ffprobe / 剪辑软件信息。
3. 按 `narration.md` 语义切分字幕，避免单条过长。
4. 根据音频时长和镜头时间线生成 / 校准时间码。
5. 输出标准 SRT。
6. 如用户要求烧录字幕，使用 ffmpeg 输出带字幕视频。
7. 将字幕路径和带字幕视频路径写入 `asset-manifest.md` 或 `edit-guide.md`。

## Whisper 生成 SRT

从音频生成中文字幕：

```bash
whisper merge.mp3 --language Chinese --task transcribe --model medium --output_format srt
```

也可以把输入替换为视频文件，Whisper 会从视频音轨转写：

```bash
whisper materials/output/final_video.mp4 --language Chinese --task transcribe --model medium --output_format srt
```

规则：

- 输入文件必须是最终音频或最终视频；不要在分镜规划阶段生成最终 SRT。
- 如果 Whisper 不可用，说明需要安装 OpenAI Whisper 或改用用户提供的字幕文件。
- Whisper 输出文件通常与输入同名，例如 `merge.srt` 或 `final_video.srt`；交付时可按项目约定复制 / 重命名为 `subtitles/subtitles.srt`。
- 生成后必须抽查中文识别、专有名词、英文产品名和时间码。

## 烧录字幕

将 SRT 烧录到最终视频：

```bash
ffmpeg -y -i materials/output/final_video.mp4 -vf "subtitles=merge.srt:force_style='FontName=Microsoft YaHei,FontSize=15,Outline=0,Shadow=0,Alignment=2,MarginV=30'" -c:a copy final_with_subtitle.mp4
```

使用规则：

- `subtitles=...` 指向实际 SRT 路径；路径含空格或特殊字符时优先改成简单英文路径。
- `FontName=Microsoft YaHei` 适合中文环境；非 Windows 环境若字体不可用，应换成本机已安装中文字体。
- `Alignment=2` 表示底部居中，`MarginV=30` 控制底部边距。
- 烧录会重新编码视频画面；如只需外挂字幕，不要使用此命令。

## SRT 规则

- 从 `00:00:00,000` 开始。
- 时间连续、不重叠。
- 格式兼容主流剪辑软件。
- 字幕不宜过长，长句应拆分。
- 无配音段不生成字幕，或明确标记为无声过场。

## 完成标准

- `subtitles/subtitles.srt` 或用户指定的 SRT 文件存在。
- 时间轴与最终音频和镜头时长一致。
- 无重叠、无倒退、无异常空洞。
- 如生成带字幕视频，视频可播放且字幕位置、字号、中文字体正常。

## 失败 / 退化路径

- 音频 / 视频不存在：回到 Audio 或 Editing 模块。
- 无法获取音频时长：请求用户提供时长，或生成草稿 SRT 并明确标记。
- 文稿和音频不一致：要求用户确认以音频还是文稿为准。
- Whisper 不可用：提示安装或要求用户提供 SRT。
- 字体不可用：更换 `force_style` 中的 `FontName`，或安装对应中文字体。

## 自检清单

- [ ] 是否在最终音频或最终视频后生成？
- [ ] 是否从 00:00:00,000 开始？
- [ ] 是否连续不重叠？
- [ ] 是否兼容标准 SRT？
- [ ] 如烧录字幕，字幕是否无乱码、无越界？
