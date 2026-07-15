# Narration

> Final voiceover text. Do not include non-spoken headings, table labels, or production notes in the spoken draft.

## 配音总稿

<!-- Write the unique full voiceover here. The text should be natural to read aloud and technically accurate. -->

> 配音总稿是唯一配音文本来源。先写定这一份总稿，再按 Shot ID 原样切分到下方映射；映射不能摘要、改写、换词或压缩。

## 分镜配音映射

| Shot ID | 时间段 | 配音文案 | 字数 | 预估时长 | 备注 |
|---|---|---|---:|---:|---|
| S01 | 00:00-00:08 |  |  |  | 从配音总稿原样切分；不得摘要改写 |

## 配音自检

- [ ] 配音总稿只包含可朗读内容，没有标题、序号、表格说明等非口播内容。
- [ ] 技术观点尽量来自原文，表达准确克制。
- [ ] 每个 Shot ID 都有对应配音或明确标记为无配音。
- [ ] 分镜配音映射只是对配音总稿做原样切分，没有摘要、改写、换词、压缩或补写。
- [ ] 去除段落空白后，所有分镜配音按 Shot ID 顺序拼接结果与配音总稿逐字一致。
- [ ] `shot-list.md` 的配音文案列与本文件同 Shot ID 配音文案逐字一致。
- [ ] 如文件已落盘，已运行 `scripts/check_narration_consistency.py --narration narration.md --shot-list shot-list.md` 或手动完成同等校验。
- [ ] 单镜头配音过长时，已经拆镜头或拆配音节拍，而不是摘要映射。
- [ ] 规划阶段未生成最终 SRT；SRT 等最终音频确认后再生成 / 校准。
