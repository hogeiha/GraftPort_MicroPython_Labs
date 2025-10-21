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

class micTask:
    """
    """
    def __init__(self,AudioFrequencyAnalyzer, LEDBar,debug=True):
        self.AudioFrequencyAnalyzer = AudioFrequencyAnalyzer
        self.LEDBar = LEDBar
        self.debug = debug


    def tick(self):

        x = self.AudioFrequencyAnalyzer.mic.read_normalized()  # 读取归一化后的信号（建议范围 0~1 或 -1~1）
        result = self.AudioFrequencyAnalyzer.sample_and_analyze()
        # 输出格式：原始值 高通值 （空格分隔）
        print("{:.4f}".format(result['energy']))
        # 控制绘图刷新速率（建议 >= 200Hz）
        if int(result['energy'])>= 8:
            ledlevel=8
        else:
            ledlevel=int(result['energy'])
        self.LEDBar.display_level(ledlevel)


# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================