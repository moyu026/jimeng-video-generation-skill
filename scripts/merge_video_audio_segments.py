from pathlib import Path
import subprocess
import re
import json
import sys


# =========================
# 配置区
# =========================

VIDEO_DIR = Path("materials/video_output")     # video1.mp4, video2.mp4 所在目录
AUDIO_DIR = Path("materials/MP3")              # audio1.mp3, audio2.mp3 所在目录

TEMP_DIR = Path("materials/output/temp_segments")   # 临时片段目录
OUTPUT_DIR = Path("materials/output")       # 最终输出目录
FINAL_OUTPUT = OUTPUT_DIR / "final_video.mp4"

VIDEO_PREFIX = "video"
AUDIO_PREFIX = "audio"

VIDEO_EXTS = [".mp4", ".mov", ".mkv"]
AUDIO_EXTS = [".mp3", ".wav", ".m4a", ".aac"]

TARGET_FPS = 30
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2

# 如果为 None，会自动使用第一个视频的宽高
TARGET_WIDTH = None
TARGET_HEIGHT = None


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
        raise RuntimeError("FFmpeg 执行失败")

    return result.stdout.strip()


def check_ffmpeg_available():
    try:
        run_cmd(["ffmpeg", "-version"])
        run_cmd(["ffprobe", "-version"])
    except Exception:
        print("没有检测到 ffmpeg 或 ffprobe。")
        print("请先安装 FFmpeg，并确保命令行里可以直接运行 ffmpeg 和 ffprobe。")
        sys.exit(1)


def extract_number(path: Path, prefix: str) -> int | None:
    """
    从 video1.mp4 / audio1.mp3 中提取编号 1。
    """
    pattern = rf"^{re.escape(prefix)}(\d+)$"
    match = re.match(pattern, path.stem, re.IGNORECASE)

    if not match:
        return None

    return int(match.group(1))


def collect_numbered_files(folder: Path, prefix: str, exts: list[str]) -> dict[int, Path]:
    """
    收集 video1、video2 或 audio1、audio2。
    返回：
    {
        1: Path("video1.mp4"),
        2: Path("video2.mp4")
    }
    """
    files: dict[int, Path] = {}

    for ext in exts:
        for path in folder.glob(f"{prefix}*{ext}"):
            number = extract_number(path, prefix)

            if number is None:
                continue

            if number in files:
                raise ValueError(
                    f"编号重复：{number}\n"
                    f"已存在：{files[number]}\n"
                    f"重复文件：{path}"
                )

            files[number] = path

    return files


def get_video_size(video_path: Path) -> tuple[int, int]:
    """
    获取视频宽高。
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(video_path),
    ]

    output = run_cmd(cmd)
    data = json.loads(output)

    streams = data.get("streams", [])
    if not streams:
        raise ValueError(f"没有找到视频流：{video_path}")

    width = int(streams[0]["width"])
    height = int(streams[0]["height"])

    return width, height


def safe_concat_file_line(path: Path) -> str:
    """
    生成 concat list 里的 file 行。
    因为 concat_list.txt 放在 TEMP_DIR 内，所以这里使用文件名即可。
    """
    return f"file '{path.name}'"


# =========================
# 核心处理函数
# =========================

def create_segment(
    number: int,
    video_path: Path,
    audio_path: Path,
    target_width: int,
    target_height: int,
) -> Path:
    """
    把 videoN + audioN 合成 segmentN.mp4。
    同时统一：
    - 分辨率
    - 帧率
    - 视频编码
    - 音频编码
    """
    segment_path = TEMP_DIR / f"segment{number:03d}.mp4"

    vf = (
        f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,"
        f"fps={TARGET_FPS},"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg",
        "-y",

        # 输入 0：视频
        "-i", str(video_path),

        # 输入 1：音频
        "-i", str(audio_path),

        # 统一画面参数
        "-vf", vf,

        # 取第一个输入的视频轨
        "-map", "0:v:0",

        # 取第二个输入的音频轨
        "-map", "1:a:0",

        # 视频编码
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",

        # 音频编码
        "-c:a", "aac",
        "-ar", str(AUDIO_SAMPLE_RATE),
        "-ac", str(AUDIO_CHANNELS),
        "-b:a", "192k",

        # 以较短轨道结束，避免尾部黑屏或静音
        "-shortest",

        str(segment_path),
    ]

    print("=" * 60)
    print(f"合成片段：video{number} + audio{number}")
    print(f"视频：{video_path.name}")
    print(f"音频：{audio_path.name}")
    print(f"输出：{segment_path}")

    run_cmd(cmd)

    return segment_path


def concat_segments(segment_paths: list[Path]):
    """
    按顺序拼接所有 segment。
    """
    concat_list = TEMP_DIR / "concat_list.txt"

    lines = [safe_concat_file_line(path) for path in segment_paths]
    concat_list.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(FINAL_OUTPUT),
    ]

    print("=" * 60)
    print("开始拼接所有片段：")
    for path in segment_paths:
        print(path.name)

    run_cmd(cmd)

    print("=" * 60)
    print(f"完整视频已生成：{FINAL_OUTPUT.resolve()}")


# =========================
# 主程序
# =========================

def main():
    check_ffmpeg_available()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    videos = collect_numbered_files(VIDEO_DIR, VIDEO_PREFIX, VIDEO_EXTS)
    audios = collect_numbered_files(AUDIO_DIR, AUDIO_PREFIX, AUDIO_EXTS)

    if not videos:
        print("没有找到视频文件，例如 video1.mp4、video2.mp4")
        return

    if not audios:
        print("没有找到音频文件，例如 audio1.mp3、audio2.mp3")
        return

    common_numbers = sorted(set(videos.keys()) & set(audios.keys()))

    missing_audio = sorted(set(videos.keys()) - set(audios.keys()))
    missing_video = sorted(set(audios.keys()) - set(videos.keys()))

    if missing_audio:
        print(f"这些视频没有对应音频：{missing_audio}")

    if missing_video:
        print(f"这些音频没有对应视频：{missing_video}")

    if not common_numbers:
        print("没有找到任何匹配的 videoN + audioN。")
        return

    print(f"找到 {len(common_numbers)} 组匹配文件：{common_numbers}")

    # 自动使用第一个视频的分辨率作为最终分辨率
    first_video = videos[common_numbers[0]]

    if TARGET_WIDTH is None or TARGET_HEIGHT is None:
        target_width, target_height = get_video_size(first_video)
    else:
        target_width, target_height = TARGET_WIDTH, TARGET_HEIGHT

    print(f"最终视频分辨率：{target_width}x{target_height}")
    print(f"最终视频帧率：{TARGET_FPS} fps")

    segment_paths = []

    for number in common_numbers:
        segment_path = create_segment(
            number=number,
            video_path=videos[number],
            audio_path=audios[number],
            target_width=target_width,
            target_height=target_height,
        )
        segment_paths.append(segment_path)

    concat_segments(segment_paths)


if __name__ == "__main__":
    main()