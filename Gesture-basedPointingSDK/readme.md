# Gesture-based Pointing SDK

手势 3D 关键点与指向射线估计 SDK。

示例代码已提供在 `gesture_pointing_demo.py` 中。

## 📁 目录结构说明

发布包已按平台打包完毕，并支持 **Python 3.10 ~ 3.13** 多版本。目录下包含核心功能库、示例代码、模型文件以及必要的底层依赖文件。

### 🐧 Linux (`linux/gpsdk/`)
- `gesture_pointing.cpython-3xx-[x86_64|aarch64]-linux-gnu.so`: 核心手势识别与射线拟合扩展库。
- `gesture_pointing_demo.py`: 集成 ROS2 发布功能的演示代码（包含 API 调用示例）。
- `gesture_recognizer.task`: 手势识别模型文件。
- *(其他 `rgbsdk` 及 `libs` 目录为底层硬件与算法依赖，请保持原样即可)*

### 🪟 Windows (`win32/gpsdk/`)
- `gesture_pointing.cp3xx-win_amd64.pyd`: 核心手势识别与射线拟合扩展库。
- `gesture_pointing_demo.py`: 集成 ROS2 发布功能的演示代码（包含 API 调用示例）。
- `gesture_recognizer.task`: 手势识别模型文件。
- *(其他 `rgbsdk`、`*.dll` 为底层硬件与 OpenCV 依赖，请保持原样即可)*

> ⚠️ **注意**：请根据您当前的 Python 环境版本（如 3.10 / 3.11 / 3.12 / 3.13）保留对应的 `.so` 或 `.pyd` 文件，多余的如需可以删除。**不要修改文件名称**。

## 🛠️ 环境依赖

在运行前，请确保安装了以下 Python 依赖：

```bash
pip install numpy opencv-python mediapipe