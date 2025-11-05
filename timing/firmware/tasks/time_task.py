# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2025/9/10 下午4:32   
# @Author  : 李清水            
# @File    : sensor_task.py       
# @Description : 每 200ms 读取超声波模块的测距距离、三点均值滤波、根据距离设置 LED 占空比与蜂鸣器频率（可调映射），支持 DEBUG 输出
# @License : CC BY-NC 4.0

# ======================================== 导入相关模块 =========================================

import time

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

class TimeTask:
    def __init__(self, ds1307, ssd1306, stop, buzzer):
        """构造参数:
        lora: HC14_Lora 实例（须提供发送/接收方法，代码中做了兼容处理）
        pcf8574: PCF8574 实例（需暴露 port 或 read()）
        ssd1306: SSD1306_I2C 实例（fill/text/show 等方法）
        """
        self.ds1307 = ds1307
        self.ssd1306 = ssd1306
        self.stop = stop
        self.buzzer = buzzer

        self._time = 20

    # -------------------- 调度器要调用的 tick() --------------------
    def second(self):

        """每秒调用一次"""
        self._time -= 1
        t = self.ds1307.datetime
        print("Current Time: %04d-%02d-%02d %02d:%02d:%02d" % (t[0], t[1], t[2], t[3], t[4], t[5]))
        self.ssd1306.fill(0)
        self.ssd1306.text("Time:", 0, 0)
        self.ssd1306.text("%04d-%02d-%02d" % (t[0], t[1], t[2]), 0, 16)
        self.ssd1306.text("%02d:%02d:%02d" % (t[3], t[4], t[5]), 0, 32)
        self.ssd1306.text(f"Alarm:%02d" % (self._time), 0, 48)
        self.ssd1306.show()

    def alarm(self):
        """每5秒调用一次"""
        if self._time <= 0:
            while self.stop.value() != 1:
                self.buzzer.value(1)
                time.sleep(0.1)
                self.buzzer.value(0)
                time.sleep(0.1)
            self._time = 20



        

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================