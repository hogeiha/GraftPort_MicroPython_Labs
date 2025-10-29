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

class DhtOledTask:
    """
    """
    def __init__(self, DHT22, MQX, SSD1306_I2C, debug=True):
        self.DHT22 = DHT22
        self.MQX = MQX
        self.SSD1306_I2C = SSD1306_I2C
        self.debug = debug
        self.last_mq2_ao = None
        self.last_temp = None
        self.last_humi = None
        self._counter = 0


    def tick(self):

        self._counter += 1
        if self._counter >= 10:
            self.DHT22.measure()
            self._counter = 0
        mq2_ao = self.MQX.comp_pin.value() # 数字输出引脚，低电平表示检测到烟雾
        temp = self.DHT22.temperature()  # 温度（摄氏度）
        humi = self.DHT22.humidity()  # 湿度（百分比）

        if self.debug:
            print("Temperature: {:.1f}°C, Humidity: {:.1f}%, MQ-2 AO: {}".format(temp, humi, mq2_ao))
        if(mq2_ao != self.last_mq2_ao or temp != self.last_temp or humi != self.last_humi):
            self.SSD1306_I2C.fill(0)
            self.SSD1306_I2C.show()
            # (0,0)原点位置为屏幕左上角，右边为x轴正方向，下边为y轴正方向
            # 显示文本
            self.SSD1306_I2C.text(f"Temp:{temp:.1f} C", 0, 5)
            self.SSD1306_I2C.text(f"RH:{humi}%", 0, 15)
            if mq2_ao:
                self.SSD1306_I2C.text("MQ-2:Normal", 0, 25)
            else:
                self.SSD1306_I2C.text("MQ-2:Smoke!", 0, 25)
            # 显示图像
            self.SSD1306_I2C.show()
            self.last_mq2_ao = mq2_ao
            self.last_temp = temp
            self.last_humi = humi




# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================