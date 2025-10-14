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
    def __init__(self, PCF8574IO8, VibrationMotor, Buzzer, debug=True):
        self.PCF8574IO8 = PCF8574IO8
        self.VibrationMotor = VibrationMotor
        self.Buzzer = Buzzer
        self.debug = debug
        # 初始化按键状态默认2无效
        self.key = [2,2,2,2]
        self.Buzzer_hz = 0
        self.state = False

    def tick(self):
        #循环执行三次 读取按键状态
        for i in range(4):
            self.key[i] = self.PCF8574IO8.ports_state(i)
        if self.debug:
            print("key=",self.key)
        if self.key[0]== 1:
            self.VibrationMotor.on()
        if self.key[1] == 1:
            self.VibrationMotor.off()
        if self.key[2] == 1:
            self.state = True
            self.Buzzer_hz += 200
        if self.key[3] == 1:
            self.state = False
            self.Buzzer_hz = 0

        if self.state:
            self.Buzzer.play_tone(self.Buzzer_hz)
            if self.debug:
                print("Buzzer_hz=",self.Buzzer_hz)
        else:
            self.Buzzer.stop_tone()
            if self.debug:
                print("Buzzer_stop")





# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================