# Jimeng CLI 模块

## 何时读取

当用户明确要求调用即梦 CLI 生成 AI 视频，或在 Checkpoint Plan 后确认进入 AI 视频素材生产时读取。

## 输入

- `shot-list.md` 中素材类型为 AI 视频 / Jimeng 的镜头
- 用户确认后的 Prompt、时长、比例、风格
- 可用的即梦 CLI 环境与认证信息

## 输出

```text
assets/jimeng/<shot-id>.mp4
asset-manifest.md 更新项
```

## 工作步骤

1. 从 `shot-list.md` 筛选 AI 视频镜头。
2. 对每个镜头确认 Prompt 是否包含镜头时长、时间轴、运动、结尾状态、风格和禁止内容。
3. 调用或生成即梦 CLI 任务。若当前环境没有即梦 CLI，输出明确的待执行命令 / 任务清单。
4. 生成结果保存到 `assets/jimeng/`。
5. 将路径、时长、状态、失败原因写回 `asset-manifest.md`。

## 完成标准

- 每个 AI 视频镜头都有生成结果或明确失败说明。
- 生成文件路径写入 `asset-manifest.md`。
- 失败镜头有 retry / fallback 建议。

## 失败 / 退化路径

- CLI 不存在：说明缺少工具，输出待执行任务清单，不假装生成成功。
- 认证失败：提示用户配置认证。
- 单镜头失败：记录失败原因，允许重试或改为后期包装 / HTML 图解。

## 自检清单

- [ ] 是否只处理 AI 视频镜头？
- [ ] 是否没有把产品 UI、Logo、代码、字幕交给 AI 生成？
- [ ] 是否更新了 `asset-manifest.md`？
- [ ] 是否保留失败记录？
