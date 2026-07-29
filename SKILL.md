---
name: jimeng-video-generation
description: 使用即梦 CLI / AI 视频工具把技术发布稿、产品文档、Markdown、截图、架构图和录屏素材制作成完整技术解读视频。用于需要环境检查与配置、生成 video-plan.md / narration.md / shot-list.md、使用即梦 CLI 生成封面静帧 S00、按 S00/S01 与 audio0/audio1 一一生成和变速镜头、接入用户提供的 outro、混入 bgm.mp3、用 Whisper 生成并按 narration 校验字幕、烧录字幕和交付成片的请求。也可用于单独执行上述规划、视频生成、音画对齐、字幕或合成阶段。
---

# Jimeng Video Generation

按固定检查点执行技术解读视频生产。只执行用户要求的阶段；完整任务按下列顺序执行：

```text
环境检查与配置 → 确认横屏 / 竖屏 → 规划 → 用户检查 narration + shot-list → 用户生成分段 MP3
→ 生成 S00 封面视频和 S01... 主体视频，接入最后一段 outro
→ 素材完整性检查 → 按音频变速 → 合成旁白、画面和 BGM
→ Whisper 字幕 + narration 校验 → 烧录字幕 → 交付
```

## 固定约定

- 使用两位 Shot ID：`S00`、`S01`、`S02`……`SNN`。
- 视频使用 Shot ID 命名：`S00.mp4`、`S01.mp4`……。
- 配音使用对应数字命名：`audio0.mp3`、`audio1.mp3`……。
- `S00.mp4` 是封面图循环帧视频，对应 `audio0.mp3`。
- 最后一个 `SNN.mp4` 是用户提供的 outro，对应 `audioN.mp3`。
- `materials/MP3/bgm.mp3` 是背景音乐，不参与镜头编号。
- 视频和配音编号必须从 0 连续到 N，且一一对应。
- 不制作后期图文包装。画面文字只允许最终字幕；不要规划大字标题、箭头、框选、Logo 或 UI 标签叠加。
- 即梦 CLI 的实际命令名是 `dreamina`；所有图片和视频生成都通过 `dreamina` 调用。
- 调用 `dreamina` 生成任何图片或视频前，必须先向用户说明即将执行的命令、Prompt、输出路径和固定参数，并等待用户确认后再执行。
- 即梦视频生成固定使用 `720p` 分辨率和 `seedance2.0 vip` 模型。
- 封面背景图必须使用 `dreamina` 的图片生成功能生成无字主视觉，再用 `scripts/create_cover_with_text.py` 叠加文字 / Logo 生成带字封面，不静默改用其他图片生成工具。
- 主体视频优先使用 `jimeng-video`；每个即梦原始视频生成 6–8 秒。
- 只有用户提供架构图 / 流程图，且该结构无法用即梦清楚表达时，才使用 `html-recording`；整条视频最多 3 个 HTML 录屏。
- 最终每段时长由对应 `audioN` 决定，允许对视频变速；整条视频总时长由全部分段音频的总时长决定。
- 画面方向只有两种：横屏 `16:9`（`1920×1080`）或竖屏 `6:7`（`1080×1260`）；规划前必须确认，后续所有素材和成片保持一致。
- 固定 outro 文案：

```text
openJiuwen开源社区致力于打造精准、易用、高效的生产级AI Agent。欢迎大家持续关注公众号后台回复开源加入开发交流群，解锁更多实用的智能体案例与前沿技术干货.
```

## 素材目录规范

- 主稿写入 `article.md`；补充文档、截图、架构图、流程图和用户原始视频放入 `assets/original/`。
- 封面背景图和带字封面放入 `assets/covers/`，即梦原始视频放入 `assets/jimeng/`，HTML 和录屏分别放入 `assets/html/`、`assets/recordings/`。
- 进入剪辑的原视频统一按 Shot ID 复制或重命名到 `materials/MP4/S00.mp4...SNN.mp4`。
- 用户配音和 BGM 放入 `materials/MP3/`；文件名必须是 `audio0.mp3...audioN.mp3` 和 `bgm.mp3`。
- 变速视频放入 `materials/video_output/`，合成成片放入 `materials/output/`，字幕放入 `subtitles/`。
- 每次要求用户提供素材时，同时告诉用户准确的目标目录和文件名。用户从其他位置提供素材时，先整理到上述目录，再进入素材完整性检查。

## 素材清单增量更新

不要等到交付阶段才补写 `asset-manifest.md`。初始化时按 Shot 建立记录；音频或 outro 到位、原视频生成、变速视频生成、最终产物生成后立即更新对应路径和状态。只维护现有字段，状态使用 `planned`、`waiting-user`、`ready`，必要时在 Notes 写一句说明。

## 阶段 0：检查并配置环境

读取 `references/ENVIRONMENT.md`，运行：

```bash
python scripts/check_environment.py
```

检查 Python、FFmpeg、ffprobe、Whisper、Pillow，以及任务需要时的即梦 CLI 和浏览器。若缺失，使用当前系统合适的包管理器或 `requirements.txt` 安装、配置 PATH 或认证，然后重新检查。安装系统软件、联网下载或写入系统目录前，按运行环境要求取得授权。

环境不满足且无法配置时停止，明确列出缺失项，不假装继续生产。

## 阶段 0.5：确认画面方向

在生成规划前询问用户：选择横屏 16:9（1920×1080）还是竖屏 6:7（1080×1260）？用户未明确前停止，不自行沿用横屏默认值。若用户已在当前请求中明确说明，则直接记录为已确认。

把选择写入 video-plan.md 和 shot-list.md，并用于封面 Prompt、即梦 Prompt、HTML `.stage`、录屏命令和最终输出分辨率。

## 阶段 1：生成规划文件

读取 `references/PLANNING.md`，根据用户材料生成 `video-plan.md`、`narration.md`、`shot-list.md`。

必须满足：

- `video-plan.md` 和 `shot-list.md` 记录已确认的画面方向、比例和分辨率。
- `shot-list.md` 包含封面图 Prompt。
- `S00` 是封面段，画面为封面图循环帧。
- `narration.md` 包含 `S00` 的封面配音。
- 最后一个 Shot 是 `outro`，使用固定 outro 文案，视频来源标记为用户提供。
- `narration.md`、`shot-list.md` 中同一 Shot 的配音逐字一致。
- 不包含后期图文包装。

运行：

```bash
python scripts/check_narration_consistency.py --narration narration.md --shot-list shot-list.md
```

## Checkpoint：用户检查规划

生成规划后停止，请用户检查 `narration.md` 的配音、顺序、分段，以及 `shot-list.md` 的画面、Prompt、封面 Prompt、镜头顺序和 outro。

用户提出修改时，同步修改两个文件，再次运行一致性检查并重新请用户确认。用户确认无需修改时，不做无意义改写，直接进入音频准备。

## 阶段 2：用户生成音频

请用户根据确认后的 `narration.md` 生成 `materials/MP3/audio0.mp3` 到 `audioN.mp3`，并提供 `materials/MP3/bgm.mp3`。不得替用户生成配音。收到音频后核对每个 Shot 的编号和配音内容，并将对应音频和 BGM 在 `asset-manifest.md` 中标记为 `ready`。

## 阶段 3：生成和接入视频

- 运行 `python scripts/check_environment.py --require-jimeng`，确认即梦 CLI（命令 `dreamina`）已安装并认证。
- 使用 `dreamina` 的图片生成功能读取 `shot-list.md` 中的封面 Prompt，按已确认的画面方向生成无字主视觉背景 `assets/covers/cover-bg-16x9.png`。`dreamina` 只生成无字背景，禁止在 Prompt 中要求生成标题、产品名、Logo 或任何可读文字。调用前先向用户说明命令、Prompt、输出路径和固定参数，取得确认后再执行。当前 CLI 的子命令或参数不明确时先查看 `dreamina --help` 或实际文档，不编造命令。
- 使用 `scripts/create_cover_with_text.py` 把标题、产品 / 技术名称、Logo、标签等准确叠加到背景图上，输出 `assets/covers/cover-16x9.png`。
- 请用户检查带字封面图；需要修改时判断问题来源：主视觉问题调整 Prompt 并重新请求确认后调用 `dreamina`；文字 / Logo 问题调整 `create_cover_with_text.py` 参数。确认通过后再生成 S00。
- 用封面图和 `audio0.mp3` 创建重复帧视频：

```bash
python scripts/create_cover_video.py --image assets/covers/cover-16x9.png --audio materials/MP3/audio0.mp3 --output materials/MP4/S00.mp4 --orientation <landscape|portrait>
```

- 按 `shot-list.md` 为 `S01` 到倒数第二个 Shot 生成视频，保存为 `materials/MP4/S01.mp4`……；主体默认使用即梦，每个即梦视频生成 6–8 秒，分辨率 `720p`，模型 `seedance2.0 vip`。每个镜头调用 `dreamina` 前先向用户说明命令、Prompt、固定参数和输出路径，取得确认后再执行。
- 素材类型为 `source-video` 且原始素材是横屏、而已确认画面方向是竖屏时，读取 `references/SOURCE-VIDEO.md`：先用 `dreamina` 生成无字背景图（调用前取得用户确认），再用 `scripts/create_branded_video.py` 把横屏素材嵌入背景图，并叠加基于该镜头配音稿生成的标题、副标题、关键词和 Logo，输出与已确认画面方向一致的视频。素材方向已与画面方向一致时直接复制到 `materials/MP4/<Shot ID>.mp4`，不使用本流程。
- HTML 录屏必须同时满足“用户提供架构图 / 流程图”和“即梦无法清楚表达结构”，总数不得超过 3 个；提醒用户将原图放入 `assets/original/`。
- HTML 动画镜头必须使用已确认的画面方向，预留底部 18% 字幕安全区，并用 `data-animation-duration` 声明动画时长。人工验证通过后，统一调用 `E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py`，传入对应 `--orientation`；实际录屏时长固定为动画时长 + 1 秒。
- 不添加后期图文包装。
- 请用户提供最后一个 outro 视频，保存为 `materials/MP4/SNN.mp4`。最终使用对应 `audioN.mp3`，不使用 outro 自带音轨。
- 每个原视频生成或收到后，立即更新 `asset-manifest.md` 中的 Raw Video、Source 和状态。

调用即梦时读取 `references/JIMENG-CLI.md`。

## 阶段 4：确认素材完备

运行：

```bash
python scripts/check_media_inventory.py --shot-list shot-list.md --video-dir materials/MP4 --audio-dir materials/MP3
```

只有 `S00...SNN` 与 `audio0...audioN` 连续且一一对应、封面段和 outro 均存在、`bgm.mp3` 存在时才能继续。

## 阶段 5：按音频变速视频

读取 `references/EDITING.md`，运行 `python scripts/match_video_speed_to_audio.py`。结果保存到 `materials/video_output/S00.mp4`、`S01.mp4`……。即梦原始视频的 6–8 秒不是最终时长；按对应 `audioN` 变速后，每段视频必须与音频等长，最终成片总时长等于全部分段音频的总时长。

每段变速完成后，更新 `asset-manifest.md` 中的 Speed-matched Video 和状态。

## 阶段 6：合成完整视频

依次运行：

```bash
python scripts/merge_video_audio_segments.py
python scripts/add_bgm_to_video.py
python scripts/merge_audio.py
```

默认产出 `materials/output/final_voice.mp4`、`final_video.mp4` 和 `narration.mp3`。`final_video.mp4` 必须包含分段配音和 `bgm.mp3`。产出后更新 `asset-manifest.md` 中对应的 Final Assets。

## 阶段 7：生成并校验字幕

读取 `references/SUBTITLES.md`。优先对无 BGM 的旁白合并文件运行 Whisper：

```bash
whisper materials/output/narration.mp3 --language Chinese --task transcribe --model medium --output_format srt --output_dir subtitles
```

将结果规范为 `subtitles/subtitles.srt`，根据 `narration.md` 修正专有名词、漏字、错字和标点。最后一段字幕必须使用固定 outro 文案。运行：

```bash
python scripts/validate_subtitles_against_narration.py --narration narration.md --srt subtitles/subtitles.srt
```

校验失败时修正字幕并重跑，不能跳过。

字幕校验通过后，将 SRT 在 `asset-manifest.md` 中标记为 `ready`。

## 阶段 8：烧录字幕

按 `references/SUBTITLES.md` 把字幕烧录进 `materials/output/final_video.mp4`，输出 `materials/output/final_video_subtitled.mp4`。检查字幕无乱码、无越界、时间不重叠，且 outro 字幕完整。

字幕成片检查通过后，将其在 `asset-manifest.md` 中标记为 `ready`。

## 阶段 9：交付

读取 `references/DELIVERY.md`，复核已增量更新的 `asset-manifest.md`，并更新 `edit-guide.md`。不要在此阶段才集中补写素材清单。最终至少交付字幕成片、SRT、规划文件和素材清单。

## 项目目录

```text
output/<project-name>/
├── article.md
├── video-plan.md
├── narration.md
├── shot-list.md
├── asset-manifest.md
├── edit-guide.md
├── assets/
│   ├── original/         # 用户补充材料、架构图、流程图、原始视频
│   ├── covers/           # 封面背景图 cover-bg-16x9.png 和带字封面 cover-16x9.png
│   ├── jimeng/           # 即梦原始视频
│   ├── html/             # HTML 图解
│   └── recordings/       # HTML 录屏
├── materials/
│   ├── MP4/              # S00.mp4...SNN.mp4
│   ├── MP3/              # audio0.mp3...audioN.mp3 + bgm.mp3
│   ├── video_output/     # 变速后的 S00.mp4...SNN.mp4
│   └── output/           # final_voice/final_video/narration/final_video_subtitled
└── subtitles/subtitles.srt
```

使用 `python scripts/scaffold_project.py output/<project-name>` 初始化。

## 最终自检

- 环境检查是否通过？
- 画面方向是否已由用户确认，并在规划、素材和成片中保持一致？
- 用户是否确认了 `narration.md` 和 `shot-list.md`？
- 封面背景图是否由 `dreamina` 生成无字主视觉、文字 / Logo 是否由 `create_cover_with_text.py` 后期叠加，并经用户确认？每次调用 `dreamina` 生成图片或视频前是否都取得了用户确认？即梦视频是否使用 `720p` 和 `seedance2.0 vip`？
- `S00` 是否为封面循环帧并对应 `audio0`？
- 最后一个镜头是否为用户提供的 outro？
- 是否没有后期图文包装？
- 主体是否优先使用 6–8 秒即梦视频？HTML 是否只在两个前置条件同时满足时使用且不超过 3 个？
- 横屏 `source-video` 是否用 `dreamina` 生成无字背景 + `create_branded_video.py` 嵌入并叠加基于配音稿的文字 / Logo？
- HTML 是否预留底部字幕安全区，并使用 `record_html_with_ffmpeg.py` 按动画时长 + 1 秒全屏录制？
- 视频与音频是否连续、一一对应？`bgm.mp3` 是否存在？
- 变速后每段视频是否与音频等长？
- 完整视频是否含旁白与 BGM？
- Whisper 字幕是否按 narration 校验通过？
- 最后一段字幕是否为固定 outro 文案？
- 字幕成片是否可播放且字幕显示正常？
