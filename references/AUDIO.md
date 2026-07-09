# Audio 模块

## 何时读取

当用户确认进入配音阶段，或用户只要求基于 `narration.md` 生成配音音频时读取。

## 输入

- `narration.md`
- 用户指定的 TTS provider / 音色 / 语速，或用户自带音频
- 可用的 API key / CLI / 本地 TTS 工具

## 输出

```text
assets/audio/voiceover.mp3
audio-info.md
```

## 工作步骤

1. 检查 `narration.md` 是否为最终口播稿。
2. 确认 TTS provider：MiniMax、OpenAI TTS、edge-tts、ElevenLabs、Azure、用户自带音频等。
3. 检查工具、认证、API key 是否可用。
4. 生成或接入音频文件。
5. 记录音频路径、时长、provider、音色、生成时间到 `audio-info.md`。
6. 进入 Checkpoint Audio，等待用户确认后再生成字幕。

## 完成标准

- 音频文件真实存在。
- 时长已记录。
- `audio-info.md` 写明生成方式和参数。
- 不直接生成最终 SRT，除非用户已经确认音频并进入字幕阶段。

## 失败 / 退化路径

- TTS CLI 不存在：提示安装或切换 provider。
- API key 缺失：提示用户配置。
- 生成失败：记录失败原因，不假装成功。
- 用户自带音频：复制或登记音频路径，并记录时长。

## 自检清单

- [ ] 是否使用最终版 `narration.md`？
- [ ] 音频文件是否真实存在？
- [ ] 是否记录时长？
- [ ] 是否没有提前生成最终 SRT？
