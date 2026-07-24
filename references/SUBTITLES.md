# Subtitles 模块

## 前置条件

- `materials/output/narration.mp3`、`materials/output/final_video.mp4` 和 `narration.md` 已存在。
- `whisper`、`ffmpeg`、`ffprobe` 和可用中文字体已通过环境检查。

## 生成字幕

优先使用无 BGM 旁白：

```bash
whisper materials/output/narration.mp3 --language Chinese --task transcribe --model medium --output_format srt --output_dir subtitles
```

将 Whisper 输出重命名为：

```text
subtitles/subtitles.srt
```

## 按 narration 校验

1. 以 `narration.md` 为文字基准，修正 Whisper 的专有名词、英文技术名、漏字、错字和标点。
2. 保留 Whisper 时间码，只修改文字；需要拆分字幕时保持时间连续、不重叠。
3. 最后一段 outro 字幕内容必须为：

```text
openJiuwen开源社区致力于打造精准、易用、高效的生产级AI Agent。欢迎大家持续关注公众号后台回复开源加入开发交流群，解锁更多实用的智能体案例与前沿技术干货.
```

4. 运行：

```bash
python scripts/validate_subtitles_against_narration.py --narration narration.md --srt subtitles/subtitles.srt
```

校验失败时继续修正，直到退出码为 0。

## 烧录字幕

Windows 示例：

```bash
ffmpeg -y -i materials/output/final_video.mp4 -vf "subtitles=subtitles/subtitles.srt:force_style='FontName=Microsoft YaHei,FontSize=15,Outline=1,Shadow=0,Alignment=2,MarginV=30'" -c:a copy -movflags +faststart materials/output/final_video_subtitled.mp4
```

非 Windows 环境将 `FontName` 换为已安装的中文字体。路径包含特殊字符时，先把 SRT 放到简单英文路径。

## 完成标准

- SRT 时间从 0 开始，连续、不倒退、不重叠。
- 字幕文字与 `narration.md` 校验通过。
- 最后 outro 文案完整准确。
- `final_video_subtitled.mp4` 可播放，字幕无乱码、无越界。
