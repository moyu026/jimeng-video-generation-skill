# jimeng-video-generation

轻量端到端即梦 / AI 视频生产编排 Skill。

它用于把技术发布稿、产品文档、Markdown、截图、录屏、架构图、流程图、机制图等素材，组织成可执行的视频生产项目：

- 视频结构规划、分镜脚本与配音稿
- 逐镜头 AI 视频 Prompt 与即梦 CLI 生成任务
- 原图转 HTML 动态图解与 HTML 图解录屏
- 用户提供音频接入
- 从音频或视频生成 SRT 字幕、字幕校准与烧录
- 视频剪辑脚本：音频拼接、音视频变速对齐、分段合成、BGM 混音
- 资产清单与剪辑交付说明

## 设计原则

参考 `web-video-presentation` 的轻量模块化模式：

```text
SKILL.md        # 主流程 / 路由 / Checkpoint
references/     # 各模块契约与细节规则
templates/      # 协作文件模板
scripts/        # 少量脚手架脚本
```

不在第一版引入复杂 `schemas/`、`evals/` 或大量自动化脚本。

## 目录结构

```text
jimeng-video-generation/
├── manifest.json
├── README.md
├── SKILL.md
├── references/
│   ├── PLANNING.md
│   ├── JIMENG-CLI.md
│   ├── HTML-DIAGRAM.md
│   ├── HTML-RECORDING.md
│   ├── SUBTITLES.md
│   ├── EDITING.md
│   ├── DELIVERY.md
│   └── TEST-PROMPTS.md
├── scripts/
│   ├── scaffold.sh
│   ├── merge_audio.py
│   ├── match_video_speed_to_audio.py
│   ├── merge_video_audio_segments.py
│   └── add_bgm_to_video.py
└── templates/
    ├── video-plan.md
    ├── narration.md
    ├── shot-list.md
    ├── asset-manifest.md
    ├── edit-guide.md
    └── html-diagram-template.html
```

## 默认工作流

```text
素材理解 → Planning → Checkpoint Plan → Assets → Checkpoint Assets → User Audio → Checkpoint User Audio → Editing → Subtitles → Delivery
```

## 初始化项目

```bash
bash .claude/skills/jimeng-video-generation/scripts/scaffold.sh output/my-video
```

## 可选运行依赖

剪辑脚本和字幕流程需要本机工具：

```bash
ffmpeg -version
ffprobe -version
whisper --help
```

- `ffmpeg` / `ffprobe`：视频合成、音频处理、字幕烧录所需的系统依赖。
- `openai-whisper`：提供 `whisper` CLI，用于从音频或视频生成 SRT。可通过 `pip install -r requirements.txt` 安装 Python 依赖。
- 烧录中文字幕时，系统需要可用中文字体；`Microsoft YaHei` 不存在时需替换为本机字体。

## 关键边界

- 不要默认跑完整链路；按用户意图路由。
- 规划阶段不生成最终 SRT。
- SRT 在用户提供最终音频或最终视频后再生成 / 校准。
- 也可用 Whisper 从最终音频或最终视频生成 SRT，并用 ffmpeg 将字幕烧录到视频。
- 原图处理必须先让用户在两个分支中选择：复用原图 + 统一背景图；将原图按原结构重绘为 HTML 动态图解。
- AI 视频中禁止生成可读文字、字母、Logo、真实代码、品牌标识；这些由后期添加。
