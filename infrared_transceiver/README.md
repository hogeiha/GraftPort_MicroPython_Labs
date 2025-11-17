# 红外无线式按键数据收发装置（基于 GraftPort-RP2040 开发板）

![](docs/DkxDbADbmo0SBDx4mjFcSdEWnpc.png)

![](docs/LzwybZkTuouf3XxueLtcb7UwnWg.gif)

## 1.简介

### **1.1 项目背景**

传统红外通信系统多为单向传输或功能单一，缺乏直观的数据显示和交互反馈能力。本项目**基于 GraftPort-RP2040 开发板**，结合**基于 PCF8574 的 8 位 IO 端口扩展模块**连接 4 个**机械按键模块**、**基于 IR333C 的红外发射模块**、**基于 TSOP34138 的红外接收模块**和 **0.96 寸 SSD1306-OLED 模块**，实现"红外数据传输-显示-交互反馈"一体化系统，解决传统红外通信系统交互性差的问题，同时融入 `MicroPython` 的高效任务调度与状态管理机制，保证系统稳定运行。

### **1.2 项目主要功能概览**

本项目基于 `MicroPython` 开发，核心功能是通过 `PCF8574` `IO` 扩展模块检测按键状态，通过**基于 IR333C 的红外发射模块**发送对应字母数据，通过**基于 TSOP34138 的红外接收模块**接收数据并在 `OLED` 显示屏上实时显示收发状态；支持自动发送间隔控制，内置显示状态自动清除机制，异常捕获与调试信息输出便于问题定位。

### **1.3 适用场景或应用领域**

- 教育实验：用于红外通信原理的教学演示，展示数据编码、传输和解码过程；
- 遥控系统：作为简易红外遥控器的原型系统，可用于设备控制、信号转发；
- 物联网节点：在无法使用无线电的场合，通过红外实现短距离数据通信；
- 交互装置：用于互动艺术装置、智能家居控制等需要非接触通信的场景。

## 2.主要功能

- **红外数据收发：** 支持 `NEC` 协议的红外数据发送和接收，自动处理重复码；
- **按键状态检测：**通过**基于 PCF8574 的 8 位 IO 端口扩展模块**检测 4 个独立按键状态；
- **OLED 实时显示：**通过** 0.96 寸 SSD1306-OLED 模块**实时显示收发数据状态；
- **自动发送控制：** 每 3 秒自动发送当前按键对应的字母数据；
- **显示状态管理：** 收发数据显示 5 秒后自动清除，避免屏幕信息堆积；
- **异常容错机制：**`I2C` 设备初始化失败时自动重试，严重错误时 `LED` 闪烁报警；
- **板级适配灵活：** 基于 `board.py` 实现引脚映射解耦，支持后续扩展其他 `RP2040` 开发板。

## 3.硬件要求

### 3.1 需要硬件

项目**基于 GraftPort-RP2040 开发板**作为主控：

![](docs/HjNYbp0zxocwgaxp8pRcdlzvnkW.png)

**其余需要的模块包括：**

#图（使用到的模块照片）

- **GtaftSense-基于 PCF8574 的 8 位 IO 端口扩展模块:**（`I2C` 通信，用于按键状态检测）；
- **GtaftSense-基于 IR333C 的红外发射模块:**（连接 `DIO` 接口，支持 38kHz 载波）；
- **GtaftSense-基于 TSOP34138 的红外接收模块:**（连接 `DIO` 接口，支持 C 协议解码）；
- **GtaftSense-0.96 寸 SSD1306-OLED 模块:**（`I2C` 通信，地址 `0x3c` 或 `0x3d`）；
- **GtaftSense-基于 SY7656 锂电池充放电模块:（连接聚合物锂电池，输出 5V 电压，带****Type-C****充电接口）；**
- **板载 LED：** 默认使用开发板固定引脚，无需额外接线。

### 3.2 **硬件连线**

**基于 PCF8574 的 8 位 IO 端口扩展模块**：通过 `PH2.0` 连接线接入 `I2C0` 接口；

![](docs/EoIpbgwIPoT7nBxnz1dckObTn2e.JPG)

**机械按键模块：**接入**基于 PCF8574 的 8 位 IO 端口扩展模块**进行按键拓展（四个机械按键都需接入 8 位 IO 端口扩展模块）

![](docs/LDUdbogfooc0A0xPQrkcaqDpnJg.JPG)

**基于 IR333C 的红外发射模块：** 通过 `PH2.0` 连接线接入 `DIO0` 接口；

![](docs/Wg0ybgjUyotK7OxFAwucEsXXnPc.JPG)

**基于 TSOP34138 的红外接收模块：** 通过 `PH2.0` 连接线接入 `DIO1` 接口；

![](docs/Qs1mbVq3doxq8HxgvURcODTcnoc.JPG)

**0.96 寸 SSD1306-OLED 模块：** 通过 `PH2.0` 连接线接入 `I2C1` 接口。

![](docs/QEuwb9o5Ho8K3ExkzOhcfpkOn5d.JPG)

**锂电池充放电模块**：`BAT` 接口连接锂电池，`OUT` 接口通过 `PH2.0-2P` 连接线为主控板供电。

![](docs/TMChbUhPioPCm9x95TAcbYE3nOk.png)

![](docs/Yh2Rb3e1QoRZB5xaAPfclUF9n8c.png)

![](docs/EhQwbH92Ioj82GxuctKcDSYFnVh.png)

### 3.3 结构装配

**首先，使用 M3 塑料柱将各模块与主控板固定在外壳底板上（主控板与外壳均预留 M3 螺丝孔）：**

![](docs/Wt7MbMGUgoKtLQxvyZyc1dPvnGb.png)

![](docs/MdO2b7ZdMoAt0KxwCoucDPYInkp.png)

**接着，利用 M3 塑料柱将外壳四周固定好，并在对应位置拧上 M3 螺丝完成装配：**

![](docs/Uz2ObnUcXojeUjx25jCcsyJ1nYg.png)

### 3.4 注意事项

**在主控板不连接外部看门狗模块时，RUN 拨码开关 2 要导通：**

![](docs/KwYabDRqooQ7ALxo6LVc101sn8f.png)

**锂电池充放电模块支持电量显示，使用下面 Type-C 接口即可充电：**

![](docs/RiOnbYLG0ouIt3xzLmccKHlKnLh.png)

## 4.软件环境

- **核心固件：**`MicroPython v1.23.0`（需适配 `GraftPort-RP2040`，支持 `machine.Pin/I2C/Timer` 模块、软定时器调度）；
- **开发 IDE：**`PyCharm`（用于代码编写、上传、调试，支持 `MicroPython REPL` 交互，需要安装 `MicroPython` 插件）；
- **辅助工具：**

  - `Python 3.12+`（用于运行本地辅助脚本，如固件烧录脚本，可选）；
  - `mpy-cross v1.23.0`（用于将.`py` 文件编译为 `.mpy`，减少开发板内存占用，可选）；
  - `mpremote v0.11.0+`（替代 `Thonny` 上传文件，支持命令行操作，可选）；
- **依赖模块：** 无额外第三方库，所有驱动（`passive_buzzer_driver.py` 等）均为自定义实现的，随项目文件提供。

## 5.文件结构

```
infrared_transceiver
├─ LICENSE
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
│  │  └─ tasks_here
│  ├─ libs
│  │  └─ libs_here
│  └─ drivers
│     ├─ __init__.py
│     ├─ ssd1306_driver
│     └─ irtranslation_driver
├─ examples
│  └─ README.md
├─ docs
└─ build
```

## 6.文件说明

- `main.py`**：项目入口，核心逻辑包括：**

  1. 全局状态变量定义（收发状态、显示控制标志等）；
  2. 硬件初始化：板载 `LED`、红外收发模块、`I2C` 外设、`PCF8574` 和 `SSD1306`；
  3. `I2C` 设备验证机制：自动扫描并验证设备地址，失败时重试；
  4. 主循环控制：按键状态检测、自动发送控制、显示状态更新和清除；
  5. 回调函数：红外接收回调、发送完成处理。
- `drivers/pcf8574_driver.py`**：`PCF8574` `IO` 扩展驱动，关键功能：**

  1. 端口读写操作，支持 8 位 `IO` 扩展；
  2. 按键状态检测和去抖动处理。
- `drivers/irtranslation_driver.py` **：红外收发驱动，关键功能：**

  1. `NEC` 协议编码和解码；
  2. 38kHz 载波生成；
  3. 红外数据发送和接收回调。
- `drivers/ssd1306_driver.p` **y：SSD1306 OLED 显示驱动，关键功能：**

  1. `I2C` 通信初始化；
  2. 屏幕控制（清屏、显示、文字输出）；
  3. 区域更新和清除。
- `board.py` **：** 板级引脚映射模块，定义 `BOARDS` 字典（含 `GraftPort-RP2040` 的固定引脚、`I2C`/`DIO` 接口映射），提供 `get_fixed_pin`、`get_i2c_pins` 等接口，实现"板级配置与业务逻辑解耦"。
- `conf.py` **：** 用户配置文件，需用户手动定义的参数包括：`I2C_INIT_MAX_ATTEMPTS`（设备初始化重试次数）、`I2C_INIT_RETRY_DELAY_S`（重试间隔秒数）、`ENABLE_DEBUG`（调试打印开关），无定义时系统使用默认值。

## 7.软件设计核心思想

![](docs/QNC0bgpyhovpQMxkGwncci2Vn8d.png)

- **状态机设计模式：** 采用基于状态标志的管理机制

  - **收发状态分离：**`tx_pending` 和 `rx_pending` 标志分别管理发送和接收状态，避免竞态条件；
  - **显示更新异步：** 回调函数只设置状态标志，主循环统一处理显示更新，确保显示操作的线程安全；
  - **自动清除机制：** 基于时间戳的显示区域自动清除，保持界面整洁。
- **事件驱动架构：** 结合中断和轮询的混合模式

  - **红外接收中断：** 实时响应红外数据接收，确保不丢失数据帧；
  - **主循环轮询：** 定期检测按键状态、处理显示更新、管理自动发送；
  - **时间触发任务：** 基于系统滴答定时执行周期性任务。
- **资源管理优化：** 高效利用系统资源

  - **I2C 总线复用：** 多个 `I2C` 设备共享总线，通过不同地址区分；
  - **显示局部更新：** 只更新变化的显示区域，减少全屏刷新频率；
  - **内存友好设计** ：避免在中断中执行复杂操作，防止内存碎片。
- **错误处理机制：** 多层防护确保系统稳定

  - **设备初始化重试：**`I2C` 设备初始化失败时自动重试多次；
  - **通信超时处理：** 红外通信设置合理的超时机制；
  - **状态一致性检查：** 关键操作前后进行状态验证。
- **数据流控制流程：** 数据流控制流程如下所示

![](docs/XhDUbku0XopdXmxK9tacIw15n8V.png)

## 8.使用说明

### **8.1 硬件连接**

按“硬件要求”中的连接方式，连接主控板、各个传感器模块和电池；

### **8.2 运行项目（使用 PyCharm + MicroPython 插件）**

打开 `PyCharm` 并安装对应的 `MicroPython` 插件。

![](docs/Dt5fbPKfpowQA0x39oAc0mJ1n3e.png)

在插件中选择 ` ` **运行设备（Target Device）** 为 `RP2040`，并启用 **自动检测设备路径（Auto-detect device path）**。

![](docs/HELAbkApXow4lhxJxjsc2hJ8n3d.png)

将 ` ` **Project/firmware** 设置为项目根目录。

![](docs/PNDLblB2Mo12w8xLpOKctjIZnzc.png)

修改运行配置：

![](docs/T1sBbaVnloNpJ9xIkNjcds1rnwb.png)

- 勾选 **允许多个实例（Allow multiple instances）**
- 选择 **存储为项目文件（Store as project file）**
- 点击 **确定** 保存配置。

点击 `IDE` 右上角的绿色三角按钮运行，即可开始上传固件并执行项目。

![](docs/DmVLbnKJOomSHZxcXYqctZyvnKg.png)

### **8.3 运行配置的修改**

您可以配置 `conf.py`，根据需求修改或添加参数，例如：

```python
# conf.py 示例配置_
I2C_INIT_MAX_ATTEMPTS = 3      _# 设备初始化最多重试次数_
I2C_INIT_RETRY_DELAY_S = 0.5   _# 每次重试间隔（秒）_
ENABLE_DEBUG = True            _# 是否开启调试打印_
```

### **8.4 功能测试**

**打开主控板下方的****VBAT****电池供电开关，可以看到主控板和模块上的电源指示灯亮起：**

- **按键检测：** 按下不同按键，观察终端输出的按键状态变化；
- **红外发送：** 使用红外接收设备验证发送数据是否正确；
- **红外接收：** 使用红外遥控器发送信号，观察接收数据显示；
- **显示功能：** 确认 `OLED` 能够正确显示收发状态和自动清除。

在 `conf.py` 中配置不变同时硬件连接没有问题的情况下，程序可以正常运行

![](docs/Ifl8bN3adoJZzExMPBickuz2nOd.gif)

终端输出结果如下所示：

![](docs/VOA6br7FlokSp5xlKAicLRFQnRe.png)

### **8.5 调试与问题定位**

- 若功能异常，确保 `ENABLE_DEBUG = True`，在终端查看调试信息（如"`I2C scan result`"、"`IR Sent`"等）；
- 若 `I2C` 设备初始化失败，检查硬件连接、电源、引脚配置；
- 若红外通信不正常，检查收发模块对准、距离、障碍物；
- 若 `OLED` 不显示，检查 I2C 地址是否正确，以及 `I2C` 总线是否正常。

## 9.示例程序

本项目没有其余参考示例代码，直接在 `firmware` 文件夹中进行修改即可。

## 10.注意事项

- **红外通信相关：**

  - **基于 IR333C 的红外发射模块**需要直线对准**基于 TSOP34138 的红外接收模块**，中间避免障碍物；
  - 通信距离受环境光影响，强光环境下距离会缩短；
  - 避免多个红外设备同时工作，防止信号干扰；
  - `TSOP34138` 接收模块对 38kHz 载波敏感，确保发射模块载波频率准确。
- **硬件连接相关：**

  - `PCF8574` 模块的 I2C 地址必须设置为 `0x27`；
  - **基于 IR333C 的红外发射模块**需要连接支持 `PWM` 输出的引脚；
  - **基于 TSOP34138 的红外接收模块**需要连接数字输入引脚；
  - `SSD1306 OLED` 模块的 I2C 地址可能为 `0x3c` 或 `0x3d`，系统会自动检测。
- **软件版本相关：**

  - 必须使用 `MicroPython v1.23.0` 及以上版本；
  - 调试打印会占用一定内存，正式使用时建议关闭。
- **功能使用相关：**

  - 自动发送间隔（3 秒）可根据实际需求调整；
  - 显示清除时间（5 秒）可根据显示需求调整；
  - 按键检测灵敏度可通过软件去抖动参数调整。

## 11.版本记录

## 12.联系开发者

如有任何问题或需要帮助，请通过以下方式联系开发者：
📧 **邮箱**：<u>10696531183@qq.com</u>
💻 **GitHub**：<u>[https://github.com/FreakStudioCN](https://github.com/FreakStudioCN)</u>

## 13.许可协议

本项目中，除 `machine` 等 `MicroPython` 官方模块（`MIT` 许可证）外，所有由作者编写的驱动与扩展代码均采用 **知识共享署名-非商业性使用 4.0 国际版 (CC BY-NC 4.0)** 许可协议发布。

您可以自由地：

- **共享** — 在任何媒介以任何形式复制、发行本作品
- **演绎** — 修改、转换或以本作品为基础进行创作

惟须遵守下列条件：

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
<td>文档版本<br/></td><td>修改日期<br/></td><td>修改人<br/></td><td>修改内容<br/></td></tr>
<tr>
<td>V1.0.0<br/></td><td>2025-11-03<br/></td><td>侯钧瀚<br/></td><td>编写文档初稿。<br/></td></tr>
<tr>
<td><br/></td><td><br/></td><td><br/></td><td><br/></td></tr>
</table>
