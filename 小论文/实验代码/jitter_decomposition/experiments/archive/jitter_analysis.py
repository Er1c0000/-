import numpy as np
import pywt  # 小波变换库（抖动分解核心）

# 生成模拟的示波器抖动信号
t = np.linspace(0, 1, 1000, endpoint=False)
signal = np.sin(2 * np.pi * 5 * t)  # 5Hz正弦信号
noise = 0.1 * np.random.randn(1000)  # 随机噪声（模拟抖动）
jitter_signal = signal + noise

print("模拟抖动信号生成完成，长度：", len(jitter_signal))  