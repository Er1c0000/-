import numpy as np
import pandas as pd
from scipy import signal
import os

def generate_multitone_dataset(filename="experiment_tie_data.csv", 
                               save_dir="Day1_Check", 
                               pj_freqs=[100e3, 110e3], # 默认双频
                               pj_amps=[10e-12, 10e-12], # 默认各10ps
                               seed=42):
    """
    生成包含多个频率分量(Multi-tone)的抖动数据，用于超分辨率实验。
    
    参数:
    pj_freqs: 频率列表 (Hz)，例如 [100e3, 110e3]
    pj_amps:  幅度列表 (秒)，例如 [10e-12, 10e-12]
    """
    # 确保目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    print(f"🚀 [Multi-Tone] 生成数据: {filename}")
    print(f"    -> 注入频率: {[f'{f/1e3:.1f}k' for f in pj_freqs]} Hz")
    
    # ================= 1. 基础参数设置 =================
    bit_rate = 2e9          # 2 Gbit/s
    sample_rate = 80e9      # 80 Gbit/s (过采样，用于模拟连续波形)
    dt = 1 / sample_rate
    num_bits = 300000       # 300k bits (足够覆盖低频特性)
    sps = int(sample_rate / bit_rate) # Samples per symbol = 40
    
    # ================= 2. 生成随机比特流 =================
    np.random.seed(seed)
    bits = np.random.randint(0, 2, num_bits)
    
    # 上采样比特流 (生成理想波形的时间基准)
    # tx_signal = np.repeat(bits, sps) # 仅用于参考，实际不需要生成全长波形数组以省内存
    
    # 生成时间轴
    # 注意：为了节省内存，我们只在需要的地方计算时间
    total_samples = num_bits * sps
    time_vector = np.arange(total_samples) * dt
    
    # ================= 3. 生成抖动分量 =================
    
    # --- A. 周期性抖动 (PJ) - 多频叠加核心逻辑 ---
    pj_jitter = np.zeros_like(time_vector)
    
    # 校验输入
    if len(pj_freqs) != len(pj_amps):
        raise ValueError("❌ 频率列表和幅度列表的长度必须一致！")
        
    for f, amp in zip(pj_freqs, pj_amps):
        # 为每个分量生成随机初始相位，模拟真实非相干源
        phase = np.random.uniform(0, 2*np.pi) 
        pj_jitter += amp * np.sin(2 * np.pi * f * time_vector + phase)

    # --- B. 随机抖动 (RJ) ---
    rj_rms = 2e-12 # 2ps RMS
    rj_jitter = np.random.normal(0, rj_rms, len(time_vector))
    
    # --- C. 占空比失真 (DCD) ---
    dcd_amp = 1e-12 # 1ps
    # 模拟：高电平(1)持续时间变长，低电平(0)变短
    # 上采样后的比特流
    tx_signal_upsampled = np.repeat(bits, sps)
    # 根据电平极性施加偏移
    dcd_jitter = np.where(tx_signal_upsampled > 0.5, dcd_amp, -dcd_amp)
    
    # --- D. 码间干扰 (ISI) ---
    # 简单的 ISI 模拟：卷积一个指数衰减或特定模式的核
    isi_kernel = np.array([0.5, -0.2, 0.1]) * 5e-12 
    # 在比特层级卷积
    isi_bits_noise = np.convolve(bits, isi_kernel, mode='same')
    # 上采样对齐到时间轴
    isi_jitter = np.repeat(isi_bits_noise, sps)
    isi_jitter = isi_jitter[:len(time_vector)] # 修正长度

    # ================= 4. 合成总抖动 =================
    # Total Jitter (TJ) = PJ + RJ + DCD + ISI
    total_jitter = pj_jitter + rj_jitter + dcd_jitter + isi_jitter
    
    # ================= 5. 提取 TIE (模拟示波器边沿采样) =================
    # 找到理想边沿位置 (index)
    bit_edges = np.diff(bits)
    edge_indices_bits = np.where(bit_edges != 0)[0] + 1 # 边沿所在的 bit index
    
    # 理想边沿在 time_vector 中的索引
    ideal_indices = edge_indices_bits * sps
    
    # 防止索引越界
    ideal_indices = ideal_indices[ideal_indices < len(total_jitter)]
    
    # 在理想边沿位置采样 Jitter 值，作为 TIE (Time Interval Error)
    extracted_ties = total_jitter[ideal_indices]
    aligned_bits = bits[edge_indices_bits[:len(ideal_indices)]] # 对应的比特值
    
    # ================= 6. 保存数据 =================
    # 限制保存长度，防止文件过大 (保留前 20000 个边沿足够实验用)
    max_edges = 20000
    if len(extracted_ties) > max_edges:
        extracted_ties = extracted_ties[:max_edges]
        ideal_indices = ideal_indices[:max_edges]
        aligned_bits = aligned_bits[:max_edges]
        
    # 为了验证精度，我们把 PJ 的真值也存下来
    pj_truth = pj_jitter[ideal_indices]
    
    df = pd.DataFrame({
        'TIE_Seconds': extracted_ties,
        'TIE_Picoseconds': extracted_ties * 1e12,
        'Bit': aligned_bits,
        'Edge_Index': ideal_indices,
        'True_PJ': pj_truth, # 用于后续计算误差
    })
    
    # 添加历史比特 (用于构建 ISI 字典)
    history_depth = 10
    for k in range(1, history_depth + 1):
        # 对应的 bit index 往前推 k 位
        # 注意：这里要用 edge_indices_bits，不是 ideal_indices
        curr_bit_indices = edge_indices_bits[:len(extracted_ties)]
        prev_indices = np.maximum(curr_bit_indices - k, 0)
        df[f'Bit_Prev_{k}'] = bits[prev_indices]

    full_path = os.path.join(save_dir, filename)
    df.to_csv(full_path, index=False, float_format='%.6e')
    
    print(f"✅ [Done] 数据已保存至: {full_path} (Edges: {len(df)})")
    return full_path