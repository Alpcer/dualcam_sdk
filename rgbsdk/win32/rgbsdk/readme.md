# RGBSDK — 双目 RGB 鱼眼相机采集与去畸变 SDK (Windows)

本 SDK 提供一套 Python 接口，用于从 USB 双目 RGB 鱼眼相机采集图像，
可选择输出**原始鱼眼图**或**去畸变（pinhole）图**，左右目同帧对齐。

`retrieve_image()` 直接返回 `numpy.ndarray`，可直接交给 OpenCV、PyTorch 等下游使用。

---

## 一、目录结构

发布包解压后目录名即为 `rgbsdk/`：

```
rgbsdk/
├── demo.py                          # 示例脚本
├── readme.md                        # 本文件
├── rgbsdk.cp310-win_amd64.pyd       # Python 3.10 扩展模块
├── rgbsdk.cp311-win_amd64.pyd       # Python 3.11 扩展模块
├── rgbsdk.cp312-win_amd64.pyd       # Python 3.12 扩展模块
├── rgbsdk.cp313-win_amd64.pyd       # Python 3.13 扩展模块
├── USB_CAMERA_API_X64.dll           # 相机底层私有库
├── opencv_core4.dll                 # OpenCV 运行时依赖
├── opencv_imgproc4.dll
├── ...（其它 OpenCV 模块及第三方依赖）
└── ...
```

> 只要保持上述相对位置不变，整个文件夹可以任意拷贝到其它机器。

运行 `demo.py` 后，会在**当前工作目录**下自动生成 `demo_output/` 用于保存示例图像：

```
rgbsdk/
├── demo.py
├── demo_output/              ← 运行后生成
│   ├── left_1.jpg
│   ├── left_2.jpg ...
│   └── right_1.jpg ...
├── readme.md
├── rgbsdk.cp312-win_amd64.pyd
├── USB_CAMERA_API_X64.dll
└── ...（其它 .dll）
```

---

## 二、运行环境

### 1. Python 版本（重要）

本 SDK 的 `.pyd` 是**针对具体 Python 版本编译**的，文件名里的 `cp3XX` 表示
它**只能被对应版本的 Python 加载**：

| 你的 Python (64 位) | 对应加载的 .pyd |
|---|---|
| 3.10.x | `rgbsdk.cp310-win_amd64.pyd` |
| 3.11.x | `rgbsdk.cp311-win_amd64.pyd` |
| 3.12.x | `rgbsdk.cp312-win_amd64.pyd` |
| 3.13.x | `rgbsdk.cp313-win_amd64.pyd` |

**必须是 64 位 Python**。32 位 Python 无法加载这些 `.pyd`。

检查当前 Python 版本和位数：

```cmd
python -c "import sys, struct; print(sys.version); print('bits:', struct.calcsize('P')*8)"
```

期望输出类似：

```
3.12.x (...)
bits: 64
```

### 2. Python 安装

从 [python.org](https://www.python.org/downloads/windows/) 下载对应版本的
**Windows installer (64-bit)**，安装时勾选：

- **Add python.exe to PATH**
- **Install for all users**（可选，推荐）

> ⚠️ **不要用 embeddable package**，那个版本没有 pip 和完整的标准库，
> 无法正常使用本 SDK。

### 3. 相机驱动

相机通过 **Windows 自带的 Media Foundation / UVC 驱动** 访问，通常**无需额外安装驱动**。
插入后可在「设备管理器 → 照相机 / 图像设备」中看到。

### 4. Python 侧依赖

`demo.py` 依赖 `opencv-python`（提供 `cv2`）和 `numpy`：

```cmd
python -m pip install opencv-python numpy
```

如果 32 位环境装不上最新的 `opencv-python`（本 SDK 是 64 位，一般不会遇到），
可以指定版本：

```cmd
python -m pip install "opencv-python==4.5.5.64" numpy
```

---

## 三、快速开始

```cmd
cd rgbsdk
python demo.py
```

或者显式指定 Python 路径（多版本共存时推荐）：

```cmd
"C:\Python312\python.exe" demo.py
```

`demo.py` 会采集 10 帧原始鱼眼图，左右目分别保存到当前目录下的 `demo_output/`：

```
demo_output/
├── left_10.jpg   left_9.jpg ... left_1.jpg
└── right_10.jpg  right_9.jpg ... right_1.jpg
```

该文件夹由脚本**自动创建**，无需手动 `mkdir`。
如果想改保存位置，编辑 `demo.py` 里的 `out_dir` 变量即可。

---

## 四、Python API 说明

### 4.1 导入

```python
import rgbsdk
```

### 4.2 常量：图像类型

| 常量 | 值 | 含义 |
|---|---|---|
| `rgbsdk.IMAGE_FISHEYE_LEFT`  | 0 | 左目原始鱼眼图 |
| `rgbsdk.IMAGE_FISHEYE_RIGHT` | 1 | 右目原始鱼眼图 |
| `rgbsdk.IMAGE_PIN_LEFT`      | 2 | 左目去畸变图（针孔模型） |
| `rgbsdk.IMAGE_PIN_RIGHT`     | 3 | 右目去畸变图（针孔模型） |

> 只有 `start(..., undistort=True)` 时，`IMAGE_PIN_*` 才有数据；
> 否则 `retrieve_image(IMAGE_PIN_*)` 返回空数组。

### 4.3 `RgbSDK()`

构造函数，无参数。

```python
sdk = rgbsdk.RgbSDK()
```

> ⚠️ **同一进程内只允许创建一个实例**。SDK 内部使用全局状态，
> 多实例会相互干扰。

### 4.4 `sdk.start(...)`

启动采集 / 解码 / 去畸变后台线程。**非阻塞**，立即返回。

```python
sdk.start(cam_path="0",
          undistort=False,
          undistort_angle_h=0.0,
          undistort_angle_v=0.0,
          undistort_w=600,
          undistort_h=400,
          undistort_fxy=414.18)
```

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `cam_path` | str | `"0"` | 相机索引（"0" 表示第一台 MF 枚举到的相机） |
| `undistort` | bool | `False` | 是否对图像做鱼眼去畸变 |
| `undistort_angle_h` | float | `0.0` | 虚拟相机水平旋转角度（度），正值向右转，范围 ±45 |
| `undistort_angle_v` | float | `0.0` | 虚拟相机竖直旋转角度（度），正值低头，范围 ±45 |
| `undistort_w` | int | `600` | 去畸变输出宽度（像素） |
| `undistort_h` | int | `400` | 去畸变输出高度（像素） |
| `undistort_fxy` | float | `414.18` | 去畸变虚拟相机焦距（像素，fx = fy） |

> **`cam_path` 说明**：Windows 版用 **Media Foundation 枚举索引**，
> `"0"` 表示第一台相机，`"1"` 表示第二台，以此类推。
> 与 Linux 版的 `/dev/video0` 用法不同，请勿混用。

**参数说明与建议**

- `undistort=False`：只输出原始鱼眼图，速度最快。
- `undistort=True`：后台线程同步处理左右目去畸变，`grab()` 返回时左右目
  同帧已对齐，可直接做立体匹配。
- `undistort_fxy` 越大，视野越窄（放大），越小视野越宽（缩小）。
- `undistort_angle_h/v` 相当于虚拟云台，用于调整去畸变后的朝向。

> **提示**：`start()` 返回后即可调用 `get_intrinsics()` 读取当前生效的内参。
> 若在 `start()` 之前调用，会得到未初始化的默认值（单位矩阵 / 零畸变）。

### 4.5 `sdk.grab()`

**阻塞**等待左右目同帧就绪。返回 `bool`。

```python
ok = sdk.grab()
```

- 返回 `True`：有新的同步帧可用，可以调用 `retrieve_image()`。
- 返回 `False`：SDK 已停止（调用了 `stop()` 或相机断开）。

**典型用法**：

```python
while sdk.grab():
    left  = sdk.retrieve_image(rgbsdk.IMAGE_FISHEYE_LEFT)
    right = sdk.retrieve_image(rgbsdk.IMAGE_FISHEYE_RIGHT)
    # 处理 left/right ...
```

### 4.6 `sdk.retrieve_image(image_type)`

获取指定类型的图像，返回 `numpy.ndarray`，`dtype=uint8`。

```python
left  = sdk.retrieve_image(rgbsdk.IMAGE_FISHEYE_LEFT)
right = sdk.retrieve_image(rgbsdk.IMAGE_FISHEYE_RIGHT)
```

| 返回情况 | shape | 说明 |
|---|---|---|
| 彩色图 | `(H, W, 3)` | 通道顺序为 **BGR**（OpenCV 默认），可直接 `cv2.imwrite` |
| 灰度图 | `(H, W)` | — |
| 无数据 | shape 中含 0 | 例如 `undistort=False` 时取 `IMAGE_PIN_*` |

返回值是**内部缓存的拷贝**，可以放心长期持有，不会随下一帧 `grab()` 被覆盖。

### 4.7 `sdk.get_intrinsics(image_type)`

获取与 `retrieve_image(image_type)` 返回图像**一一对应**的内参，返回一个元组
`(K, D)`，可直接喂给 `cv2.undistort` / `cv2.fisheye.undistortImage` /
`cv2.stereoRectify` 等。

```python
K, D = sdk.get_intrinsics(rgbsdk.IMAGE_FISHEYE_LEFT)
```

### 4.8 `sdk.stop()`

停止所有后台线程并释放资源。可在 `grab()` 阻塞期间从另一个线程调用，
`grab()` 会立刻返回 `False`。

```python
sdk.stop()
```

一般无需显式调用——`RgbSDK` 析构时（程序退出、`del sdk`）会自动 `stop()`。

---

## 五、常见问题

### Q1. `ModuleNotFoundError: No module named 'rgbsdk'`

- 确认你在 `rgbsdk/` 目录下运行 `python demo.py`；
- 确认 `.pyd` 文件名中的 Python 版本与当前 `python` 一致
  （`rgbsdk.cp312-win_amd64.pyd` ↔ `python --version` 输出 `3.12.x`）；
- 如果从其它目录运行，可以临时加 `PYTHONPATH`：
  ```cmd
  set PYTHONPATH=E:\path\to\rgbsdk
  python your_script.py
  ```

### Q2. `ImportError: DLL load failed while importing rgbsdk: 找不到指定的模块。`

这是 Windows 上最常见的报错，原因是 `.pyd` 依赖的某个 `.dll` 没有被找到。

可能原因与排查：

1. **某个 DLL 缺失**：确认 `USB_CAMERA_API_X64.dll`、`opencv_*.dll`、
   以及其它随包提供的所有 `.dll` 都在 `.pyd` 同一目录下；
2. **位数不匹配**：用 32 位 Python 加载 64 位 `.pyd`（或反之）。
   用 `python -c "import struct; print(struct.calcsize('P')*8)"` 确认输出是 `64`；
3. **MSVC 运行库缺失**（少见）：
   下载安装 [Microsoft Visual C++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)，
   或者把 Python 安装目录下的 `vcruntime140.dll` / `vcruntime140_1.dll` / `msvcp140.dll`
   拷到 `rgbsdk/` 目录。

排查工具：用 [Dependencies.exe](https://github.com/lucasg/Dependencies/releases)
打开 `.pyd`，红标的 DLL 就是缺失的。

### Q3. `ImportError: dynamic module does not define module export function` 或 `undefined symbol`

- 99% 是 Python 版本不匹配（比如用 3.11 的 Python 加载 `cp312` 的 `.pyd`）。
- 用 `python -c "import sys; print(sys.version_info)"` 确认版本。

### Q4. `grab()` 一直不返回

- 检查相机是否插好，设备管理器中是否能看到；
- 检查相机是否被其它程序占用（Windows 相机应用、OBS、Zoom、Teams 等）；
- 关闭所有可能占用相机的程序后重试。

### Q5. 运行一段时间后报错 / 图像卡住

- 本 SDK 内部队列长度为 1，如果下游处理太慢会丢帧，这是设计行为；
- 如果希望「不丢帧、处理后端阻塞」，需自行在 Python 侧增加处理线程。

### Q6. 想同时跑多个相机

- 当前实现**不支持**——进程内的状态是全局的。
- 需要多相机时，请用 `multiprocessing` 为每个相机起独立进程。

### Q7. 图像保存失败（`cv2.imwrite` 返回 False）

- 目标文件夹不可写：确认 `demo_output/` 所在目录对当前用户有写权限；
- 文件名含非法字符：默认文件名是 `left_N.jpg`，一般不会出问题；
- 磁盘空间不足。

### Q8. `get_intrinsics()` 返回单位矩阵 / 全 0 畸变？

- 说明在 `start()` 之前调用了。`start()` 内部才会读相机 Flash 里的内参并
  计算 ROI 裁剪、去畸变虚拟相机 K，请确保调用顺序是：
  ```python
  sdk = rgbsdk.RgbSDK()
  sdk.start(...)                 # ← 先 start
  K, D = sdk.get_intrinsics(...) # ← 再取内参
  ```

---

## 六、性能参考

单机（x86_64，8 核）实测，仅供参考：

| 配置 | 帧率 |
|---|---|
| `undistort=False`，只出原始鱼眼图 | ~60 Hz |
| `undistort=True`，640×480 去畸变 | ~30–60 Hz（取决于 CPU 与 omp 线程数） |

去畸变耗时与输出分辨率、CPU 核数有关，多核机器会自动并行。

---

## 七、文件清单

| 文件 | 说明 |
|---|---|
| `demo.py` | 示例脚本 |
| `readme.md` | 本说明 |
| `rgbsdk.cpXXX-win_amd64.pyd` | Python 扩展模块（按 Python 版本区分，保留所需版本即可） |
| `USB_CAMERA_API_X64.dll` | 相机底层 API |
| `opencv_*.dll` 等 | OpenCV 及第三方运行时依赖 |
| `demo_output/` | 运行 `demo.py` 后自动生成的示例图像输出目录 |

---

如有问题，请提供以下信息，便于排查：

1. `python -c "import sys, struct; print(sys.version); print('bits:', struct.calcsize('P')*8)"`
2. 设备管理器 → 照相机 / 图像设备中相机设备的名称
3. `rgbsdk/` 目录的完整文件列表（`dir /b` 输出）
4. 完整报错信息