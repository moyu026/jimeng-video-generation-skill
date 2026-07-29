# Environment 模块

## 目标

在任何规划或生产前确认本机能执行完整工作流；缺失依赖时先配置并复检。

## 检查

运行：

```bash
python scripts/check_environment.py
```

默认必需项：

- Python 3.10+
- `ffmpeg`
- `ffprobe`
- `whisper` CLI
- Python 包 `Pillow`

需要调用即梦 CLI（命令名 `dreamina`）时附加：

```bash
python scripts/check_environment.py --require-jimeng
```

需要 HTML 录屏时附加：

- 确认 `E:\pythonwork\0.study\jimeng-video-generation-skill\scripts\record_html_with_ffmpeg.py` 存在。
- 确认 Chrome 路径存在；`record_html_with_ffmpeg.py` 直接调用系统 PATH 中的 `ffmpeg`，不使用私有或内置 ffmpeg 路径。

```bash
python scripts/check_environment.py --require-browser
```

## 配置规则

1. Python 包缺失时，在当前 Python 环境运行 `python -m pip install -r requirements.txt`。
2. FFmpeg / ffprobe 缺失时，使用当前系统包管理器安装 FFmpeg，并把其 `bin` 目录加入 PATH。
3. Whisper 安装后必须验证 `whisper --help`；只安装包但命令不可见时，修复当前 Python Scripts 目录的 PATH。
4. 即梦 CLI 缺失或认证失败时，按实际 CLI 文档安装并配置认证；命令名为 `dreamina`，不要伪造命令或结果。
5. 浏览器只在 HTML 录屏阶段需要。
6. 安装系统软件、联网下载、修改系统 PATH 或认证信息前，遵循宿主环境的授权要求。
7. 配置完成后重新运行检查，退出码必须为 0。

## 完成标准

- 检查脚本输出 `Environment check passed.`。
- 所有当前任务需要的命令和 Python 包均可用。
- 仍缺失的项目有明确配置建议；未满足时不进入后续阶段。
