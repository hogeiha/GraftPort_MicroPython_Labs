# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-
# @Time    : 2025/10/10 上午11:00
# @Author  : 侯钧瀚
# @File    : sensor_task.py
# @Description :   传感器任务，每200秒读取MQ-2 DO(低=检测到烟雾)火焰 DO（低=检测到火焰）。
# @License : CC BY-NC 4.0

# ======================================== 导入相关模块 =========================================

# 导入时间相关模块
import time

# ======================================== 全局变量 ============================================
# PLL 倍频系数 (25MHz * 15 = 375 MHz)
mul = 15
# 输出频率 2 MHz（最大 200 MHz）
freq = 2.0e6
# 正交输出标志（最低输出频率 = PLL / 128）
quadrature = True
# 反相输出标志（四相模式下忽略）
invert = False
# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

class sensorTask:
    """
    """
    def __init__(self, PCF8574Keys, SimpleOLEDMenu, SI5351_I2C, debug=True):
        self.PCF8574Keys = PCF8574Keys
        self.SimpleOLEDMenu = SimpleOLEDMenu
        self.SI5351_I2C = SI5351_I2C
        self.debug = debug
        self.SimpleOLEDMenu.add_menu("freq", enter_callback=self.show_freq)
        self.SimpleOLEDMenu.add_menu("output", enter_callback=self.sw_output)
        self.SimpleOLEDMenu.add_menu("open", enter_callback=self.show_output)
        self.SimpleOLEDMenu.add_menu("stop", enter_callback=self.show_stop)
        self.SimpleOLEDMenu.display_menu()
        self.SI5351_I2C.setup_pll(pll=0, mul=mul)
        self.SI5351_I2C.init_clock(output=0, pll=0)
        self.SI5351_I2C.init_clock(output=1, pll=0)
        self.SI5351_I2C.init_clock(output=2, pll=0)
        self.SI5351_I2C.disable_output(output=0)
        self.SI5351_I2C.disable_output(output=1)
        self.SI5351_I2C.disable_output(output=2)
        self.PCF8574Keys._pcf.port = 0b01000000
        self.freq =10
        self.output = 0

    def sw_output(self):
        self.SimpleOLEDMenu.show_message("output-{}".format(self.output))
    def show_freq(self):
        self.SimpleOLEDMenu.show_message("freq-{}Mhz".format(self.freq))
        self.SI5351_I2C.disable_output(output=self.output)
        self.SI5351_I2C.set_freq_fixedpll(output=self.output, freq=self.freq*1e6)
    def show_output(self):
        self.PCF8574Keys._pcf.port = 0b00000000
        self.SimpleOLEDMenu.show_message("{}Mhz-to-{}".format(self.freq,self.output))
        self.SI5351_I2C.enable_output(output=self.output)

    def show_stop(self):
        self.PCF8574Keys._pcf.port = 0b01000000
        self.SimpleOLEDMenu.show_message("stop")
        self.SI5351_I2C.disable_output(output=self.output)


    def tick(self):
        all_states = self.PCF8574Keys.read_all()
        # 低电平有效
        if not all_states['UP']:  # UP 按键
            self.SimpleOLEDMenu.select_up()
        elif not all_states['DOWN']:  # DOWN 按键
            self.SimpleOLEDMenu.select_down()
        elif not all_states['SW1']:  # SW1 - 确认/进入
            self.SimpleOLEDMenu.select_current()
        elif not all_states['SW2']:  # SW2 - 返回
            self.SimpleOLEDMenu.select_back()
        elif not all_states['LEFT']:  # SW2 - 返回
            if self.SimpleOLEDMenu.get_current_menu_name() == 'freq':
                self.freq -= 1
                self.freq = max(0, min(self.freq, 20))
            if self.SimpleOLEDMenu.get_current_menu_name() == 'output':
                self.output -= 1
                self.output = max(0, min(self.output, 3))
            self.SimpleOLEDMenu.select_current()
            self.SimpleOLEDMenu.select_current()
        elif not all_states['RIGHT']:  # SW2 - 返回
            if self.SimpleOLEDMenu.get_current_menu_name() == 'freq':
                self.freq += 1
                self.freq = max(0, min(self.freq, 20))
            if self.SimpleOLEDMenu.get_current_menu_name() == 'output':
                self.output += 1
                self.output = max(0, min(self.output, 3))
            self.SimpleOLEDMenu.select_current()


# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================