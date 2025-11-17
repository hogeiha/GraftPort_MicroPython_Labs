# 可调式方波信号发生装置（基于 GraftPort-RP2040 开发板）

![](docs/T4B8bji9Yo9RQ9xfphAc4308nIh.png)

![](docs/CmiGbeIowoFy7pxa3l1c4qVVnIh.gif)
# 目录
- [1. 简介](#1简介)
- [2. 主要功能](#2主要功能)
- [3. 硬件要求](#3硬件要求)
- [4. 软件环境](#4软件环境)
- [5. 文件结构](#5文件结构)
- [6. 关键文件说明](#6关键文件说明)
- [7. 软件设计核心思想](#7软件设计核心思想)
- [8. 使用说明](#8使用说明)
- [9. 示例程序](#9示例程序)
- [10. 注意事项](#10注意事项)
- [11. 版本记录](#11版本记录)
- [12. 联系开发者](#12联系开发者)
- [13. 许可协议](#13许可协议)
# **项目说明**

## **1.简介**

### **1.1 项目背景**

传统信号发生器设备通常体积庞大、操作复杂且价格昂贵。本项目**基于 GraftPort-RP2040 开发板**，结合**基于 SI5351 芯片的时钟信号发生模块**、**基于 PCF8574 的五向按键模块**和 **0.96 寸 SSD1306-OLED 模块**，实现"频率设置-通道选择-信号输出"一体化可编程信号发生器系统，解决专业信号源设备操作复杂、便携性差的问题，同时融入 `MicroPython` 的轻量化任务调度与菜单交互机制，提供友好的用户操作体验。

### **1.2 项目主要功能概览**

本项目基于 `MicroPython` 开发，核心功能是通过 `SI5351` 芯片生成可编程频率信号，通过 `OLED` 显示屏提供交互式菜单界面，用户可以通过五向按键设置输出频率、选择输出通道、控制信号输出启停；支持板载按键中断切换任务启停，内置自动垃圾回收避免内存泄漏，异常捕获与限速打印便于问题定位。

### **1.3 适用场景或应用领域**

- **电子实验**：为电路测试提供可调频率的信号源；
- **教学演示**：用于数字电路、频率合成原理的教学演示；
- **射频开发**：作为低成本射频信号源用于原型开发；
- **仪器校准**：为其他测试设备提供参考信号源。

## 2.主要功能

- **可编程信号输出**：通过**基于 SI5351 芯片的时钟信号发生模块**支持 0-20MHz 频率范围的可编程信号输出，支持三个独立输出通道；
- **OLED 菜单交互**：通过 **0.96 寸 SSD1306-OLED 模块**提供四级菜单系统（频率设置、输出通道、开启输出、停止输出）；
- **五向按键控制**：通过**基于 PCF8574 的五向按键模块**实现菜单导航和参数调节；
- **多通道输出管理**：支持三个独立输出通道的单独控制，可独立设置频率和启停状态；
- **按键中断交互**：板载按键触发下降沿中断，可切换核心任务"运行/暂停"；
- **自动内存管理**：空闲时检测内存，若低于阈值自动触发 `GC`，防止 `MicroPython` 因内存泄漏崩溃；
- **异常容错机制**：任务执行抛异常时，完整打印回溯信息并限速，避免刷屏；
- **板级适配灵活**：基于 `board.py` 实现引脚映射解耦，支持后续扩展其他 `RP2040` 开发板。

## 3.硬件要求

### 3.1 需要硬件

项目**基于 GraftPort-RP2040 开发板**作为主控：

![](docs/DNrmbkvU4oPWlCxSgT5cGe5SnUh.png)

**其余需要的模块包括：**

![](docs/RgIMbMzCvokLeZxBB8DcQ1cvnqh.png)

- **GtaftSense-SI5351 可编程时钟发生器模块:**（`I2C` 通信，地址 `0x60` 或 `0x61`）；
- **GtaftSense-PCF8574 I2C 扩展的五向按键模块:**（`I2C` 通信，地址 `0x20`-`0x27`）；
- **GtaftSense-0.96 寸 SSD1306-OLED 模块:**（`I2C` 通信，地址 `0x3c` 或 `0x3d`）；
- **GtaftSense-6 路 12C 直连扩展模块：**`I2C` 总线接口拓展；
- **GtaftSense-基于SY7656 锂电池充放电模块:**（连接聚合物锂电池，输出 5V 电压，带 `Type-C` 充电接口）；
- **板载按键:** 默认使用开发板固定引脚（引脚 18，上拉输入），无需额外接线；
- **板载LED:** 默认使用开发板固定引脚（引脚 25），无需额外接线。

### 3.2 **硬件连线**

**PCF8574 五向按键模块：**通过 `PH2.0` 连接线接入** I2C 拓展模块**；

**0.96 寸 SSD1306-OLED 模块：**通过 `PH2.0` 连接线接入** I2C 拓展模块**；

![](docs/ZdtGbGfi2oW3R7xs05FcG9kmn3b.JPG)

**6 路 12C 直连扩展模块**：通过 `PH2.0` 连接线接入 `I2C0` 接口

![](docs/RlOjb0LTGoCbNFx7yqtcjykln5d.png)

**GtaftSense-SI5351 可编程时钟发生器模块**:通过 `PH2.0` 连接线接入 `I2C1` 接口；

![](docs/E6RibyBdgoGtkCxztbPcktgHn9g.png)

**锂电池充放电模块**：`BAT` 接口连接锂电池，`OUT` 接口通过 `PH2.0-2P` 连接线为主控板供电。

![](docs/DVifbKGZnoEkJ3x18mrcfSein5c.png)

![](docs/VJ2dbAmYaoliV4xxWd5cOAIJnId.png)

![](docs/GoGXbEAi2osMzKx3O4mcxw8pn7c.png)

### 3.3 结构装配

**首先，使用 M3 塑料柱将各模块与主控板固定在外壳底板上（主控板与外壳均预留 M3 螺丝孔）**：

![](docs/BrYMbio8AoNuZCxRZ4OcwAZCni9.png)

![](docs/D0tSb7dxDokjs8xfBb6cXYMbnGd.png)

**接着，利用 M3 塑料柱将外壳四周固定好，并在对应位置拧上 M3 螺丝完成装配：**

![](docs/PObabNUsEoXHeTxQ9Gocua49nAc.png)

### 3.4 注意事项

**在主控板不连接外部看门狗模块时，RUN 拨码开关 2 要导通：**

![](docs/V4mDbc9mNoxt7ax3z2jcRb2ynab.png)

**锂电池充放电模块支持电量显示，使用下面****Type-C****接口即可充电：**

![](docs/U44dbQi1AoqmxKxv6qMcd6QJnDB.png)

## 4.软件环境

- **核心固件**：`MicroPython v1.23.0`（需适配 `GraftPort-RP2040`，支持 `machine.Pin/I2C/Timer` 模块、软定时器调度）；
- **开发 IDE**：`PyCharm`（用于代码编写、上传、调试，支持 `MicroPython REPL` 交互，需要安装 `MicroPython` 插件）；
- **辅助工具**：

  - `Python 3.12+`（用于运行本地辅助脚本，如固件烧录脚本，可选）；
  - `mpy-cross v1.23.0`（用于将 `.py` 文件编译为 `.mpy`，减少开发板内存占用，可选）；
  - `mpremote v0.11.0+`（替代 `Thonny` 上传文件，支持命令行操作，可选）；
- **依赖模块**：无额外第三方库，所有驱动（`passive_buzzer_driver.py` 等）均为自定义实现的，随项目文件提供。

## 5.文件结构

```
square_wave_generator
├─ .flake8
├─ LICENSE
├─ README.md
├─ tools
│  ├─ dependency_analyzer.py
│  ├─ mpy_compiler.py
│  ├─ mpy_uploader.py
│  └─ README.md
├─ firmware
│  ├─ board.py
│  ├─ boot.py
│  ├─ conf.py
│  ├─ main.py
│  ├─ tasks
│  │  ├─ maintenance.py
│  │  ├─ sensor_task.py
│  │  └─ __init__.py
│  ├─ libs
│  │  ├─ __init__.py
│  │  ├─ scheduler
│  │  └─ oledmenu
│  └─ drivers
│     ├─ __init__.py
│     ├─ ssd1306_driver
│     ├─ si5351_driver
│     └─ pcf8574keys_driver
└─ examples
   └─ README.md
```

## 6.关键文件说明

- **main.py**：**项目入口，核心逻辑包括**：

  1. 上电延时 3 秒（等待硬件稳定），初始化板载 `LED`、`OLED`、`SI5351`、`PCF8574` 按键模块、按键（含中断注册）；
  2. 硬件初始化：`I2C` 总线扫描自动识别设备地址，`OLED` 菜单系统初始化；
  3. 创建 `sensor_task` 实例（传入硬件驱动与配置参数），封装为调度器任务（周期 200ms）；
  4. 初始化 `Scheduler`（软定时器，调度周期 50ms），添加任务并启动调度，进入无限循环；
  5. 定义 `button_handler` 中断回调（切换任务启停）、`fatal_hang` 阻塞函数（严重错误处理）。
- **tasks/sensor_task.py**：**核心业务任务，**`sensorTask` **类关键逻辑**：

  1. `__init__`：初始化硬件实例，创建四级菜单系统，配置 `SI5351 PLL` 和输出通道；
  2. `tick`：每 200ms 执行一次，流程为"读取按键状态 → 菜单导航 → 参数设置 → 信号输出控制"；
  3. 菜单回调函数：`show_freq`（设置频率）、`sw_output`（选择输出通道）、`show_output`（开启输出）、`show_stop`（停止输出）。
- **tasks/maintenance.py**：**系统维护模块，关键函数**：

  1. `task_idle_callback`：调度器空闲时触发，检测内存低于 `GC_THRESHOLD_BYTES`（默认 100000 字节）则执行 `gc.collect()`；
  2. `task_err_callback`：任务抛异常时触发，打印完整回溯信息（优先 `sys.print_exception`），并延时 `ERROR_REPEAT_DELAY_S`（默认 1 秒）防止刷屏；
  3. 支持从 `conf.py` 读取配置，无配置时使用默认值，保证兼容性。
- **drivers/xxx_driver**：**硬件驱动模块，均采用"实例化 + 方法调用"模式**：

  - `si5351_driver`：`SI5351_I2C` 类通过 `I2C` 控制时钟发生器，提供 `setup_pll`、`init_clock`、`set_freq_fixedpll`、`enable_output` 等方法；
  - `pcf8574keys_driver`：`PCF8574Keys` 类通过 `I2C` 读取五向按键状态，`read_all` 方法返回所有按键状态字典；
  - `ssd1306_driver`：`SSD1306_I2C` 类通过 `I2C` 控制 `OLED` 显示，提供 `fill`、`text`、`show` 等方法；
  - `oledmenu`：`SimpleOLEDMenu` 类实现 `OLED` 菜单系统，支持菜单添加、导航、显示和回调执行。
- **board.py**：板级引脚映射模块，定义 `BOARDS` 字典（含 `GraftPort-RP2040` 的固定引脚、`I2C` 接口映射），提供 `get_fixed_pin`、`get_i2c_pins` 等接口，实现"板级配置与业务逻辑解耦"。
- **conf.py**：**用户配置文件，需用户手动定义的参数包括**：`I2C_INIT_MAX_ATTEMPTS`（传感器初始化重试次数）、`I2C_INIT_RETRY_DELAY_S`（重试间隔秒数）、`ENABLE_DEBUG`（调试打印开关）、`AUTO_START`（任务是否自动启动），无定义时系统使用默认值。

## 7.软件设计核心思想

![](docs/D13zbolXmoZZ11xddfccjFxynzg.png)

- **系统分层思路**：采用"四层架构"，实现解耦与复用

  - **硬件驱动层（****drivers/****）**：仅负责硬件的底层控制，如 `SI5351` 驱动只关心"如何设置频率"，不关心"用户如何操作"。
  - **任务逻辑层（****tasks/****）**：基于驱动层和菜单系统实现业务逻辑，如 `sensorTask` 通过菜单回调响应用户操作，调用 `SI5351` 驱动设置参数。
  - **调度控制层（****libs/scheduler.py****）**：提供通用的任务管理能力，支持任务添加/暂停/恢复、空闲/异常回调。
  - **入口层（****main.py****）**：负责"组装"各层，初始化硬件 → 创建任务 → 启动调度，是系统的"胶水"。
- **模块划分原则**：高内聚、低耦合，便于维护与扩展

  - **高内聚：** 每个模块只负责单一职责，如 `maintenance.py` 仅处理系统维护，`sensor_task.py` 仅处理用户交互和信号控制。
  - **低耦合：** 模块间通过"接口"交互，如 `sensorTask` 通过 `PCF8574Keys.read_all`()获取按键状态，不直接操作 `I2C` 硬件。
  - **扩展性：** 新增功能只需在菜单系统中添加新项和对应回调，无需修改现有架构。
- **核心机制：** 保障系统稳定与用户体验

  - **任务调度机制：** 基于软定时器实现，调度周期 50ms，核心任务周期 200ms，通过"计数器累加"判断任务执行时机。
  - **菜单交互机制**：四级菜单结构清晰，五向按键操作直观，实时显示当前状态和参数。
  - **频率控制机制：** 支持 0-20MHz 范围精确调节，三个输出通道独立控制，`PLL` 配置保证频率稳定性。
  - **容错机制：**`I2C` 设备自动地址识别，异常情况 `LED` 闪烁提示，关键操作异常捕获防止系统崩溃。
- **任务执行流程：任务执行流程如下所示**：

![](docs/EKCfbvdS9oPiiRxrpUIcAZwVnBf.png)

## 8.使用说明

### **8.1 硬件连接**

按“硬件要求”中的连接方式，连接主控板、各个传感器模块和电池；

### **8.2 运行项目（使用PyCharm + MicroPython插件）**

打开 `PyCharm` 并安装对应的 `MicroPython` 插件。

![](docs/SVhtb39JUoi3V6xHNsCc5PVRnNd.png)

在插件中选择 **运行设备（**`Target Device`**）** 为 `RP2040`，并启用 **自动检测设备路径（**`Auto-detect device path`**）**。

![](docs/ZwA3bEll9oz3n0xfP8Lc3OG5nre.png)

将 ` Project/firmware` 设置为项目根目录。

![](docs/L0glbTzTGoyWJgxatDZciJHench.png)

**修改运行配置**：

![](docs/T9vobYyKuoyUPSxZiYUcxwGDnx1.png)

- 勾选 **允许多个实例（****Allow multiple instances****）**
- 选择 **存储为项目文件（****Store as project file****）**
- 点击 **确定** 保存配置。

点击 `IDE` 右上角的绿色三角按钮运行，即可开始上传固件并执行项目。

![](docs/XUr7bVoI3o9xVFx0DEAcqm86nMd.png)

### **8.3 运行配置的修改**

**您可以配置 ****conf.py****，根据需求修改或添加参数，例如**：

```python
# conf.py 示例配置
I2C_INIT_MAX_ATTEMPTS = 3      # 传感器初始化最多重试次数
I2C_INIT_RETRY_DELAY_S = 0.5   # 每次重试间隔（秒）
ENABLE_DEBUG = True            # 是否开启调试打印
AUTO_START = True              # 是否在启动时自动运行任务
```

### **8.4 功能测试**

**打开主控板下方的****VBAT****电池供电开关，可以看到主控板和模块上的电源指示灯亮起**：

- **菜单导航**：使用五向按键上下选择菜单项，左右调节参数，`SW1` 确认，`SW2` 返回；
- **频率设置**：在 `freq` 菜单中设置输出频率（0-20MHz 范围）；
- **通道选择**：在 `output` 菜单中选择输出通道（0-2）；
- **信号输出**：在 `open` 菜单开启选中通道的信号输出，在 `stop` 菜单停止输出；

![](docs/S1ncbKtKeowsiQx5zNxcCAQSn0f.gif)

- 示波器根据设置输出正确显示波形频率为 12Mhz：

![](docs/AqwhbmPELonqsBxOmsRcRLdfnah.png)

- **任务控制**：按下板载按键，任务暂停（停止菜单响应），再次按下恢复。

在 `conf.py` 中配置不变同时硬件连接没有问题的情况下，程序可以正常运行

**终端输出结果如下所示**：

![](docs/J0nWbsuFQojY2mxGmgwcX1CDnif.png)

### **8.5 调试与问题定位**

- 若功能异常，确保 `ENABLE_DEBUG = True`，在终端查看调试信息；
- 若 `I2C` 设备不响应，检查硬件连接、电源、`I2C` 地址配置；
- 若 `OLED` 不显示，检查 `I2C` 地址是否正确（`0x3c` 或 `0x3d`），以及 `I2C` 总线是否正常；
- 若 `SI5351` 无输出，检查 `PLL` 配置、频率设置和输出使能状态。

## 9.示例程序

本项目没有其余参考示例代码，直接在 `firmware` 文件夹中进行修改即可。

## 10.注意事项

- **传感器相关：**

  - 输出频率范围受 `SI5351` 芯片限制，最高约 200MHz，本项目限制在 0-20MHz；
  - 频率切换时需要重新配置 `PLL`，会有短暂的频率不稳定期。
- **硬件连接相关**：

  - `I2C` 设备地址可能因厂商不同而变化，系统会自动扫描识别；
  - `SI5351` 模块需要稳定的电源供应，避免频率抖动。
- **软件版本相关**：

  - 必须使用 `MicroPython v1.23.0` 及以上版本；
  - 调试打印会占用一定内存，正式使用时建议关闭。
- **功能使用相关**：

  - 任务周期（200ms）不建议修改过小，否则可能影响按键响应；
  - 频率设置步进为 1MHz，可根据需要调整代码中的调节步长。

## 11.版本记录

- **v1.0.0 (2025-10-10)**：**侯钧瀚完成初始版本，基本功能实现和文档编写**：
  - 支持 `SI5351` 可编程信号输出
  - 实现 `OLED` 四级菜单交互系统
  - 支持五向按键导航和参数调节
  - 实现三通道独立输出控制

## 12.联系开发者

**如有任何问题或需要帮助，请通过以下方式联系开发者**：
📧 **邮箱**：<u>10696531183@qq.commailto:10696531183@qq.com</u>
💻 **GitHub**：<u>[https://github.com/FreakStudioCN](https://github.com/FreakStudioCN)</u>

## 13.许可协议

本项目中，除 `machine` 等 `MicroPython` 官方模块（`MIT` 许可证）外，所有由作者编写的驱动与扩展代码均采用 **知识共享署名-非商业性使用 4.0 国际版 (CC BY-NC 4.0)** 许可协议发布。

**您可以自由地**：

- **共享** — 在任何媒介以任何形式复制、发行本作品
- **演绎** — 修改、转换或以本作品为基础进行创作

**惟须遵守下列条件**：

- **署名** — 您必须给出适当的署名，提供指向本许可协议的链接，同时标明是否（对原始作品）作了修改。您可以用任何合理的方式来署名，但是不得以任何方式暗示许可人为您或您的使用背书。
- **非商业性使用** — 您不得将本作品用于商业目的。
- **合理引用方式** — 可在代码注释、文档、演示视频或项目说明中明确来源。

**版权归 FreakStudio 所有。**

# 附件一：项目源代码下载

# 附件二：硬件模块参考资料

[GraftSense-基于 SY7656 芯片的锂电池充放电模块（开放版）](https://f1829ryac0m.feishu.cn/docx/C3RFd6XGEowEwOxb3plc7C5CnBb?from=from_copylink)

[GraftPort-RP2040 开发板](https://f1829ryac0m.feishu.cn/docx/ZHdjdPdCwonbLyxVeAdcehG4n8b?from=from_copylink)

# 版本记录

<table>
<tr>
<td>**文档版本**<br/></td><td>**修改日期**<br/></td><td>**修改人**<br/></td><td>**修改内容**<br/></td></tr>
<tr>
<td>V1.0.0<br/></td><td>2025-11-03<br/></td><td>侯钧瀚<br/></td><td>编写文档初稿。<br/></td></tr>
<tr>
<td><br/></td><td><br/></td><td><br/></td><td><br/></td></tr>
</table>
