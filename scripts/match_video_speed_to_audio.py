from pathlib import Path
import subprocess
import re
import sys


# =========================
# 配置区
# =========================

VIDEO_DIR = Path("materials/MP4")          # 视频所在目录
AUDIO_DIR = Path("materials/MP3")          # 音频所在目录
OUTPUT_DIR = Path("materials/video_output")   # 输出目录

VIDEO_PREFIX = "video"         # video1.mp4, video2.mp4...
AUDIO_PREFIX = "audio"         # audio1.mp3, audio2.mp3...

VIDEO_EXTS = [".mp4", ".mov", ".mkv"]
AUDIO_EXTS = [".mp3", ".wav", ".m4a", ".aac"]

OUTPUT_EXT = ".mp4"

# 如果变速太夸张，给出提醒，但仍然继续处理
MIN_SPEED_FACTOR = 0.5
MAX_SPEED_FACTOR = 2.0


# =========================
# 工具函数
# =========================

def run_cmd(cmd: list[str]) -> str:
    """
    执行命令，并返回 stdout。
    """
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


def get_duration(path: Path) -> float:
    """
    使用 ffprobe 获取音频或视频时长，单位：秒。
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


def extract_number(path: Path, prefix: str) -> int | None:
    """
    从 video1.mp4 / audio1.mp3 中提取编号 1。
    只匹配指定前缀，避免误匹配其他文件。
    """
    pattern = rf"^{re.escape(prefix)}(\d+)$"
    match = re.match(pattern, path.stem, re.IGNORECASE)

    if not match:
        return None

    return int(match.group(1))


def collect_numbered_files(folder: Path, prefix: str, exts: list[str]) -> dict[int, Path]:
    """
    收集 video1/video2 或 audio1/audio2 文件，返回：
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


def check_ffmpeg_available():
    """
    检查 ffmpeg 和 ffprobe 是否可用。
    """
    try:
        run_cmd(["ffmpeg", "-version"])
        run_cmd(["ffprobe", "-version"])
    except Exception:
        print("没有检测到 ffmpeg 或 ffprobe。")
        print("请先安装 FFmpeg，并确保 ffmpeg / ffprobe 可以在命令行中直接运行。")
        sys.exit(1)


# =========================
# 核心处理函数
# =========================

def process_one_pair(number: int, video_path: Path, audio_path: Path):
    """
    处理单组 videoN + audioN：
    1. 获取视频时长
    2. 获取音频时长
    3. 计算视频变速系数
    4. 用 setpts 改变视频速度
    5. 合成目标音频
    """
    output_path = OUTPUT_DIR / f"video{number}{OUTPUT_EXT}"

    video_duration = get_duration(video_path)
    audio_duration = get_duration(audio_path)

    if video_duration <= 0:
        raise ValueError(f"视频时长异常：{video_path}")

    if audio_duration <= 0:
        raise ValueError(f"音频时长异常：{audio_path}")

    # 核心公式：
    # 目标视频时长 = 音频时长
    # setpts 系数 = 音频时长 / 原视频时长
    #
    # 比如：
    # 视频 4 秒，音频 6 秒：factor = 6 / 4 = 1.5，视频变慢
    # 视频 6 秒，音频 4 秒：factor = 4 / 6 = 0.666，视频变快
    speed_factor = audio_duration / video_duration

    print("=" * 60)
    print(f"处理编号：{number}")
    print(f"视频文件：{video_path.name}")
    print(f"音频文件：{audio_path.name}")
    print(f"视频时长：{video_duration:.3f} 秒")
    print(f"音频时长：{audio_duration:.3f} 秒")
    print(f"setpts 系数：{speed_factor:.6f}")

    if speed_factor > MAX_SPEED_FACTOR:
        print("提醒：视频会被明显放慢，画面可能拖沓。")

    if speed_factor < MIN_SPEED_FACTOR:
        print("提醒：视频会被明显加快，画面可能很赶。")

    vf = f"setpts={speed_factor:.8f}*PTS"

    cmd = [
        "ffmpeg",
        "-y",

        # 输入 0：视频
        "-i", str(video_path),

        # 输入 1：音频
        "-i", str(audio_path),

        # 只改变视频速度
        "-vf", vf,

        # 使用第一个输入的视频轨
        "-map", "0:v:0",

        # 使用第二个输入的音频轨
        "-map", "1:a:0",

        # 视频重新编码
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",

        # 音频统一编码
        "-c:a", "aac",
        "-b:a", "192k",

        # 输出时长以较短轨道结束，避免尾部异常
        "-shortest",

        str(output_path),
    ]

    run_cmd(cmd)

    final_duration = get_duration(output_path)

    print(f"输出文件：{output_path}")
    print(f"输出时长：{final_duration:.3f} 秒")


# =========================
# 主程序
# =========================

def main():
    check_ffmpeg_available()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    videos = collect_numbered_files(VIDEO_DIR, VIDEO_PREFIX, VIDEO_EXTS)
    audios = collect_numbered_files(AUDIO_DIR, AUDIO_PREFIX, AUDIO_EXTS)

    if not videos:
        print("没有找到视频文件，例如 video1.mp4、video2.mp4")
        return

    if not audios:
        print("没有找到音频文件，例如 audio1.mp3、audio2.mp3")
        return

    video_numbers = set(videos.keys())
    audio_numbers = set(audios.keys())

    common_numbers = sorted(video_numbers & audio_numbers)

    missing_audio = sorted(video_numbers - audio_numbers)
    missing_video = sorted(audio_numbers - video_numbers)

    if missing_audio:
        print(f"这些视频没有对应音频：{missing_audio}")

    if missing_video:
        print(f"这些音频没有对应视频：{missing_video}")

    if not common_numbers:
        print("没有找到任何匹配的 videoN + audioN。")
        return

    print(f"找到 {len(common_numbers)} 组匹配文件：{common_numbers}")

    for number in common_numbers:
        process_one_pair(number, videos[number], audios[number])

    print("=" * 60)
    print("全部处理完成。")
    print(f"输出目录：{OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()