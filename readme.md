# Dualcam SDK

本项目是一个基于 USB 双目鱼眼相机的综合 SDK 集合，提供从**底层 RGB 图像采集**、**手势 3D 交互**，到**ROS2 深度相机与点云部署**的全链路支持。

本仓库按功能划分为三个独立的子模块，请根据你的业务需求选择对应的目录：

---

## 📦 模块说明

### 1. [Gesture-based Pointing SDK](./Gesture-basedPointingSDK)
用于实时检测手部 21 个 3D 关键点，并估计食指的指向射线。
- **核心功能**：高精度 3D 关键点输出、防抖射线拟合、支持 ROS2 发布。
- **适用场景**：人机交互、手势控制、空间指向识别。
- **运行环境**：Python 3.10 ~ 3.13（支持 Linux / Windows）。

### 2. [RGBSDK (Python 原生采集)](./rgbsdk)
轻量级的相机 RGB 图像采集与处理 SDK，直接返回 `numpy` 数组。
- **核心功能**：极低延迟的双目原图/去畸变图采集、内外参获取、双目标定对齐。
- **适用场景**：需要自己编写 CV 算法、非 ROS 环境的 Python 应用。
- **运行环境**：Python 3.10 ~ 3.13（Linux）。

### 3. [RGBDSdk (ROS2 深度相机与点云)](./RGBDSdk)
基于 Docker 容器化的一体化 ROS2 节点，提供深度图与点云生成。
- **核心功能**：使用 TensorRT 加速，直接输出双目图像、深度图以及 3D 点云数据。
- **适用场景**：ROS2 机器人开发、建图导航、快速部署。
- **运行环境**：Docker, ROS2, CUDA, NVIDIA 显卡。

---

## 🚀 快速导航

每个子目录中都包含了**独立的详细说明文档 (`readme.md`) 和示例代码**。请直接点击上方对应模块的链接，或进入对应文件夹查看。

### 目录树预览
```text
dualcam_sdk/
├── Gesture-basedPointingSDK/   # 手势 3D 关键点与指向射线 SDK
├── rgbsdk/                     # 基础双目相机 Python 采集 SDK
└── RGBDSdk/                    # ROS2 Docker 节点与深度/点云输出