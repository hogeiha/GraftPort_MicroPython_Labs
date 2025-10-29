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

class DHT11fanTask:
    """
    该类用于控制DHT11温湿度传感器、雾化器和风扇。
    主要功能：每次调用tick方法时，读取两次温湿度数据，根据温度≥30℃或湿度≥70%来控制风扇转速和雾化器开关，
    并可选打印当前温湿度。 、
    """
    def __init__(self, DHT11, atomizer, fan, debug=True):
        self.DHT11 = DHT11
        self.atomizer = atomizer
        self.fan = fan
        self.debug = debug
        self.alarm = False


    def tick(self):
        for i in range(2):
            self.DHT11.measure
            time.sleep(2)
        temperature = self.DHT11.temperature
        humidity = self.DHT11.humidity
        if self.debug:
            # 打印温湿度数据
            print("temperature: {}℃, humidity: {}%".format(temperature, humidity))
        if temperature >= 30 or humidity >= 70:
            self.fan.set_speed(1023)
            self.atomizer.on()

        else:
            self.fan.set_speed(0)
            self.atomizer.off()
# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================