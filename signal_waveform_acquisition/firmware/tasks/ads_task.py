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


class ADSTask:
    def __init__(self, signal, ssd1306, width=128, height=64, top_margin=10):
        """
        signal: ADS1115 实例 (具有 read(rate, channel1, channel2) 和 raw_to_v(raw))
        ssd1306: OLED 实例 (常见接口: fill, pixel, text, show)
        width, height: 屏幕分辨率（默认 128x64）
        top_margin: 顶部留给文本的像素高度
        """
        self.signal = signal
        self.ssd = ssd1306
        self.W = width
        self.H = height
        self.top = top_margin

        # 波形绘制区域高度（包含 top 到 H-1）
        self.plot_h = self.H - self.top

        # 环形缓冲，初始化为中线（屏幕坐标）
        mid = self.top + (self.plot_h // 2)
        self.buf = [mid] * self.W
        self.idx = 0  # 指向将要写入的位置（写入后 idx 增一）

        # 显示与采样参数（可按需调整）
        self.adc_rate = 4         # 对应 ADS1115.RATES 索引（保留）
        self.adc_channel = 0      # 采样通道
        self.raw_max = 32767      # 单端最大原始值（可修改）
        self.raw_min = 0

        # 调试
        self.last_v = 0.0
        self.last_raw = 0

    def immediate_off(self):
        """暂停/关闭时调用：清屏并显示 PAUSED"""
        try:
            self.ssd.fill(0)
            txt = "PAUSED"
            x = max((self.W - len(txt) * 8) // 2, 0)
            y = max((self.H - 8) // 2, 0)
            try:
                self.ssd.text(txt, x, y)
            except Exception:
                pass
            self.ssd.show()
        except Exception:
            pass

    def _map_raw_to_y(self, raw):
        """
        将 raw (raw_min..raw_max) 映射到屏幕坐标 y（top..H-1）。
        设计：raw 越大 y 越小（靠上），返回整型 y。
        """
        if raw is None:
            raw = self.raw_min
        # 限幅
        if raw < self.raw_min:
            raw = self.raw_min
        if raw > self.raw_max:
            raw = self.raw_max

        span = max(1, (self.raw_max - self.raw_min))
        ratio = (raw - self.raw_min) / span  # 0..1
        # invert so larger raw -> smaller y (更靠上)
        y = self.top + int((1.0 - ratio) * (self.plot_h - 1))
        # 保证在 [top, H-1]
        if y < self.top:
            y = self.top
        if y > (self.H - 1):
            y = self.H - 1
        return y

    # -------------------- 调度器要调用的 tick() --------------------
    def tick(self):
        """
        每次调度调用：采样 ADS1115，更新缓冲并重绘 OLED。
        尽量短小，捕获异常，避免在 ISR 或调度器中崩溃。
        """
        try:
            # 配置与读取（保留你原接口）
            self.signal.set_conv(rate=7, channel1=self.adc_channel)
            raw = self.signal.read_rev()
            self.last_raw = raw
            # 转换电压（如果接口有）
            self.last_v = self.signal.raw_to_v(self.last_raw)

            # 映射到屏幕 Y 坐标（整型）
            y = self._map_raw_to_y(self.last_raw)

            # 推入缓冲：写入当前 idx，然后移动 idx（环形）
            self.buf[self.idx] = int(y)
            self.idx += 1
            if self.idx >= self.W:
                self.idx = 0

            # 绘制：先清屏，写文本，再绘制波形
            try:
                self.ssd.fill(0)
            except Exception:
                pass

            # 顶部显示数值
            try:
                txt1 = "R:{:6d}".format(int(self.last_raw))
                txt2 = "{:.3f}V".format(self.last_v)
                self.ssd.text(txt1, 0, 0)
                x_right = max(self.W - len(txt2) * 8, 0)
                self.ssd.text(txt2, x_right, 0)
            except Exception:
                pass

            # 画波形（从左到右）：缓冲中的点顺序为 oldest..newest,
            # 当前 idx 指向下一个写入位置（即 newest+1）
            seq = self.buf[self.idx:] + self.buf[:self.idx]

            # 绘制连线
            prev_y = seq[0]
            for x in range(1, self.W):
                cur_y = seq[x]
                self.ssd.line(x - 1, prev_y, x, cur_y, 1)

                prev_y = cur_y

            # 刷新屏幕
            try:
                self.ssd.show()
            except Exception:
                pass

        except Exception:
            # 外层保护：任何异常都不要抛回调度器
            try:
                # 尝试至少刷新一次界面提示错误
                self.ssd.fill(0)
                self.ssd.text("ERR", 0, 0)
                self.ssd.show()
            except Exception:
                pass

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================
