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

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

class sensorTask:
    """
    """
    def __init__(self,BH1750, LEDBar,debug=True):
        self.BH1750 = BH1750
        self.LEDBar = LEDBar
        self.debug = debug
        self.BH1750.configure(
            measurement_mode=BH1750.MEASUREMENT_MODE_ONE_TIME,
            resolution=BH1750.RESOLUTION_HIGH,
            measurement_time=69
        )

    def tick(self):
        lux = self.BH1750.measurement
        print("One-time lux =", int(lux))
        if int(lux) >= 2000:
            lux = 2000
        if 0 <= int(lux/250) <= 8:
            self.LEDBar.display_level(int(lux/250))




# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================