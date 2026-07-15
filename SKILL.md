---
name: jimeng-video-generation
description: 为即梦 / AI 视频生成场景，把技术发布稿、产品文档、Markdown、截图、录屏、架构图、流程图、机制图等素材，规划并生产技术发布解读视频。支持生成视频结构规划、分镜脚本、配音稿、逐镜头 AI 视频 Prompt、即梦 CLI 生成任务、文章原图转 HTML 动态图解、HTML 录屏、16:9 主封面与视频号封面、用户提供音频接入、音视频生成 SRT 字幕、字幕烧录、视频音频分段合成、变速对齐、BGM 混音、资产清单与剪辑交付说明。适用于“生成即梦视频 / 技术发布短视频 / 产品功能解读视频 / AI 视频 Prompt / 图片转 HTML 动态图解 / HTML 录屏 / 配音字幕 / 视频剪辑脚本 / 整理剪辑交付资产”等请求。该 Skill 采用分阶段工作流：先规划，再经用户确认后进入素材生产、用户音频确认、剪辑、字幕和交付整理。
---

# Jimeng Video Generation

面向技术发布、产品新功能、项目更新和技术文章的端到端即梦 / AI 视频生产编排 Skill。

它不是一次性无确认地跑完整链路，而是采用：

```text
素材理解 → 视频规划 → Checkpoint Plan → 素材生产 → Checkpoint Assets → 用户音频确认 → 剪辑合成 → 字幕 → 交付整理
```

主文件只负责流程路由和检查点；每个生产模块的详细规则放在 `references/`。

---

## 适用场景

- 基于发布稿 / 产品文档 / Markdown / 截图 / 录屏生成即梦技术解读视频
- 生成视频结构规划、分镜脚本、配音稿、逐镜头 AI 视频 Prompt
- 调用即梦 CLI 或生成即梦 CLI 任务说明来生产 AI 视频镜头
- 将文章原图、架构图、流程图、机制图转为 HTML 动态图解
- 对 HTML 动态图解进行浏览器录屏，作为视频素材
- 生成 16:9 主封面，经人工检查后生成 1080×608 与 1080×1260 视频号封面
- 接入用户提供的配音 / 音频文件，并登记路径和时长
- 使用脚本完成音频拼接、视频按音频变速、分段音视频合成和 BGM 混音
- 从最终音频或视频生成 / 校准 SRT 字幕，并可将字幕烧录进视频
- 整理 `asset-manifest.md` 和 `edit-guide.md`，交付给剪辑

不适用：

- 用户只需要普通文章摘要
- 用户要做完整网页演示型视频
- 用户没有素材，只要求凭空构思完整发布内容；应先要求提供素材、大纲或主题说明

---

## 核心原则

1. **先规划，再生产**：先生成 `video-plan.md`、`narration.md`、`shot-list.md`，经用户确认后再进入素材生产。
2. **规划阶段不生成最终 SRT**：SRT 必须在用户提供最终音频或最终视频之后，根据最终音频 / 视频与镜头时长生成 / 校准。
3. **不要默认跑完整链路**：用户只要求某一项时，只执行对应模块。
4. **硬 Checkpoint**：进入素材生产、剪辑、字幕前必须确认上游产物；每张 HTML 图解生成后必须人工验证通过，才能录屏；16:9 主封面必须人工检查通过，才能生成视频号尺寸封面。
5. **技术表达专业克制**：关键技术特性、机制说明、性能收益、边界判断应尽量参考原文提取，不要过度口语化或改成泛营销话术。
6. **时长动态决定**：根据素材复杂度、信息量和复用视频 / 录屏片段动态决定，总时长控制在 150 秒以内；不要为了压时长删掉必要技术解释。
7. **原图处理只有两个分支**：复用原图 + 生成统一背景图；将原图按原结构重绘为 HTML 动态图解。
8. **AI 视频禁止生成关键文字资产**：AI 视频中禁止生成可读文字、字母、Logo、真实代码、品牌标识；文字、标题、字幕、UI 标签由后期添加。
9. **默认禁止真实人物**：除非用户明确要求，禁止 AI 生成真实人物、人物背影、手部特写。
10. **英文固定文件名作为协作接口**：端到端流程默认使用 `video-plan.md`、`narration.md`、`shot-list.md`、`asset-manifest.md`、`edit-guide.md`、`subtitles.srt`。

---
## Intent Router：先判断用户当前任务

| 用户意图 | 进入阶段 / 参考文件 | 默认产出 |
|---|---|---|
| 只要视频脚本 / 分镜 / 配音稿 | `references/PLANNING.md` | `video-plan.md`、`narration.md`、`shot-list.md` |
| 只要即梦 Prompt | `references/PLANNING.md` | 单镜头或多镜头 AI 视频 Prompt |
| 要调用即梦生成 AI 视频 | `references/JIMENG-CLI.md` | `assets/jimeng/*.mp4`、更新 `asset-manifest.md` |
| 要把原图转 HTML | `references/HTML-DIAGRAM.md` | `assets/html/*.html` |
| 要调试 HTML 图解 | `references/HTML-DIAGRAM.md` | 局部修改后的 HTML |
| 要录屏 HTML | `references/HTML-RECORDING.md` | `assets/recordings/*.mp4` |
| 要生成封面 / 视频号封面 | `references/COVER.md` | `assets/covers/*.png`、更新 `asset-manifest.md` |
| 要接入用户提供音频 | 本文件 Phase 3 | 确认音频路径、时长和编号对应关系 |
| 要剪辑合成 / 音视频对齐 / 加 BGM | `references/EDITING.md` | `materials/output/final_video.mp4` 或最终导出视频 |
| 要从音频或视频生成 / 校准字幕 / 烧录字幕 | `references/SUBTITLES.md` | `subtitles/subtitles.srt` 或带字幕视频 |
| 要完整端到端视频 | 本文件完整工作流 + 各模块 reference | 规划、素材、音频、字幕、交付清单 |
| 要优化 Skill 本身 | 先给修改计划，再修改 Skill | Skill 修改计划 / 文档更新 |

追问原则：

- 无法判断产品 / 功能对象：必须追问。
- 只缺时长、比例、配音风格：不追问，使用默认值。
- 素材中包含文章原图、架构图、流程图、机制图或产品截图，且用户未明确处理方式：必须先询问两个分支。
- 用户只要求单项内容：只输出对应内容，不强制生成完整分镜或完整项目。

---

## 工作流总览

```text
Phase 1  Planning
  输入素材 → 理解技术主题 → 生成 video-plan.md + narration.md + shot-list.md

[Checkpoint Plan]
  确认视频结构、配音稿、分镜、素材来源、原图处理方式

Phase 2  Assets
  ├─ AI 视频镜头 → Jimeng CLI
  ├─ 文章原图 / 架构图 → HTML 动态图解
  ├─ Checkpoint HTML Review：人工打开 HTML 验证效果
  ├─ HTML 图解 → Chrome / Edge + ffmpeg 录屏
  ├─ 封面 → 16:9 主封面 → Checkpoint Cover Review → 视频号封面
  ├─ 原始视频 / 录屏 → 复用或裁剪
  └─ 后期图文包装 → 标题、字幕、箭头、框选

[Checkpoint Assets]
  确认素材是否就位，是否等待 / 接入用户音频

Phase 3  User Audio
  接入用户提供的最终音频，确认路径、时长、编号对应关系

[Checkpoint User Audio]
  确认音频可用，是否进入剪辑合成

Phase 4  Editing
  根据素材和音频执行变速对齐、分段合成、字幕烧录、BGM 混音等剪辑脚本

Phase 5  Subtitles
  基于最终音频或最终视频生成 / 校准 subtitles.srt，可选烧录字幕

Phase 6  Delivery
  整理 asset-manifest.md + edit-guide.md
```

---

## 各阶段读取指南

| 阶段 | 必读 reference | 说明 |
|---|---|---|
| Planning | `references/PLANNING.md` | 视频结构、配音稿、分镜、AI Prompt、素材来源规划 |
| Jimeng CLI | `references/JIMENG-CLI.md` | 即梦任务、生成结果、失败回退、manifest 回填 |
| HTML Diagram | `references/HTML-DIAGRAM.md` | 原图按结构重绘为 HTML 动态图解，以及强制人工验证 / 反馈调试 |
| HTML Recording | `references/HTML-RECORDING.md` | 人工验证通过后，用 Chrome / Edge + ffmpeg 录屏 HTML 图解 |
| Cover | `references/COVER.md` | 16:9 主封面、强制人工检查、视频号尺寸封面 |
| Editing | `references/EDITING.md` | 视频剪辑脚本：音频拼接、变速对齐、分段合成、BGM 混音 |
| Subtitles | `references/SUBTITLES.md` | 从音频 / 视频生成 SRT、校准字幕、烧录字幕 |
| Delivery | `references/DELIVERY.md` | 资产清单、剪辑说明、交付检查 |
| Test | `references/TEST-PROMPTS.md` | 用轻量测试提示词验证路由和行为 |

运行录屏、剪辑或字幕命令前，先按对应 reference 的“前置依赖”检查 `ffmpeg`、`ffprobe`、`whisper`、Chrome / Edge 和中文字体。

---
## Phase 1：Planning

读取 `references/PLANNING.md`，默认产出：

```text
video-plan.md
narration.md
shot-list.md
```

规划阶段必须包含：

- 核心功能 / 用户痛点 / 旧方式不足 / 一句话定义 / 核心变化
- 2–3 个最适合视频表达的核心能力
- 一个最强实战案例或 Wow Moment
- 适用场景和边界判断
- Hook / What / How / Future 四段式叙事
- 每个镜头的素材类型：AI 视频、原图复用 + 统一背景图、原图转 HTML 动态图解并录屏、原始视频复用、后期包装
- AI 视频镜头的逐 1–2 秒镜头内时间轴 Prompt；即梦镜头默认优先 4–8 秒，复杂内容优先拆成多个短镜头
- 唯一配音文本：`配音总稿` 按 Shot ID 原样切分到 `narration.md` 分镜映射，并同步到 `shot-list.md` 配音文案；拼接后必须与总稿逐字一致
- 视频封面图 Prompt，必须突出当前文章产品 / 技术名称；封面文字、Logo、作者名、平台标签由后期添加

规划阶段禁止生成最终 SRT，禁止未经用户确认直接调用即梦 / 录屏工具，禁止生成配音音频，禁止替用户擅自决定原图处理方式。

---

## Checkpoint Plan

`video-plan.md`、`narration.md`、`shot-list.md` 完成后必须停下，向用户确认：

```text
规划已完成，产出：
- video-plan.md：视频结构与叙事骨架
- narration.md：配音稿
- shot-list.md：分镜、素材来源、AI Prompt / HTML 图解规划

请确认 5 件事：
1. 视频结构是否合理？
2. 配音稿是否需要调整？
3. 分镜和素材来源是否确认？
4. 原图处理方式是否确认：
   1）复用原图 + 生成统一背景图
   2）将原图按原结构重绘为 HTML 动态图解
5. 是否进入素材生产阶段？
```

用户未确认前，不进入 Phase 2。

---

## Phase 2：Assets

根据 `shot-list.md` 拆分素材生产任务：

- AI 生成视频镜头：读取 `references/JIMENG-CLI.md`
- 文章原图 / 架构图 / 流程图：读取 `references/HTML-DIAGRAM.md`，生成后必须执行人工验证
- HTML 图解录屏：仅在对应 HTML 人工验证通过后读取 `references/HTML-RECORDING.md`，默认使用 Chrome / Edge + ffmpeg `gdigrab` 半自动录屏
- 封面图：读取 `references/COVER.md`，先生成 16:9 主封面并人工检查，通过后再生成 1080×608 与 1080×1260 视频号封面
- 原始视频 / 录屏：复用、裁剪或写入剪辑说明
- 后期图文包装：写入 `edit-guide.md`，不交给 AI 视频模型生成可读文字

素材生产完成后更新 `asset-manifest.md`。

---

## Checkpoint Assets

素材生产阶段完成后必须停下，确认：即梦视频、HTML 图解、HTML 录屏、封面图、原始素材复用、`asset-manifest.md` 是否就位，以及用户音频是否已提供。用户未确认前，不进入 Phase 3。

---

## Phase 3：User Audio

不生成音频。本阶段只接入用户已经提供的最终音频。

需要确认：

- 最终完整音频路径，例如 `merge.mp3`
- 分段音频路径，例如 `materials/MP3/audio1.mp3`、`audio2.mp3`
- 音频与 `shot-list.md` 或 `videoN` 的编号对应关系
- 音频时长；必要时使用 `ffprobe` 获取

---

## Checkpoint User Audio

用户音频确认后必须停下，确认文件、时长和编号对应关系。用户未确认前，不进入 Phase 4。

---

## Phase 4：Editing

读取 `references/EDITING.md`。按用户目标选择现有脚本：

- `scripts/merge_audio.py`：拼接 `materials/audio*.mp3` 为 `merge.mp3`
- `scripts/match_video_speed_to_audio.py`：将 `videoN` 变速匹配 `audioN`
- `scripts/merge_video_audio_segments.py`：将编号视频和音频合成片段后拼接为 `final_video.mp4`
- `scripts/add_bgm_to_video.py`：给最终视频混入 BGM
- `scripts/record_html_with_ffmpeg.py`：用 Chrome / Edge + ffmpeg 录制 HTML 图解
- `scripts/check_narration_consistency.py`：校验配音总稿、分镜映射与 `shot-list.md` 配音文案一致性
- `scripts/create_cover_with_text.py`：为无字封面背景叠加准确标题、产品 / 技术名称和 Logo，并导出多尺寸封面

执行前必须确认脚本顶部配置区中的输入 / 输出目录符合当前项目；必要时先修改配置或提示用户目录约定。

---

## Phase 5：Subtitles

读取 `references/SUBTITLES.md`。SRT 只在用户提供最终音频或最终视频存在后生成 / 校准。输出 `subtitles/subtitles.srt`。

如用户提供最终视频或要求从视频中生成字幕，可直接用视频作为 Whisper 输入；如用户要求“添加字幕 / 烧字幕”，按 `references/SUBTITLES.md` 使用 ffmpeg `subtitles` filter 输出带字幕视频。

---

## Phase 6：Delivery

读取 `references/DELIVERY.md`。默认产出：

```text
asset-manifest.md
edit-guide.md
```

交付说明必须覆盖素材路径、生成来源、配音、字幕、后期包装、剪辑顺序和导出建议。

---

## 文件输出约定

默认项目目录：

```text
output/<project-name>/
├── article.md
├── video-plan.md
├── narration.md
├── shot-list.md
├── asset-manifest.md
├── edit-guide.md
├── assets/
│   ├── jimeng/
│   ├── html/
│   ├── recordings/
│   ├── covers/
│   └── original/
├── subtitles/
│   └── subtitles.srt
└── materials/
    ├── MP4/
    ├── MP3/
    ├── video_output/
    └── output/
```

可使用：

```bash
bash .claude/skills/jimeng-video-generation/scripts/scaffold.sh output/<project-name>
```

初始化目录和模板。

---

## 全局自检

交付任何阶段产物前，检查：

- 是否正确路由到用户实际需要的模块，而不是默认跑完整流程？
- 是否在该停下的 Checkpoint 停下了？
- 规划阶段是否没有生成最终 SRT？
- 技术观点是否尽量来自原文，且表达准确克制？
- 是否明确区分素材类型？
- AI 视频 Prompt 是否包含镜头时长、时间轴、运动、结尾状态、风格、禁止内容？
- 原图处理方式是否经过用户确认？
- HTML 图解是否保留原图结构和文字信息，并已人工验证通过后才录屏？
- 封面是否先生成 16:9 主图并人工检查通过，再生成视频号尺寸？是否突出当前文章产品 / 技术名称？
- 字幕是否在用户提供最终音频或最终视频后生成 / 校准？
- `asset-manifest.md` 和 `edit-guide.md` 是否能支持剪辑人员接手？
