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
    def __init__(self, PIRSensor, BusPWMServoController, debug=True):
        self.PIRSensor = PIRSensor
        self.BusPWMServoController = BusPWMServoController
        self.debug = debug
        self.BusPWMServoController.attach_servo(0, BusPWMServoController.SERVO_180, min_us=500, max_us=2500, neutral_us=1500)
        self.BusPWMServoController.attach_servo(1, BusPWMServoController.SERVO_180, min_us=500, max_us=2500, neutral_us=1500)
    def tick(self):
        if self.PIRSensor.is_motion_detected():
            if self.debug:
                print("检测到人体")
            self.BusPWMServoController.set_angle(0, 90)
            self.BusPWMServoController.set_angle(1, 90)
            time.sleep(1)
            self.BusPWMServoController.set_angle(0, 0)
            self.BusPWMServoController.set_angle(1, 0)
            time.sleep(1)
            self.BusPWMServoController.set_angle(0, 90)
            self.BusPWMServoController.set_angle(1, 90)
            time.sleep(1)
            self.BusPWMServoController.set_angle(0, 0)
            self.BusPWMServoController.set_angle(1, 0)








# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================