# RGBSDK — 双目 RGB 鱼眼相机采集与去畸变 SDK

本 SDK 提供一套 Python 接口，用于从 USB 双目 RGB 鱼眼相机采集图像，
可选择输出**原始鱼眼图**或**去畸变（pinhole）图**，左右目同帧对齐。

`retrieve_image()` 直接返回 `numpy.ndarray`，可直接交给 OpenCV、PyTorch 等下游使用。

---

## 一、目录结构

发布包解压后目录名即为 `rgbsdk/`：

```
rgbsdk/
├── demo.py                                       # 示例脚本
├── readme.md                                     # 本文件
├── rgbsdk.cpython-312-x86_64-linux-gnu.so        # Python 扩展模块
└── libs/
    └── libUSB_Camera_API.so                      # 相机底层私有库
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
├── rgbsdk.cpython-312-x86_64-linux-gnu.so
└── libs/
    └── libUSB_Camera_API.so
```

---

## 二、运行环境

### 1. Python 版本（重要）

本 SDK 的 `.so` 是**针对具体 Python 版本编译**的，文件名里的 `cpython-312`
表示它**只能被 Python 3.12 加载**。

| 你的 Python | 能否 import |
|---|---|
| 3.12.x | ✅ 可以 |
| 3.11.x、3.10.x、3.13.x | ❌ 不行 |

检查当前 Python 版本：

```bash
python3 --version
# 期望输出：Python 3.12.x
```

如果版本不符，请联系 SDK 提供方，提供适配你 Python 版本的发布包。

### 2. 系统依赖

```bash
sudo apt update
sudo apt install -y \
    python3-opencv \        # OpenCV Python 绑定（提供 cv2 和 numpy）
    libudev1 \              # 相机 USB 设备访问
    v4l-utils               # 可选：v4l2-ctl 用于排查摄像头
```

或者，如果你使用虚拟环境，也可以用 pip 安装 Python 侧依赖：

```bash
pip install opencv-python numpy
```

> **注意**：`libUSB_Camera_API.so` 及其下游依赖已经打包在 `libs/` 里，
> 无需系统级安装。SDK 通过 RPATH `$ORIGIN/libs` 自动定位。

### 3. 硬件与权限

- 相机插在 USB 口上，识别为 `/dev/video0`（可用 `v4l2-ctl --list-devices` 确认）。
- 当前用户需要对 `/dev/video0` 有读写权限：

```bash
# 查看权限
ls -l /dev/video0

# 临时授权（重启失效）
sudo chmod 666 /dev/video0
```

持久化授权建议加 udev 规则，或把用户加入 `video` 组：

```bash
sudo usermod -aG video $USER    # 重新登录后生效
```

---

## 三、快速开始

```bash
cd rgbsdk
python3 demo.py
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
sdk.start(cam_path="/dev/video0",
          undistort=False,
          undistort_angle_h=0.0,
          undistort_angle_v=0.0,
          undistort_w=600,
          undistort_h=400,
          undistort_fxy=414.18)
```

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `cam_path` | str | `"/dev/video0"` | 相机设备节点，也是内参文件路径的定位依据 |
| `undistort` | bool | `False` | 是否对图像做鱼眼去畸变 |
| `undistort_angle_h` | float | `0.0` | 虚拟相机水平旋转角度（度），正值向右转，范围 ±45 |
| `undistort_angle_v` | float | `0.0` | 虚拟相机竖直旋转角度（度），正值低头，范围 ±45 |
| `undistort_w` | int | `600` | 去畸变输出宽度（像素） |
| `undistort_h` | int | `400` | 去畸变输出高度（像素） |
| `undistort_fxy` | float | `414.18` | 去畸变虚拟相机焦距（像素，fx = fy） |

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

- 确认你在 `rgbsdk/` 目录下运行 `python3 demo.py`；
- 确认 `.so` 文件名中的 Python 版本与当前 `python3` 一致
  （`rgbsdk.cpython-312-...so` ↔ `python3 --version` 输出 `3.12.x`）；
- 如果从其它目录运行，可以临时加 `PYTHONPATH`：
  ```bash
  PYTHONPATH=/path/to/rgbsdk python3 /path/to/your_script.py
  ```

### Q2. `ImportError: libUSB_Camera_API.so: cannot open shared object file`

- 确认 `libs/libUSB_Camera_API.so` 与 `rgbsdk*.so` 的相对位置没被破坏
  （`libs/` 必须在 `.so` 同级目录）；
- 检查 RPATH 是否生效：
  ```bash
  readelf -d rgbsdk.cpython-312-x86_64-linux-gnu.so | grep -i runpath
  # 期望：$ORIGIN/libs
  ```
- 检查依赖是否完整：
  ```bash
  ldd rgbsdk.cpython-312-x86_64-linux-gnu.so | grep -i "not found"
  ```
  有 `not found` 时，说明还缺库，请联系 SDK 提供方。

### Q3. `ImportError: undefined symbol: ...`

- 99% 是 Python 版本不匹配（比如用 3.11 的 Python 加载 3.12 的 `.so`）。
- 用 `python3 -c "import sys; print(sys.version_info)"` 确认版本。

### Q4. `grab()` 一直不返回

- 检查相机是否插好、`/dev/video0` 是否存在、权限是否足够（见「二、3. 硬件与权限」）；
- 检查是否有其它进程占用了相机（如 `cheese`、`guvcview`、之前没退出的旧进程）：
  ```bash
  sudo fuser -v /dev/video0
  ```

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
| `rgbsdk.cpython-312-x86_64-linux-gnu.so` | Python 扩展模块（Python 3.12 专用） |
| `libs/libUSB_Camera_API.so` | 相机底层 API，`.so` 通过 `$ORIGIN/libs` 自动加载 |
| `demo_output/` | 运行 `demo.py` 后自动生成的示例图像输出目录 |

---

如有问题，请提供以下信息，便于排查：

1. `python3 --version`
2. `ls -l /dev/video*`
3. `readelf -d rgbsdk*.so | grep -i runpath`
4. `ldd rgbsdk*.so | grep "not found"`
5. 完整报错信息