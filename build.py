import os
import subprocess
from pathlib import Path


def convert_icon():
    """将logo.png转换为.ico格式"""
    if not Path("logo.ico").exists():
        try:
            # 首先尝试使用ImageMagick
            cmd = f"magick convert logo.png -define icon:auto-resize=256,128,64,48,32,16 logo.ico"
            subprocess.run(cmd, shell=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 回退到Pillow实现
            from PIL import Image

            img = Image.open("logo.png")
            img.save(
                "logo.ico",
                sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
            )


def build_executable():
    """使用PyInstaller打包应用"""
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=logo.ico",
        "--name=Sultan Saver",
        "--add-data=logo.ico;.",
        "main.py",
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"错误码: {e.returncode}")
        print(f"标准输出: {e.stdout}")
        print(f"错误输出: {e.stderr}")
        raise


if __name__ == "__main__":
    convert_icon()
    build_executable()
    print("构建完成！可执行文件在dist目录下")
