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

class TofTask:
    def __init__(self, tof, nm):
        """
        Args:
            tof: 距离传感器对象，提供 read() -> 距离（单位同原代码，假设 mm）
            nm: NeopixelMatrix 对象，提供 fill(), text(), show(), width, COLOR_* 常量
        """
        self.tof = tof
        self.nm = nm
        self.text = "Welcome to GXCVU"
        self.pos = self.nm.width   # 从屏幕最右边开始滚动

        # 定时控制（均以 ms 为单位，使用 ticks_* API）
        self.active_until = 0          # ticks_ms 时间点，表示保持显示到此时间点（含）
        self.last_scroll = 0           # 上次滚动更新时间
        self.scroll_period_ms = 50     # 字符滚动更新周期（可调）

        # 失活后闪烁绿光控制
        self.flash_interval_ms = 10000  # 每隔 10s 闪一次
        self.flash_duration_ms = 300    # 绿光闪烁持续时间（ms）
        self.last_flash = 0             # 上次闪烁触发时间（或进入失活时设置为 now）
        self.flash_end = 0              # 正在闪烁时的结束时间点；为 0 表示当前不在闪烁

        # 当前是否处于“显示活动（有人）”状态的快速标记（便于 reset 等）
        self.body = False

    def _now(self):
        return time.ticks_ms()

    def _start_active(self, now):
        # 检测到人，刷新保持窗口（10s）
        self.active_until = time.ticks_add(now, 10000)  # 保持 10000ms
        self.body = True
        # 进入活动时，取消任何失活闪烁状态
        self.last_flash = 0
        self.flash_end = 0

    def _show_display(self, now):
        # 只按 scroll_period_ms 更新显示与位置，避免每次 tick 都重绘太频繁
        if time.ticks_diff(now, self.last_scroll) >= self.scroll_period_ms:
            self.nm.fill(self.nm.COLOR_RED)
            self.nm.text(self.text, self.pos, 0, self.nm.COLOR_BLUE)
            self.nm.show()

            self.pos -= 1
            text_length = len(self.text) * 8  # 假设每字符宽度 8 像素
            if self.pos < -text_length:
                self.pos = self.nm.width

            self.last_scroll = now

    def _start_flash(self, now):
        # 开始一次绿光闪烁（短时）
        self.nm.fill(self.nm.COLOR_GREEN)
        self.nm.show()
        self.flash_end = time.ticks_add(now, self.flash_duration_ms)
        # 记录本次闪烁触发时间（用于间隔计时）
        self.last_flash = now

    def _end_flash(self):
        # 结束闪烁，熄灭（保持黑色）
        self.nm.fill(0)
        self.nm.show()
        self.flash_end = 0

    def tick(self):
        """每次由调度器调用（应被频繁调用，例如每 50ms 左右）"""
        now = self._now()

        # 读取距离（注意：传感器读取可能阻塞/耗时，取决实现）
        distance = self.tof.read()

        # 如果检测到人在 2m 内 -> 刷新/延长活动窗口
        if distance <= 2000:
            self._start_active(now)

        # 如果仍在 active 窗口内（有人刚走但在 10s 保持期内） -> 持续显示
        if time.ticks_diff(self.active_until, now) > 0:
            # 活动显示
            self._show_display(now)
        else:
            # 已失活（超过 10s 没人）
            if self.body:
                # 刚从活动切换到失活：记录切换时间，使下一次闪烁在 10s 后
                self.last_flash = now
            self.body = False

            # 先处理正在进行的闪烁（若在闪烁期则等待结束）
            if self.flash_end:
                if time.ticks_diff(now, self.flash_end) >= 0:
                    # 闪烁时间到 -> 结束闪烁
                    self._end_flash()
            else:
                # 非闪烁状态，判断是否到达下次闪烁时间点
                if self.last_flash == 0:
                    # 若从未设置过 last_flash（设备刚上电或刚构造），设置为 now
                    self.last_flash = now
                elif time.ticks_diff(now, self.last_flash) >= self.flash_interval_ms:
                    # 到达间隔 -> 发起一次绿光闪烁
                    self._start_flash(now)

    def reset(self):
        """重置任务状态（例如系统重启或需要手动复位）"""
        self.pos = self.nm.width
        self.body = False
        self.active_until = 0
        self.last_scroll = 0
        self.last_flash = 0
        self.flash_end = 0
        # 显示一次绿色短提示然后清屏（可选）
        self.nm.fill(self.nm.COLOR_GREEN)
        self.nm.show()
        time.sleep(0.2)
        self.nm.fill(0)
        self.nm.show()


        

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================