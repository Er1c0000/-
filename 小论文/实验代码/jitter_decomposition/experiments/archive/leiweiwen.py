import numpy as np

# 假设 TIE 是你的抖动序列，bits 是对应的比特流
# M 是数据长度
M = len(TIE)
# K 是ISI考虑的比特位数，如论文所述取 3-10，这里设为 5
K = 5 
# PJ_freq 是已知的周期抖动频率（可以通过FFT预先分析TIE得到频谱峰值）
PJ_freq = 100e3 
Fs = 10e9 # 采样率/数据速率

# 1. 构建系数矩阵 H (参考论文公式 4-54 [cite: 1386])
# H 将包含三部分列：PJ部分, DCD部分, ISI部分
# 总列数 = 2(PJ sin/cos) + 1(DCD) + 2^(K-1)(ISI状态)

num_isi_cols = 2**(K-1) # 论文模型简化，只考虑前K位组合
H = np.zeros((M, 2 + 1 + num_isi_cols))

for i in range(K, M):
    t = i / Fs
    
    # --- PJ 部分 (公式 4-54 A矩阵) ---
    H[i, 0] = np.sin(2 * np.pi * PJ_freq * t)
    H[i, 1] = np.cos(2 * np.pi * PJ_freq * t)
    
    # --- DCD 部分 (公式 4-54 B矩阵) ---
    # 判断当前边沿是上升还是下降。假设 bits[i] != bits[i-1] 才有TIE
    # d_i = 1 (有跳变), 0 (无跳变)。这里假设只处理有跳变的点。
    # 论文用 cos(n*pi) 表示，实际就是 +1/-1 交替
    if bits[i] == 1 and bits[i-1] == 0: # 上升沿
        H[i, 2] = 1
    elif bits[i] == 0 and bits[i-1] == 1: # 下降沿
        H[i, 2] = -1
        
    # --- ISI 部分 (公式 4-54 C矩阵) ---
    # 获取前 K-1 位的历史 pattern 转为整数索引
    # 注意：论文 4.3.1.2 节提到 pattern 决定 ISI
    pattern = bits[i-K : i-1] 
    idx = 0
    for bit in pattern:
        idx = (idx << 1) | bit
    
    # 在对应的 ISI 列置 1
    if idx < num_isi_cols:
        H[i, 3 + idx] = 1

# 2. 移除全零行 (没有跳变沿的位置没有TIE数据)
valid_indices = np.where(np.abs(H[:, 2]) == 1)[0]
H_valid = H[valid_indices, :]
TIE_valid = TIE[valid_indices]

# 3. 最小二乘求解 (公式 4-56 [cite: 1412])
# theta = (H^T * H)^-1 * H^T * Z
# 在 Python 中推荐用 lstsq，数值稳定性更好
theta, residuals, rank, s = np.linalg.lstsq(H_valid, TIE_valid, rcond=None)

# 4. 提取结果
# PJ 幅度 (公式 4-58)
PJ_amp = np.sqrt(theta[0]**2 + theta[1]**2)
# DCD 值 (公式 4-64)
DCD_val = theta[2]
# ISI 峰峰值 (公式 4-65)
ISI_vals = theta[3:]
ISI_pkpk = np.max(ISI_vals) - np.min(ISI_vals)
# RJ (残差)
RJ_rms = np.std(residuals) # 或者根据公式 4-66 计算