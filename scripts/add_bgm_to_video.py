from pathlib import Path
import subprocess
import json
import sys


# =========================
# 配置区
# =========================

VIDEO_PATH = Path("final_with_subtitle.mp4")
BGM_PATH = Path("materials/bgm.mp3")
OUTPUT_PATH = Path("final_with_bgm.mp4")

# 原视频声音音量，比如旁白
VOICE_VOLUME = 1.0

# BGM 音量，建议 0.12 ~ 0.25
BGM_VOLUME = 0.18

# 是否给 BGM 做淡入淡出
ENABLE_FADE = True
FADE_DURATION = 1.5


# =========================
# 工具函数
# =========================

def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if result.returncode != 0:
        print("命令执行失败：")
        print(" ".join(cmd))
        print(result.stderr)
        raise RuntimeError("FFmpeg / FFprobe 执行失败")

    return result.stdout.strip()


def check_ffmpeg_available():
    try:
        run_cmd(["ffmpeg", "-version"])
        run_cmd(["ffprobe", "-version"])
    except Exception:
        print("没有检测到 ffmpeg 或 ffprobe。")
        print("请先安装 FFmpeg，并确保命令行里可以直接运行 ffmpeg 和 ffprobe。")
        sys.exit(1)


def get_duration(path: Path) -> float:
    """
    获取视频或音频时长，单位：秒。
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]

    output = run_cmd(cmd)

    if not output:
        raise ValueError(f"无法获取时长：{path}")

    return float(output)


def has_audio_stream(video_path: Path) -> bool:
    """
    判断视频里是否已有音频流。
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "json",
        str(video_path),
    ]

    output = run_cmd(cmd)
    data = json.loads(output)

    return len(data.get("streams", [])) > 0


# =========================
# 核心逻辑
# =========================

def add_bgm():
    check_ffmpeg_available()

    if not VIDEO_PATH.exists():
        raise FileNotFoundError(f"找不到视频文件：{VIDEO_PATH}")

    if not BGM_PATH.exists():
        raise FileNotFoundError(f"找不到 BGM 文件：{BGM_PATH}")

    video_duration = get_duration(VIDEO_PATH)
    video_has_audio = has_audio_stream(VIDEO_PATH)

    print(f"视频文件：{VIDEO_PATH}")
    print(f"BGM 文件：{BGM_PATH}")
    print(f"视频时长：{video_duration:.3f} 秒")
    print(f"视频是否已有音频：{video_has_audio}")
    print(f"BGM 音量：{BGM_VOLUME}")

    fade_out_start = max(video_duration - FADE_DURATION, 0)

    if ENABLE_FADE:
        bgm_filter = (
            f"[1:a]"
            f"volume={BGM_VOLUME},"
            f"afade=t=in:st=0:d={FADE_DURATION},"
            f"afade=t=out:st={fade_out_start:.3f}:d={FADE_DURATION}"
            f"[bgm]"
        )
    else:
        bgm_filter = f"[1:a]volume={BGM_VOLUME}[bgm]"

    if video_has_audio:
        filter_complex = (
            f"[0:a]volume={VOICE_VOLUME}[voice];"
            f"{bgm_filter};"
            f"[voice][bgm]amix=inputs=2:duration=longest:dropout_transition=2[aout]"
        )
    else:
        filter_complex = (
            f"{bgm_filter};"
            f"[bgm]anull[aout]"
        )

    cmd = [
        "ffmpeg",
        "-y",

        # 输入 0：原视频
        "-i", str(VIDEO_PATH),

        # 输入 1：BGM，短了就循环
        "-stream_loop", "-1",
        "-i", str(BGM_PATH),

        "-filter_complex", filter_complex,

        # 保留原视频画面
        "-map", "0:v:0",

        # 使用混合后的音频
        "-map", "[aout]",

        # 视频不重新编码，速度快
        "-c:v", "copy",

        # 音频重新编码
        "-c:a", "aac",
        "-b:a", "192k",

        # 按视频长度截断输出
        "-t", f"{video_duration:.3f}",

        # 方便网页/平台播放
        "-movflags", "+faststart",

        str(OUTPUT_PATH),
    ]

    run_cmd(cmd)

    print("=" * 60)
    print(f"完成：{OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    add_bgm()