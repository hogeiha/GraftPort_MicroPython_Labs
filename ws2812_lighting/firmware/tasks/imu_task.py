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

class ImuTask:
    def __init__(self, imu, nm):
        """
        Args:
            imu (IMU): 陀螺仪对象（带 RecvData()）
            nm (NeopixelMatrix): LED 矩阵对象
        """
        self.imu = imu
        self.nm = nm

        # 图案坐标与图案数据
        self.pos_x = 0
        self.pos_y = 0
        self.pattern = self._make_pattern()

        # 初始化显示
        self._draw_pattern()

    def _make_pattern(self):
        """创建一个简单图案，比如中心方块 3x3"""
        pattern = []
        for y in range(2):
            row = []
            for x in range(2):
                row.append(self.nm.COLOR_RED)  # 红色 RGB565
            pattern.append(row)
        return pattern

    def _draw_pattern(self):
        """将当前图案绘制到 nm 上"""
        self.nm.fill(self.nm.COLOR_BLUE)  # 清屏
        for j, row in enumerate(self.pattern):
            for i, color in enumerate(row):
                x = self.pos_x + i
                y = self.pos_y + j
                if 0 <= x < self.nm.width and 0 <= y < self.nm.height:
                    self.nm.pixel(x, y, color)
        self.nm.show()

    def tick(self):
        """每次调用由调度器执行，周期 2000ms，但内部自行限制 300ms 更新"""
        self.imu.RecvData()
        roll = self.imu.angle_x   # 横滚角（左右）
        pitch = self.imu.angle_y   # 俯仰角（前后）
        
        print("左右", roll)
        print("前后", pitch)

        # 简单映射角度到移动方向
        if pitch > 180:
            self.pos_y = max(0, self.pos_y - 1)  # 向上
        elif pitch < 180:
            self.pos_y = min(self.nm.height - 2, self.pos_y + 1)  # 向下

        if roll > 180:
            self.pos_x = min(self.nm.width - 2, self.pos_x + 1)   # 向右
        elif roll < 180:
            self.pos_x = max(0, self.pos_x - 1)  # 向左

        self._draw_pattern()




        

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================