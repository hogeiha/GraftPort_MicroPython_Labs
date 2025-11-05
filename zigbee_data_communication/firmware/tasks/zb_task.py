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

class ZBTask:
    def __init__(self, ssd1306, cor, rou):
        """构造参数:
        lora: HC14_Lora 实例（须提供发送/接收方法，代码中做了兼容处理）
        pcf8574: PCF8574 实例（需暴露 port 或 read()）
        ssd1306: SSD1306_I2C 实例（fill/text/show 等方法）
        """
        self.ssd1306 = ssd1306
        self.cor = cor
        self.rou = rou

    def _update_tx_display(self, text):
        # 清除 TX 区再写入
        self.ssd1306.fill_rect(30, 40, 90, 10, 0)
        self.ssd1306.text(text, 30, 40)
        self.ssd1306.show()

    def _update_rx_display(self, text):
        # 清除 RX 区再写入
        self.ssd1306.fill_rect(30, 52, 90, 10, 0)
        self.ssd1306.text(text, 30, 52)
        self.ssd1306.show()

    # -------------------- 调度器要调用的 tick() --------------------
    def tick(self):

        tx_index = 0
        
        self.rou.send_node_to_coord(f'{tx_index}')
        self._update_tx_display(chr(ord('a') + tx_index))
        #time.sleep(0.2)
        if self.cor._uart.any():
            resp = self.cor._uart.read().decode('utf-8')
        #resp = self.cor.recv_frame()[1].decode('utf-8')
        self._update_rx_display(chr(ord('a') + int(resp)))




        

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================