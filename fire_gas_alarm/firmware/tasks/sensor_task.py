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

class GasFireAlarmTask:
    """
    每 200 秒读取 MQ-2 DO(低=检测到烟雾)火焰 DO（低=检测到火焰）。
    每5s钟检查一次，如果两个传感器都检测到正常状态，则关闭报警LED。
    如果任一传感器检测到异常状态且报警未触发，则点亮报警LED
    """
    def __init__(self, mq2, flame_sensor, led, debug=True):
        self.mq2 = mq2
        self.flame_sensor = flame_sensor
        self.led = led
        self.debug = debug
        self.alarm = False
        self._counter = 0


    def tick(self):

        try:
            mq2_ao = self.mq2.comp_pin.value()
            flame_do = self.flame_sensor.is_flame_detected()
            if self.debug:
                print("mq2_ao:", mq2_ao, "flame_do:", flame_do)
        except Exception as e:
            if self.debug:
                print("sensor read error:", e)
        self._counter += 1
        if self._counter >= 25:
            # 这里写每5秒执行一次的代码
            if self.mq2.comp_pin.value() and self.flame_sensor.is_flame_detected():
                self.led.off()
                if self.debug:
                    print("led.off")
                self.alarm = False

            self._counter = 0
        try:
            if (self.mq2.comp_pin.value()==0 or self.flame_sensor.is_flame_detected()==0)and self.alarm == False:
                self.led.set_brightness(30)
                self.alarm = True
        except Exception as e:
            if self.debug:
                print("LED error:", e)
            return
# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================