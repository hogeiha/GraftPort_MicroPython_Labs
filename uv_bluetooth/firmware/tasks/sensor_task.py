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

class uvOledTask:
    """
       任务1：每 200ms 运行一次
       构造参数：
           HC08: HC08 实例，提供 send_data()
           GUVA_S12SD: GUVA_S12SD 实例，提供 uvi
          SSD1306_I2C: SSD1306_I2C 实例，提供 show()/fill()/text()
           enable_debug, min_dist, max_dist
       """
    def __init__(self, HC08, GUVA_S12SD, SSD1306_I2C, debug=True):
        self.HC08 = HC08
        self.GUVA_S12SD = GUVA_S12SD
        self.SSD1306_I2C = SSD1306_I2C
        self.debug = debug
        self.firstset = True
        # 记录上一次的UV值，初始化为1是确保第一次读取时会更新显示
        self.uv_last = 1

        self.uv_level = 0


    def tick(self):
        """
         调度器每 200ms 调用一次：
        1)从GUVA_S12SD读取uv光强

        """
        # 获取uv传感器光照强度
        self.uv_level = self.GUVA_S12SD.uvi
        # 更新数据包
        hcdata = bytes([0xA5, self.uv_level, self.uv_level, 0x5A])
        # 发送数据包
        self.HC08.send_data(hcdata)
        if self.debug:
            print("UV Level:", self.uv_level)
        # 当uv强度有变化
        if self.uv_level != self.uv_last:
            # 首先清除屏幕
            self.SSD1306_I2C.fill(0)
            self.SSD1306_I2C.show()
            # (0,0)原点位置为屏幕左上角，右边为x轴正方向，下边为y轴正方向
            # 显示文本与参数
            self.SSD1306_I2C.text(f"UV Level:{str(self.uv_level)}", 0, 5)
            # 显示图像
            self.SSD1306_I2C.show()
            # 刷新uv_last
            self.uv_last = self.uv_level




# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================