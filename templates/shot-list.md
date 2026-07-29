# Shot List

> S00 固定为封面循环帧，最后一个 Shot 固定为用户提供的 outro。生成主体镜头后重新连续编号，并同步 narration.md 与 audioN 文件名。
>
> 画面方向与尺寸：<横屏 16:9（1920×1080）/ 竖屏 6:7（1080×1260）>

## 分镜总表

| Shot ID | 板块 | 素材类型 | 生成时长 | 最终时长依据 | 画面设计 | 视频 Prompt / 执行说明 | 配音文案 | 视频文件 | 音频文件 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| S00 | Cover | cover-still | 按 audio0 生成 | audio0 | 使用与已确认画面方向一致的封面图循环帧 | 根据 audio0.mp3 时长生成静帧视频；不添加后期图文包装 | 请在此填写封面配音。 | materials/MP4/S00.mp4 | materials/MP3/audio0.mp3 | planned |
| S01 | Outro | user-provided-outro | 用户素材原时长 | audio1 | 使用用户提供的 openJiuwen outro 视频 | 不调用即梦生成；不使用原视频音轨；不添加后期图文包装 | openJiuwen开源社区致力于打造精准、易用、高效的生产级AI Agent。欢迎大家持续关注公众号后台回复开源加入开发交流群，解锁更多实用的智能体案例与前沿技术干货. | materials/MP4/S01.mp4 | materials/MP3/audio1.mp3 | waiting-user |

## 封面图 Prompt

```text
封面目标：<核心卖点>
当前产品 / 技术名称：<名称>
生成工具：dreamina CLI（图片生成，只生成无字主视觉背景）
画面方向与比例：<横屏 16:9（1920×1080）/ 竖屏 6:7（1080×1260）>
主体构图：<主体、前景、中景、背景>
技术隐喻：<与文章内容直接相关的视觉隐喻>
视觉风格：<风格、质感>
色彩与光效：<主色、辅助色、对比关系>
禁止内容：禁止生成任何可读文字、标题、产品名、Logo、品牌标识、第三方 Logo、水印和真实人物。
输出路径：assets/covers/cover-bg-16x9.png
后期嵌字：使用 scripts/create_cover_with_text.py 叠加标题、产品 / 技术名称、Logo 和标签，输出 assets/covers/cover-16x9.png
视频化：根据 audio0.mp3 时长循环 assets/covers/cover-16x9.png，输出 materials/MP4/S00.mp4
```

## HTML 动画录屏规则

仅当用户提供架构图 / 流程图，且即梦无法清楚表达该结构时使用；整条视频最多 3 个 HTML 录屏。

```text
HTML 输出：assets/html/<diagram-id>.html
动画时长：<A> 秒
录屏时长：<A+1> 秒
字幕安全区：底部 18%，不得放置关键内容
录屏脚本：E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py --orientation <landscape|portrait>
录屏输出：assets/recordings/<diagram-id>.mp4
```

## AI 视频 Prompt 详情

> 为每个 `jimeng-video` 镜头建立同名小节，并在 Prompt 中写明已确认的 `16:9` 或 `6:7`。每个即梦原始视频生成 6–8 秒，分辨率 `720p`，模型 `seedance2.0 vip`，并包含逐 1–2 秒变化、镜头运动、结尾状态、风格和禁止内容；最终片段时长以对应 audioN 为准，可在后续变速。不要设计后期图文包装。调用 `dreamina` 生成前必须先取得用户确认。

## source-video 横屏嵌入规则

> 当 `source-video` 镜头的原始素材是横屏，而已确认画面方向是竖屏时，先用 `dreamina` 生成无字背景图（调用前取得用户确认），再用 `scripts/create_branded_video.py` 把横屏素材嵌入背景图，并叠加基于该镜头配音稿生成的标题、副标题、关键词和 Logo，输出与已确认画面方向一致的视频。素材方向已与画面方向一致时直接复制到 `materials/MP4/<Shot ID>.mp4`。详见 `references/SOURCE-VIDEO.md`。

## 素材自检

- [ ] 画面方向已确认，所有 Prompt 与输出尺寸一致。
- [ ] Shot ID 从 S00 连续到最后的 outro。
- [ ] S00 是 cover-still，最后一段是 user-provided-outro。
- [ ] 每段视频和 audioN 一一对应，最终片段时长以对应 audioN 为准。
- [ ] 主体镜头是否以 6–8 秒即梦原始视频为主？
- [ ] HTML 是否同时满足“用户提供架构图 / 流程图”和“即梦无法清楚表达”，且总数不超过 3 个？
- [ ] 封面 Prompt 完整可执行，并指定使用 dreamina CLI 图片生成。
- [ ] 所有主体视频 Prompt 都没有要求生成可读文字、Logo、代码或字幕。
- [ ] 没有大字标题、箭头、框选、Logo、UI 标签等后期包装。
- [ ] HTML 镜头是否记录动画时长和动画时长 + 1 秒的录屏时长？
- [ ] HTML 底部 18% 是否预留为字幕安全区？
- [ ] HTML 是否统一使用 scripts/record_html_with_ffmpeg.py 全屏录制？
- [ ] 横屏 source-video 是否用 dreamina 生成无字背景 + create_branded_video.py 嵌入并叠加基于配音稿的文字 / Logo？
- [ ] 用户已经检查并确认 shot-list.md。
