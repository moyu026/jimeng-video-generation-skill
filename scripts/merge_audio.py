from pathlib import Path
import re
import subprocess

audio_dir = Path("materials")
output_file = "merge.mp3"
list_file = "audio_list.txt"

def natural_key(path: Path):
    """
    让 audio2 排在 audio10 前面。
    普通 sorted 会变成 audio1, audio10, audio2。
    """
    return [
        int(text) if text.isdigit() else text
        for text in re.split(r"(\d+)", path.stem)
    ]

audio_files = sorted(audio_dir.glob("audio*.mp3"), key=natural_key)

if not audio_files:
    raise FileNotFoundError("没有找到 audio*.mp3 文件")

with open(list_file, "w", encoding="utf-8") as f:
    for audio in audio_files:
        f.write(f"file '{audio.as_posix()}'\n")

cmd = [
    "ffmpeg",
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", list_file,
    "-c", "copy",
    output_file,
]

subprocess.run(cmd, check=True)

print("拼接完成：", output_file)
print("拼接顺序：")
for audio in audio_files:
    print(audio.name)