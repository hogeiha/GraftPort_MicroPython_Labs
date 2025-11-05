# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2025/9/9 下午11:17   
# @Author  : 李清水            
# @File    : main.py       
# @Description : 主程序文件夹，主要用于初始化配置、创建任务和启动任务。
# @License : CC BY-NC 4.0

# ======================================== 导入相关模块 =========================================

# 导入硬件相关模块
from machine import UART, Pin, I2C, Timer
# 导入时间相关模块
import time

# 导入板级支持包
import board
# 导入配置文件
from conf import *
# 导入lib文件夹下面自定义库
from libs.scheduler import Scheduler, Task
# 导入drivers文件夹下面传感器模块驱动库
from drivers.air_quality_driver import AirQualityMonitor, MEMSGasSensor, PCA9546ADR
from drivers.tas755c_driver import TAS_755C_ETH

#  导入tasks文件夹下面任务模块
from tasks.maintenance import task_idle_callback, task_err_callback
from tasks.maintenance import GC_THRESHOLD_BYTES, ERROR_REPEAT_DELAY_S
from tasks.lora_task import LoraTask

# ======================================== 全局变量 ============================================

# I2C0 时钟频率 (Hz)，默认 100kHz
I2C_FREQ = 400_000
# I2C 上 模块的固定通信地址
AIR_ADDR = 0x70

# ======================================== 功能函数 ============================================

def fatal_hang(led: Pin, msg: str,
               on_ms: int = 150, off_ms: int = 150,
               pulses: int = 2, pause_s: float = 1.0) -> None:
    """
    在检测到严重错误时阻塞运行：板载 LED 按指定节奏闪烁，并不断在终端打印提示信息。

    Args:
        led (Pin): 已初始化的板载 LED Pin 对象（输出模式）。
        msg (str): 要在终端重复打印的错误/提示信息。
        on_ms (int): 每次闪烁点亮时长，单位毫秒（默认 150ms）。
        off_ms (int): 每次闪烁熄灭时长，单位毫秒（默认 150ms）。
        pulses (int): 每个循环内的闪烁次数（例如 2 表示两短闪）。
        pause_s (float): 每个循环后的静默暂停，单位秒（默认 1.0s）。

    Returns:
        None: 该函数不会返回（无限循环），除非外部抛出 KeyboardInterrupt。
    """
    try:
        # 确保 LED 初始为灭
        try:
            led.value(0)
        except Exception:
            pass

        # 无限循环：每个循环打印并闪烁 pulses 次，然后 pause
        while True:
            for i in range(pulses):
                # 在每次点亮前打印提示（频率可根据需要调整）
                try:
                    print(msg)
                except Exception:
                    # 打印失败也不要中断，至少确保 LED 行为正常
                    pass

                # LED 点亮
                try:
                    led.value(1)
                except Exception:
                    pass
                # 等待点亮时长
                time.sleep_ms(on_ms)

                # LED 熄灭
                try:
                    led.value(0)
                except Exception:
                    pass
                # 等待熄灭时长
                time.sleep_ms(off_ms)

            # 循环间较长暂停
            time.sleep(pause_s)

    except KeyboardInterrupt:
        # 如果在 REPL 手动中断（Ctrl-C）则关闭 LED 并把中断抛出，便于调试
        try:
            led.value(0)
        except Exception:
            pass
        raise
    except Exception as e:
        # 捕获意外异常，打印并灭灯后短暂等待，继续挂起
        try:
            print("fatal_hang internal error:", e)
        except Exception:
            pass
        try:
            led.value(0)
        except Exception:
            pass
        while True:
            time.sleep(1)

def button_handler(pin: Pin) -> None:
    """
    外部中断回调：切换任务运行/暂停状态。

    在外部中断触发时被调用，用于在运行态与暂停态之间切换 `sensor_task`。
        - 当任务正在运行时：调用调度器暂停任务，并**立即**关闭与任务相关的外设（LED / 蜂鸣器）。
        - 当任务已暂停时：调用调度器恢复任务运行。

    Args:
        pin (Pin): 触发中断的输入 Pin 对象（由外部中断注册时指定）。

    Returns:
        None

    Notes:
        - 该函数设计为中断回调（ISR）使用，应尽量保持简短与非阻塞，避免大量内存分配和长时间阻塞操作。
        - 这里包含少量打印（仅在 ENABLE_DEBUG 打开时）与 try/except 捕获，用于兼容调试与保证回调的稳健性。
    """
    global sensor_task, led, buzzer

    if sensor_task._state == Task.TASK_RUN:
        # 暂停任务
        sc.pause(sensor_task)
        if ENABLE_DEBUG:
            print("task_sensor paused")
        # 暂停时立即关闭 LED 和蜂鸣器
        try:
            sensor_task_obj.immediate_off()
        except Exception:
            pass
    else:
        # 恢复任务
        sc.resume(sensor_task)

        if ENABLE_DEBUG:
            print("task_sensor resumed")

# 显示相关
def _init_display(ssd1306):
    ssd1306.fill(0)
    ssd1306.text("GXCZD", 45, 0)
    ssd1306.text("TX:", 0, 40)
    ssd1306.text("RX:", 0, 52)
    ssd1306.show()

def _press(ssd1306):
    ssd1306.fill(0)
    ssd1306.text("Press Key button Now", 0, 0)
    ssd1306.text("Hold on Press", 0, 40)
    ssd1306.show()

def _unpress(ssd1306):
    ssd1306.fill(0)
    ssd1306.text("Free Key button Now", 0, 0)
    ssd1306.show()

def i2c_valid(i2c, correct_addrs):
    # 尝试初始化I2C外设上的传感器模块
    for attempt in range(1, I2C_INIT_MAX_ATTEMPTS + 1):
        print("I2C init attempt {}/{}".format(attempt, I2C_INIT_MAX_ATTEMPTS))

        # 扫描 I2C 总线
        try:
            addrs = i2c.scan()
            print("I2C scan result (hex):", [hex(a) for a in addrs])
        except Exception as e_scan:
            print("I2C scan failed on attempt {}: {}".format(attempt, e_scan))
            addrs = []

        # 若找到目标地址则返回
        if correct_addrs in addrs:
            return addrs

        # 若还有重试次数，等待后重试
        if attempt < I2C_INIT_MAX_ATTEMPTS:
            time.sleep(I2C_INIT_RETRY_DELAY_S)
    # 如果多次尝试仍失败，则进入 fatal_hang（阻塞并报告）
    if addrs is None:
        err_msg = "RCWL9623 init failed after {} attempts. last_err: {}".format(
            I2C_INIT_MAX_ATTEMPTS, repr(last_err)
        )
        # fatal_hang 会阻塞（闪灯并持续在终端输出 msg）
        fatal_hang(led, err_msg)

# ======================================== 自定义类 ============================================

# ======================================== 初始化配置 ==========================================

# 上电延时3s
#time.sleep(3)
# 打印调试信息
print("FreakStudio : proximity music light in GraftPort-RP2040")

# 获取板载LED的固定引脚
led_pin = board.get_fixed_pin("LED")
led = Pin(led_pin, Pin.OUT)

# 获取板载按键的固定引脚
button_pin = board.get_fixed_pin("BUTTON")
# 创建板载按键实例
button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

uart0_tx, uart0_rx = board.get_uart_pins(0)
uart0 = UART(0, baudrate=9600, tx=Pin(uart0_tx), rx=Pin(uart0_rx))
#hc14_tx = HC14_Lora(uart0)

# 获取I2C0 I2C1的引脚编号
i2c0_sda_pin , i2c0_scl_pin = board.get_i2c_pins(0)
# 创建I2C实例
i2c0 = I2C(id = 0, scl = i2c0_scl_pin, sda = i2c0_sda_pin, freq = I2C_FREQ)

air = i2c_valid(i2c0, AIR_ADDR)
air = AirQualityMonitor(i2c0, air[0])

air.register_sensor('VOC_Sensor', 0x2A, 0, 0x2A)

print(air.read_gas('VOC_Sensor'))