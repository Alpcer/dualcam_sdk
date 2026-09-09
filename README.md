# ROS2 Depth Camera (Docker Deployment Guide)

本仓库提供基于 Docker 容器部署的 ROS2 双目/深度相机节点安装与运行指南。

---

## 📋 目录

- [1. 环境准备](#1-环境准备)
- [2. 加载与启动 Docker 容器](#2-加载与启动-docker-容器)
- [3. 生成 TensorRT Engine 模型文件](#3-生成-tensorrt-engine-模型文件)
- [4. 运行节点与参数配置](#4-运行节点与参数配置)

---

## 1. 环境准备

在开始使用前，请确保宿主机已配置好以下驱动与基础软件库：

* **NVIDIA 显卡驱动**（适用于 RTX 系列显卡）
* **CUDA 工具包**
* **Docker** 以及 **NVIDIA Container Toolkit**（确保容器可顺利调用 GPU）
* **ROS 2 环境**（须与宿主机系统相匹配，例如 Ubuntu 20.04对应ROS2 Foxy）
  * 详细文档：[ROS Foxy 安装指南](https://docs.ros.org/en/foxy/Installation/Ubuntu-Install-Debians.html)
  * 推荐安装完整桌面版（`desktop-full`）

---

## 2. 加载与启动 Docker 容器

### 2.1 导入镜像

在宿主机终端中执行命令导入镜像文件：

```bash
docker load -i depth_camera_2.0.tar
```

### 2.2 启动容器

运行以下命令启动容器并映射设备：

```bash
docker run --gpus all -it --network host --device=/dev/video0:/dev/video0 --entrypoint /bin/bash depth_camera:v2.0
```

> **💡 注意：**
> 请将 `--device=/dev/video0:/dev/video0` 中的 `/dev/video0` 修改为你宿主机上实际连接的相机设备路径。

---

## 3. 生成 TensorRT Engine 模型文件

### 3.1 传输 ONNX 模型至容器

1. 打开宿主机的另一个终端，获取当前运行中的容器 ID：

   ```bash
   docker ps
   ```

2. 将宿主机的 ONNX 模型文件拷贝入容器内部（例如存放至 `/root/`）：

   ```bash
   docker cp /path_to_local_fisheye.onnx <CONTAINER_ID>:/root/fisheye.onnx
   docker cp /path_to_local_pin.onnx <CONTAINER_ID>:/root/pin.onnx
   ```

### 3.2 转换 Engine 模型

在**容器内的终端**中进行转换：

1. 编辑转换脚本：

   ```bash
   vi /ros2_ws/convert.py
   ```

2. 将脚本内的 `onnx_file` 与 `engine_file` 变量修改为你实际对应的文件路径。

3. 执行转换脚本：

   ```bash
   python3 convert.py
   ```

> **⚠️ 说明：**
> 需要分别针对 `fisheye.onnx` 和 `pin.onnx` 修改路径并执行两次转换，最终在容器内生成对应的 `fisheye.engine` 与 `pin.engine` 文件。

---

## 4. 运行节点与参数配置

### 4.1 启动 ROS2 节点

在**容器内的终端**中，加载环境变量并启动深度相机节点：

```bash
source /ros2_ws/install/setup.bash

ros2 run depth_camera depth_camera_node --ros-args \
  -p undistort:=false \
  -p colormap:=true \
  -p pointcloud:=false \
  -p engine_fisheye_path:=/root/fisheye.engine \
  -p engine_pin_path:=/root/pin.engine \
  -p cam_path:=/dev/video0
```

> **提示：** 运行过程中按下 `Ctrl + C` 即可安全终止程序。

### 4.2 参数说明

| 参数名称 | 类型 | 默认值 | 详细说明 |
| :--- | :--- | :--- | :--- |
| `undistort` | `bool` | `false` | 去畸变功能开关 |
| `colormap` | `bool` | `true` | 是否将原始深度数据转换为彩色可视化图像 |
| `pointcloud` | `bool` | `false` | 点云输出开关。开启后仅发送点云，不再发送图像数据 |
| `engine_fisheye_path` | `string` | - | 容器内生成的 `fisheye.engine` 文件绝对路径 |
| `engine_pin_path` | `string` | - | 容器内生成的 `pin.engine` 文件绝对路径 |
| `cam_path` | `string` | `/dev/video0` | 挂载到容器内的相机设备节点路径 |
