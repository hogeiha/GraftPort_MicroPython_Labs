# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2025/9/9 下午11:17   
# @Author  : 李清水            
# @File    : main.py       
# @Description : 主程序文件夹，主要用于初始化配置、创建任务和启动任务。
# @License : CC BY-NC 4.0

# ======================================== 导入相关模块 =========================================

# 导入硬件相关模块
from machine import Pin, I2C
# 导入时间相关模块
import time

# 导入板级支持包
import board
# 导入配置文件
from conf import *
# 导入drivers文件夹下面传感器模块驱动库
from drivers.pcf8574_driver import PCF8574, SSD1306_I2C
from drivers.irtranslation_driver import NEC, NEC_16

# ======================================== 全局变量 ============================================

# I2C 时钟频率 (Hz)，默认 400kHz
I2C_FREQ = 400_000
# I2C0 上 SSD1306 模块的固定通信地址
SSD1306_ADDR = 0x3d
PCF8574_ADDR = 0x27
# I2C外设初始化错误记录
last_err = None

# 红外 & 显示状态全局变量
tx_index = 0
last_tx_time = 0      # 用于控制自动发送间隔（3s）
last_rx_time = 0      # 可选的调试时间戳

# 显示控制相关（用于主循环内的显示更新/清除）
tx_pending = False    # send_next 设置，主循环将消费并更新 OLED TX 区
tx_letter = ""        # 要显示的 TX 字母
tx_last_update = 0    # 记录上次更新 TX 区的 ticks_ms（用于 5s 清除）

rx_pending = False    # ir_callback 设置，主循环将消费并更新 OLED RX 区
rx_letter = ""        # 要显示的 RX 字母
rx_last_update = 0    # 记录上次更新 RX 区的 ticks_ms（用于 5s 清除）

TX_RX_CLEAR_MS = 5000  # 5 秒后清除对应区域


# ======================================== 功能函数 ============================================
# 显示相关
def _init_display(ssd1306):
    ssd1306.fill(0)
    ssd1306.text("GXCVU", 45, 0)
    ssd1306.text("TX:", 0, 40)
    ssd1306.text("RX:", 0, 52)
    ssd1306.show()

def _update_tx_display(text):
    # 清除 TX 区再写入
    ssd1306.fill_rect(30, 40, 90, 10, 0)
    ssd1306.text(text, 30, 40)
    ssd1306.show()

def _update_rx_display(text):
    # 清除 RX 区再写入
    ssd1306.fill_rect(30, 52, 90, 10, 0)
    ssd1306.text(text, 30, 52)
    ssd1306.show()

def _clear_tx_area():
    ssd1306.fill_rect(30, 40, 90, 10, 0)
    ssd1306.show()

def _clear_rx_area():
    ssd1306.fill_rect(30, 52, 90, 10, 0)
    ssd1306.show()

# 外部红外接收回调
def send_next():
    """发送一个字母并设置发送完成标志（不在此处直接更新 OLED）"""
    global tx_index, last_tx_time, tx_pending, tx_letter
    if tx_index is None:
        return
    # 更新用于自动发送间隔的时间戳
    last_tx_time = time.ticks_ms()

    # 生成字母并发送
    letter = chr(ord('a') + tx_index)
    ir_tx.transmit(0x00, tx_index)

    # 不要在中断/回调里更新 OLED，改为设置标志，由主循环处理显示
    tx_letter = letter
    tx_pending = True

    print("IR Sent:", letter)

def ir_callback(addr, cmd, repeat):
    """红外接收回调：仅设置标志与接收数据，由主循环更新 OLED"""
    global rx_pending, rx_letter, last_rx_time
    # 更新可选的调试时间戳（短小，不做复杂调用）
    last_rx_time = time.ticks_ms()
    print(f"[RX] Address=0x{addr:02X}, Cmd=0x{cmd:02X}, Repeat={repeat}")

    # 仅在有效数据时设置标志（不要在回调里直接操作显示）
    if repeat or addr != 0x01:
        return

    letter = chr(ord('a') + (cmd % 4))
    rx_letter = letter
    rx_pending = True
    print("IR Received (pending):", letter)


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
print("FreakStudio : ir_data_communication in GraftPort-RP2040")

# 获取板载LED的固定引脚
led_pin = board.get_fixed_pin("LED")
led = Pin(led_pin, Pin.OUT)

# 获取数字接口0的引脚编号
ir_tx , _ = board.get_dio_pins(0)
ir_tx = Pin(ir_tx, Pin.OUT)
# 创建ir_tx实例
ir_tx = NEC(ir_tx, freq=38000)

# 获取数字接口1的引脚编号
ir_rx , _ = board.get_dio_pins(1)
ir_rx = Pin(ir_rx, Pin.IN)
# 创建ir_rx实例
ir_rx = NEC_16(ir_rx, ir_callback)

# 获取I2C0 I2C1的引脚编号
i2c0_sda_pin , i2c0_scl_pin = board.get_i2c_pins(0)
i2c1_sda_pin , i2c1_scl_pin = board.get_i2c_pins(1)
# 创建I2C实例
i2c0 = I2C(id = 0, scl = i2c0_scl_pin, sda = i2c0_sda_pin, freq = I2C_FREQ)
i2c1 = I2C(id = 1, scl = i2c1_scl_pin, sda = i2c1_sda_pin, freq = I2C_FREQ)

pcf8574 = i2c_valid(i2c0, PCF8574_ADDR)
ssd1306 = i2c_valid(i2c1, SSD1306_ADDR)

pcf8574 = PCF8574(i2c0, pcf8574[0])
ssd1306 = SSD1306_I2C(i2c1, ssd1306[0], 128, 64, False)

pcf8574.port = 0xFF  # 设置PCF8574所有引脚为输入模式（上拉）
_init_display(ssd1306)

# 输出调试消息
print("All peripherals initialized.")

# ========================================  主程序  ===========================================
while True:
    now = time.ticks_ms()

    tmp = list(f"{pcf8574.port:08b}")
    tmp.reverse()
    
    bit_map = {0: 0, 2: 1, 5: 2, 7: 3}
    print(tmp)
    
    tx_index = None
    for i in bit_map:
        if tmp[i] == '0':
            tx_index = bit_map[i]

    # 每 3 秒触发一次发送（保持你原来的发送节奏）
    if time.ticks_diff(now, last_tx_time) > 3000:
        send_next()
        time.sleep_ms(500)

    # ----- 处理发送完成标志（由 send_next 设置） -----
    if tx_pending:
        # 消费该标志：更新 OLED 并记录更新时间以便 5s 后清除
        _update_tx_display(tx_letter)
        tx_pending = False
        tx_last_update = time.ticks_ms()  # 用当前时刻开始 5s 计时

    # ----- 处理接收完成标志（由 ir_callback 设置） -----
    if rx_pending:
        _update_rx_display(rx_letter)
        rx_pending = False
        rx_last_update = time.ticks_ms()  # 用当前时刻开始 5s 计时

    # ----- 定期检查是否需要清除 TX 区（5s 无新更新） -----
    if tx_last_update != 0 and time.ticks_diff(now, tx_last_update) >= TX_RX_CLEAR_MS:
        _clear_tx_area()
        tx_last_update = 0  # 重置，避免重复清除

    # ----- 定期检查是否需要清除 RX 区（5s 无新更新） -----
    if rx_last_update != 0 and time.ticks_diff(now, rx_last_update) >= TX_RX_CLEAR_MS:
        _clear_rx_area()
        rx_last_update = 0  # 重置

    # 小延时，避免忙循环（你可以调节 sleep 大小）
    time.sleep_ms(200)