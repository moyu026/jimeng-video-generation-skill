# Shot List

> S00 固定为封面循环帧，最后一个 Shot 固定为用户提供的 outro。生成主体镜头后重新连续编号，并同步 narration.md 与 audioN 文件名。

## 分镜总表

| Shot ID | 板块 | 素材类型 | 生成时长 | 最终时长依据 | 画面设计 | 视频 Prompt / 执行说明 | 配音文案 | 视频文件 | 音频文件 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| S00 | Cover | cover-still | 按 audio0 生成 | audio0 | 使用确认后的 16:9 封面图循环帧 | 根据 audio0.mp3 时长生成静帧视频；不添加后期图文包装 | 请在此填写封面配音。 | materials/MP4/S00.mp4 | materials/MP3/audio0.mp3 | planned |
| S01 | Outro | user-provided-outro | 用户素材原时长 | audio1 | 使用用户提供的 openJiuwen outro 视频 | 不调用即梦生成；不使用原视频音轨；不添加后期图文包装 | openJiuwen开源社区致力于打造精准、易用、高效的生产级AI Agent。欢迎大家持续关注公众号后台回复开源加入开发交流群，解锁更多实用的智能体案例与前沿技术干货. | materials/MP4/S01.mp4 | materials/MP3/audio1.mp3 | waiting-user |

## 封面图 Prompt

```text
封面目标：<核心卖点>
当前产品 / 技术名称：<名称>
画面比例：16:9
主体构图：<主体、前景、中景、背景>
技术隐喻：<与文章内容直接相关的视觉隐喻>
视觉风格：<风格、质感>
色彩与光效：<主色、辅助色、对比关系>
禁止内容：禁止错误文字、第三方 Logo、水印和真实人物。
输出路径：assets/covers/cover-16x9.png
视频化：根据 audio0.mp3 时长循环该图片，输出 materials/MP4/S00.mp4
```

## HTML 动画录屏规则

仅当用户提供架构图 / 流程图，且即梦无法清楚表达该结构时使用；整条视频最多 3 个 HTML 录屏。

```text
HTML 输出：assets/html/<diagram-id>.html
动画时长：<A> 秒
录屏时长：<A+1> 秒
字幕安全区：底部 18%，不得放置关键内容
录屏脚本：E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py
录屏输出：assets/recordings/<diagram-id>.mp4
```

## AI 视频 Prompt 详情

> 为每个 `jimeng-video` 镜头建立同名小节。每个即梦原始视频生成 6–8 秒，并包含逐 1–2 秒变化、镜头运动、结尾状态、风格和禁止内容；最终片段时长以对应 audioN 为准，可在后续变速。不要设计后期图文包装。

## 素材自检

- [ ] Shot ID 从 S00 连续到最后的 outro。
- [ ] S00 是 cover-still，最后一段是 user-provided-outro。
- [ ] 每段视频和 audioN 一一对应，最终片段时长以对应 audioN 为准。
- [ ] 主体镜头是否以 6–8 秒即梦原始视频为主？
- [ ] HTML 是否同时满足“用户提供架构图 / 流程图”和“即梦无法清楚表达”，且总数不超过 3 个？
- [ ] 封面 Prompt 完整可执行。
- [ ] 所有主体视频 Prompt 都没有要求生成可读文字、Logo、代码或字幕。
- [ ] 没有大字标题、箭头、框选、Logo、UI 标签等后期包装。
- [ ] HTML 镜头是否记录动画时长和动画时长 + 1 秒的录屏时长？
- [ ] HTML 底部 18% 是否预留为字幕安全区？
- [ ] HTML 是否统一使用 scripts/record_html_with_ffmpeg.py 全屏录制？
- [ ] 用户已经检查并确认 shot-list.md。
