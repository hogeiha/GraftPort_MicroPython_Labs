import math

class AudioFrequencyAnalyzer:
    def __init__(self, mic, sample_rate=1000, fft_size=64, alpha=0.995, notch_freq=50, q=5.0):
        self.mic = mic
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.alpha = alpha
        self.notch_freq = notch_freq
        self.q = q

        # 高通滤波
        self.dc_estimate = 0.0

        # 陷波器系数
        fs = sample_rate
        f0 = notch_freq
        w0 = 2 * math.pi * f0 / fs
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        alpha_n = sin_w0 / (2 * q)
        b0 = 1
        b1 = -2 * cos_w0
        b2 = 1
        a0 = 1 + alpha_n
        a1 = -2 * cos_w0
        a2 = 1 - alpha_n
        self.b0 = b0 / a0
        self.b1 = b1 / a0
        self.b2 = b2 / a0
        self.a1 = a1 / a0
        self.a2 = a2 / a0
        self.x1 = self.x2 = self.y1 = self.y2 = 0.0

        # 汉明窗
        self.window = [0.54 - 0.46 * math.cos(2 * math.pi * n / (fft_size - 1)) for n in range(fft_size)]

    def _fft_simple(self, x):
        N = len(x)
        if N <= 1:
            return x
        even = self._fft_simple(x[0::2])
        odd = self._fft_simple(x[1::2])
        T = [complex(math.cos(-2*math.pi*k/N), math.sin(-2*math.pi*k/N)) * odd[k] for k in range(N//2)]
        return [even[k] + T[k] for k in range(N//2)] + [even[k] - T[k] for k in range(N//2)]

    def sample_and_analyze(self):
        # 采样
        buffer = []
        for _ in range(self.fft_size):
            voltage = self.mic.read_voltage()
            self.dc_estimate = self.alpha * self.dc_estimate + (1 - self.alpha) * voltage
            ac = voltage - self.dc_estimate
            x0 = ac
            y0 = self.b0*x0 + self.b1*self.x1 + self.b2*self.x2 - self.a1*self.y1 - self.a2*self.y2
            self.x2, self.x1 = self.x1, x0
            self.y2, self.y1 = self.y1, y0
            buffer.append(y0)

        # 加窗、去均值
        win_data = [buffer[i] * self.window[i] for i in range(self.fft_size)]
        m = sum(win_data) / self.fft_size
        win_data = [v - m for v in win_data]

        # FFT
        spec = self._fft_simple(win_data)
        mags = [abs(c) for c in spec[:self.fft_size//2]]

        # 主频与能量
        peak_bin = mags.index(max(mags))
        freq = peak_bin * self.sample_rate / self.fft_size
        energy = sum([v*v for v in win_data])

        return {
            'frequency': freq,
            'energy': energy,
            'mags': mags,
            'peak_bin': peak_bin
        }
