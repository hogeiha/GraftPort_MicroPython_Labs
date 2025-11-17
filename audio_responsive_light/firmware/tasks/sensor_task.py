# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-
# @Time    : 2025/10/10 上午11:00
# @Author  : 侯钧瀚
# @File    : sensor_task.py
# @Description :   传感器任务，每200秒获取音频能量解析等级映射到八段数码管。
# @License : CC BY-NC 4.0

# ======================================== 导入相关模块 =========================================

# 导入时间相关模块
import time

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

class micTask:
    """
           任务1：每 200ms 运行一次
       构造参数：
           AudioFrequencyAnalyzer: AudioFrequencyAnalyzer 实例，提供 sample_and_analyze()
          LEDBar: LEDBar 实例，提供 display_level()
    """
    def __init__(self,AudioFrequencyAnalyzer, LEDBar,debug=True):
        self.AudioFrequencyAnalyzer = AudioFrequencyAnalyzer
        self.LEDBar = LEDBar
        self.debug = debug


    def tick(self):
        """
        调度器每 200ms 调用一次：
        1)从AudioFrequencyAnalyzer读取音频频率分析数据
        2)通过LEDBar显示音频能量等级
        """
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