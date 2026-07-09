---
name: jimeng-video-generation
description: 为即梦 / AI 视频生成场景，把技术发布稿、产品文档、Markdown、截图、录屏、架构图、流程图、机制图等素材，规划并生产技术发布解读视频。支持生成视频结构规划、分镜脚本、配音稿、逐镜头 AI 视频 Prompt、即梦 CLI 生成任务、文章原图转 HTML 动态图解、HTML 录屏、配音音频、SRT 字幕校准、资产清单与剪辑交付说明。适用于“生成即梦视频 / 技术发布短视频 / 产品功能解读视频 / AI 视频 Prompt / 图片转 HTML 动态图解 / HTML 录屏 / 配音字幕 / 整理剪辑交付资产”等请求。该 Skill 采用分阶段工作流：先规划，再经用户确认后进入素材生产、音频、字幕和交付整理。
---

# Jimeng Video Generation

面向技术发布、产品新功能、项目更新和技术文章的端到端即梦 / AI 视频生产编排 Skill。

它不是一次性无确认地跑完整链路，而是采用：

```text
素材理解 → 视频规划 → Checkpoint Plan → 素材生产 → Checkpoint Assets → 配音 → Checkpoint Audio → 字幕 → 交付整理
```

主文件只负责流程路由和检查点；每个生产模块的详细规则放在 `references/`。

---

## 适用场景

- 基于发布稿 / 产品文档 / Markdown / 截图 / 录屏生成即梦技术解读视频
- 生成视频结构规划、分镜脚本、配音稿、逐镜头 AI 视频 Prompt
- 调用即梦 CLI 或生成即梦 CLI 任务说明来生产 AI 视频镜头
- 将文章原图、架构图、流程图、机制图转为 HTML 动态图解
- 对 HTML 动态图解进行浏览器录屏，作为视频素材
- 生成配音音频，或接入用户自带配音音频
- 在最终音频和镜头时长确认后生成 / 校准 SRT 字幕
- 整理 `asset-manifest.md` 和 `edit-guide.md`，交付给剪辑

不适用：

- 用户只需要普通文章摘要
- 用户要做完整网页演示型视频，应优先考虑 `web-video-presentation`
- 用户没有素材，只要求凭空构思完整发布内容；应先要求提供素材、大纲或主题说明

---

## 核心原则

1. **先规划，再生产**：先生成 `video-plan.md`、`narration.md`、`shot-list.md`，经用户确认后再进入素材生产。
2. **规划阶段不生成最终 SRT**：SRT 必须在配音音频生成或用户提供最终音频之后，根据最终音频与镜头时长生成 / 校准。
3. **不要默认跑完整链路**：用户只要求某一项时，只执行对应模块。
4. **硬 Checkpoint**：进入素材生产、配音、字幕前必须确认上游产物。
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
| 要生成配音音频 | `references/AUDIO.md` | `assets/audio/voiceover.mp3`、`audio-info.md` |
| 要生成 / 校准字幕 | `references/SUBTITLES.md` | `subtitles/subtitles.srt` |
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
  ├─ HTML 图解 → 浏览器录屏
  ├─ 原始视频 / 录屏 → 复用或裁剪
  └─ 后期图文包装 → 标题、字幕、箭头、框选

[Checkpoint Assets]
  确认素材是否就位，是否进入配音

Phase 3  Audio
  基于 narration.md 生成或接入配音音频

[Checkpoint Audio]
  确认音频可用，是否进入字幕生成 / 校准

Phase 4  Subtitles
  基于最终音频和镜头时长生成 / 校准 subtitles.srt

Phase 5  Delivery
  整理 asset-manifest.md + edit-guide.md
```

---

## 各阶段读取指南

| 阶段 | 必读 reference | 说明 |
|---|---|---|
| Planning | `references/PLANNING.md` | 视频结构、配音稿、分镜、AI Prompt、素材来源规划 |
| Jimeng CLI | `references/JIMENG-CLI.md` | 即梦任务、生成结果、失败回退、manifest 回填 |
| HTML Diagram | `references/HTML-DIAGRAM.md` | 原图按结构重绘为 HTML 动态图解，以及反馈调试 |
| HTML Recording | `references/HTML-RECORDING.md` | 浏览器录屏 HTML 图解 |
| Audio | `references/AUDIO.md` | 配音音频生成 / 用户音频接入 |
| Subtitles | `references/SUBTITLES.md` | 最终音频后的 SRT 生成 / 校准 |
| Delivery | `references/DELIVERY.md` | 资产清单、剪辑说明、交付检查 |
| Test | `references/TEST-PROMPTS.md` | 用轻量测试提示词验证路由和行为 |

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
- 每个镜头的素材类型：AI 视频、原图复用 + 背景、HTML 动态图解、原始视频复用、原始图片复用、后期包装
- AI 视频镜头的逐 1–2 秒镜头内时间轴 Prompt

规划阶段禁止生成最终 SRT，禁止未经用户确认直接调用即梦 / TTS / 录屏工具，禁止替用户擅自决定原图处理方式。

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
- 文章原图 / 架构图 / 流程图：读取 `references/HTML-DIAGRAM.md`
- HTML 图解录屏：读取 `references/HTML-RECORDING.md`
- 原始视频 / 录屏：复用、裁剪或写入剪辑说明
- 后期图文包装：写入 `edit-guide.md`，不交给 AI 视频模型生成可读文字

素材生产完成后更新 `asset-manifest.md`。

---

## Checkpoint Assets

素材生产阶段完成后必须停下，确认：即梦视频、HTML 图解、HTML 录屏、原始素材复用、`asset-manifest.md` 是否就位。用户未确认前，不进入 Phase 3。

---

## Phase 3：Audio

读取 `references/AUDIO.md`。输入 `narration.md` 和用户选择的 TTS provider / 用户自带音频。输出：

```text
assets/audio/voiceover.mp3
audio-info.md
```

如果外部 TTS 工具、API key 或 CLI 不可用，必须明确告知失败原因和退化路径，不得假装合成成功。

---

## Checkpoint Audio

音频完成后必须停下，确认文件、时长和说明。用户未确认前，不进入 Phase 4。

---

## Phase 4：Subtitles

读取 `references/SUBTITLES.md`。SRT 只在最终音频生成或用户提供最终音频后生成 / 校准。输出 `subtitles/subtitles.srt`。

---

## Phase 5：Delivery

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
│   ├── original/
│   └── audio/
└── subtitles/
    └── subtitles.srt
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
- HTML 图解是否保留原图结构和文字信息？
- 字幕是否在最终音频后生成 / 校准？
- `asset-manifest.md` 和 `edit-guide.md` 是否能支持剪辑人员接手？
