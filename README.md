# Jimeng Video Generation Skill

把技术材料编排为带配音、BGM 和字幕的即梦 / AI 技术解读视频。

核心流程：

```text
环境检查 → 确认横屏或 6:7 竖屏 → 规划三文件
→ 用户确认 narration/shot-list → 用户生成 audioN
→ S00 封面循环帧 + 主体视频 + 用户 outro → 素材检查 → 变速
→ 旁白与 BGM 合成 → Whisper → narration 校验 → 字幕烧录
```

## 仓库结构

```text
.
├─ SKILL.md                              # Skill 入口和完整生产流程
├─ README.md                             # 项目概览、结构和使用说明
├─ manifest.json                         # Skill 名称、版本、兼容环境和输出清单
├─ requirements.txt                      # Python 依赖
├─ references/                           # 各生产阶段的详细规则
│  ├─ ENVIRONMENT.md                     # 环境检查和安装要求
│  ├─ PLANNING.md                        # 规划文件、镜头和配音规则
│  ├─ COVER.md                           # 封面图和 S00 封面视频规则
│  ├─ JIMENG-CLI.md                      # 即梦视频生成要求
│  ├─ HTML-DIAGRAM.md                    # 架构图、流程图的 HTML 动画规范
│  ├─ HTML-RECORDING.md                  # HTML 全屏录屏规范
│  ├─ EDITING.md                         # 视频变速、拼接和 BGM 合成流程
│  ├─ SUBTITLES.md                       # Whisper、字幕校验和烧录规则
│  ├─ DELIVERY.md                        # 最终交付物和验收要求
│  └─ TEST-PROMPTS.md                    # Skill 流程测试用例
├─ scripts/                              # 可重复执行的生产脚本
│  ├─ scaffold_project.py                # 创建标准视频项目目录
│  ├─ check_environment.py               # 检查并提示配置生产环境
│  ├─ check_narration_consistency.py     # 检查配音稿与镜头表是否一致
│  ├─ create_cover_video.py              # 按 audio0 时长生成 S00 封面视频
│  ├─ create_cover_with_text.py           # 生成带文字的横竖屏封面图
│  ├─ record_html_with_ffmpeg.py          # 全屏打开并录制 HTML 动画
│  ├─ check_media_inventory.py            # 检查 SNN、audioN、BGM 和 outro
│  ├─ match_video_speed_to_audio.py       # 按对应音频时长变速视频
│  ├─ merge_video_audio_segments.py       # 拼接分段视频和旁白
│  ├─ add_bgm_to_video.py                 # 为旁白视频混入 BGM
│  ├─ merge_audio.py                      # 合并 audioN，供 Whisper 使用
│  └─ validate_subtitles_against_narration.py # 按 narration 校验字幕
└─ templates/                            # 新视频项目的初始模板
   ├─ video-plan.md                       # 视频目标、结构和素材策略
   ├─ narration.md                        # 按 Shot ID 切分的配音稿
   ├─ shot-list.md                        # 镜头表、封面和即梦 Prompt
   ├─ asset-manifest.md                   # 素材状态清单
   ├─ edit-guide.md                       # 剪辑顺序和导出参数
   └─ html-diagram-template.html          # HTML 架构/流程动画模板
```

## 初始化视频项目

```bash
python scripts/scaffold_project.py output/my-video
```

脚本不会覆盖已有文件，生成的项目结构如下：

```text
output/my-video/
├─ article.md                         # 用户原始技术材料或整理后的文章
├─ video-plan.md                      # 视频规划
├─ narration.md                       # 分段配音稿
├─ shot-list.md                       # 分镜和生成 Prompt
├─ asset-manifest.md                  # 生产过程中增量更新的素材清单
├─ edit-guide.md                      # 剪辑与导出说明
├─ assets/
│  ├─ original/                       # 用户提供的文档、图片、架构图和源视频
│  ├─ covers/                         # 封面图
│  ├─ jimeng/                         # 即梦生成过程中的下载或辅助素材
│  ├─ html/                           # HTML 动画文件及模板
│  └─ recordings/                     # HTML 动画录屏
├─ materials/
│  ├─ MP3/                            # audio0...audioN 和 bgm.mp3
│  ├─ MP4/                            # S00...SNN 原始分段视频
│  ├─ video_output/                   # 按音频时长变速后的 S00...SNN
│  └─ output/                         # 合成音频、无字幕成片和最终成片
└─ subtitles/
   └─ subtitles.srt                   # Whisper 生成并按 narration 校验的字幕
```

用户素材应放在：

- 文档、图片、架构图、流程图和源视频：`assets/original/`
- 分段配音和 BGM：`materials/MP3/`
- 用户提供的最后一段 outro：按最终 Shot ID 放入 `materials/MP4/SNN.mp4`

## 固定命名

- 视频：`materials/MP4/S00.mp4...SNN.mp4`
- 配音：`materials/MP3/audio0.mp3...audioN.mp3`
- BGM：`materials/MP3/bgm.mp3`
- 变速视频：`materials/video_output/S00.mp4...SNN.mp4`
- 成片：`materials/output/final_video_subtitled.mp4`

`S00` 是封面图循环帧，最后一个视频是用户提供的 outro。流程不制作后期图文包装，只在最后烧录已按 narration 校验的字幕。

详细行为以 `SKILL.md` 和 `references/` 为准。
