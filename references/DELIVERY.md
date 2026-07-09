# Delivery 模块

## 何时读取

当素材、音频、字幕基本完成，需要整理给剪辑或交付时读取。

## 输入

- `shot-list.md`
- `asset-manifest.md`
- `narration.md`
- `subtitles/subtitles.srt`
- 所有生成或复用的素材文件

## 输出

```text
asset-manifest.md
edit-guide.md
```

## 工作步骤

1. 汇总所有素材：即梦视频、HTML 录屏、原始视频 / 图片、配音音频、字幕。
2. 检查每个镜头是否有可用素材。
3. 更新 `asset-manifest.md`：资产 ID、类型、路径、来源模块、状态、时长、备注。
4. 编写 `edit-guide.md`：剪辑顺序、转场、标题、字幕、箭头、框选、Logo、UI 标签、导出建议。
5. 标记缺失或需人工处理的资产。

## 完成标准

- 剪辑人员只看 `asset-manifest.md` 和 `edit-guide.md` 就能接手。
- 每个镜头有素材路径或缺失说明。
- 后期文字、字幕、Logo、箭头、框选位置说明清楚。

## 失败 / 退化路径

- 素材缺失：标记为 `missing`，说明补救方案。
- 时长未知：标记 `duration: TBD`。
- 剪辑顺序不确定：回到 `shot-list.md` 让用户确认。

## 自检清单

- [ ] 每个镜头是否有素材或缺失说明？
- [ ] 配音和字幕路径是否登记？
- [ ] 后期包装要求是否明确？
- [ ] 是否列出最终导出建议？
