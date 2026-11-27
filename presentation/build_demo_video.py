"""Build the backup MP4 from the actual browser and model evidence captures."""
import argparse
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
FRAMES = HERE.parent / ".runtime/course-final/video-frames"
SEQUENCE = [
    ("00-dashboard", "启动仪表盘 · FastAPI 与 SQLite 均已连接", 4),
    ("01-project", "F01  同名文件两次导入，保留缺陷版与修复版", 6),
    ("02-ast", "F02  AST 解析定位 magnitude 函数及源码行号", 6),
    ("03-suite", "F03  使用模板生成测试并触发真实 WASI 首跑", 6),
    ("04-execution", "F04  定位失败节点，保留运行日志与文件版本", 6),
    ("05-regression", "F05  在修复版运行原套件和原失败节点，缺陷解决", 7),
    ("06-quality", "F06  查看修复后报告，并核对下载的 JSON", 6),
    ("07-mutation", "F13  固定清单逐项执行，示例杀死 1 / 1", 6),
    ("08-model", "PHASE-06  本机 27B 模型实际健康响应的归档回放", 6),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/msyh.ttc"))
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    font = ImageFont.truetype(str(args.font), 32)
    FRAMES.mkdir(parents=True, exist_ok=True)
    frames = []
    for index, (name, caption, duration) in enumerate(SEQUENCE):
        source = HERE / "screenshots" / (name + ".png")
        with Image.open(source) as screenshot:
            resized = ImageOps.contain(screenshot.convert("RGB"), (1360, 808))
        frame = Image.new("RGB", (1440, 900), "#102B3D")
        frame.paste(resized, ((1440 - resized.width) // 2, (808 - resized.height) // 2))
        draw = ImageDraw.Draw(frame)
        draw.line((40, 820, 1400, 820), fill="#76DBBF", width=2)
        draw.text((40, 846), caption, font=font, fill="#F2F7F8")
        name = f"{index:02d}.png"
        frame.save(FRAMES / name)
        frames.extend([f"file '{name}'", f"duration {duration}"])
    frames.append(f"file '{name}'")
    manifest = FRAMES / "frames.ffconcat"
    manifest.write_text("ffconcat version 1.0\n" + "\n".join(frames) + "\n", encoding="utf-8")
    subprocess.run([args.ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(manifest), "-vf", "fps=25", "-c:v", "libx264", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(HERE / "TestPilot_AI_备用演示.mp4")], check=True)


if __name__ == "__main__":
    main()
