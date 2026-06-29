import numpy as np
import pandas as pd
from scipy import signal
import os
import matplotlib.pyplot as plt

def generate_aligned_dataset(filename="experiment_tie_data.csv", save_dir="Least Squares", pj_freq=100e3, seed=42):
    """
    生成单次实验数据。
    filename: 保存的文件名
    save_dir: 保存目录
    pj_freq: PJ 频率 (Hz)
    """
    # 确保目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    print(f"🚀 生成数据: {filename} (Freq: {pj_freq/1e3:.1f} kHz, Seed: {seed}) -> {save_dir}")
    
    # ================= 1. 基础参数设置 =================
    bit_rate = 2e9          # 2 Gbit/s
    ui_width = 1 / bit_rate # 500 ps
    sample_rate = 80e9      # 80 Gbit/s (过采样)
    dt = 1 / sample_rate
    num_bits = 300000       # 300k bits
    sps = int(sample_rate / bit_rate) 
    
    # ================= 2. 生成随机比特流 =================
    np.random.seed(seed)
    bits = np.random.randint(0, 2, num_bits)
    
    transition_mask = np.diff(bits) != 0
    edges_indices = np.where(transition_mask)[0] + 1
    aligned_bits = bits[edges_indices]
    num_edges = len(edges_indices)
    ideal_edge_times = edges_indices * ui_width

    # ================= 3. 注入抖动分量 =================
    
    # --- A. PJ (周期性抖动) ---
    pj_amp = 15e-12 / 2
    pj_jitter = pj_amp * np.sin(2 * np.pi * pj_freq * ideal_edge_times)
    
    # --- B. RJ (随机抖动) ---
    rj_jitter = np.random.normal(0, 2.0e-12, num_edges)
    
    # --- C. DCD (占空比失真) ---
    dcd_val = 1.0e-12
    dcd_jitter = np.where(aligned_bits == 1, dcd_val/2, -dcd_val/2)
    
    # --- D. ISI (码间干扰) ---
    waveform_ideal = np.repeat(bits, sps).astype(float) - 0.5
    f_cutoff = 2e9
    nyquist = sample_rate / 2
    b, a = signal.bessel(4, f_cutoff / nyquist, 'low')
    waveform_isi = signal.lfilter(b, a, waveform_ideal)
    
    isi_ties = []
    for edge_idx in edges_indices:
        sample_idx = edge_idx * sps
        search_range = 3
        found = False
        for i in range(sample_idx - search_range, sample_idx + search_range):
            if i+1 >= len(waveform_isi): break
            y1 = waveform_isi[i]
            y2 = waveform_isi[i+1]
            if np.sign(y1) != np.sign(y2):
                t1 = i * dt
                t2 = (i+1) * dt
                t_zero = t1 - y1 * (t2 - t1) / (y2 - y1)
                t_ideal = edge_idx * ui_width
                isi_ties.append(t_zero - t_ideal)
                found = True
                break
        if not found: isi_ties.append(0.0)
            
    isi_jitter = np.array(isi_ties)
    isi_jitter = isi_jitter - np.mean(isi_jitter)

    # ================= 4. 合成与保存 =================
    min_len = min(len(pj_jitter), len(isi_jitter))
    total_tie = (pj_jitter[:min_len] + rj_jitter[:min_len] + 
                 dcd_jitter[:min_len] + isi_jitter[:min_len])
    
    final_indices = edges_indices[:min_len]
    final_bits = aligned_bits[:min_len]
    
    df = pd.DataFrame({
        'TIE_Seconds': total_tie,
        'TIE_Picoseconds': total_tie * 1e12,
        'Bit': final_bits,
        'Edge_Index': final_indices
    })
    
    # 提取历史比特
    history_depth = 10
    for k in range(1, history_depth + 1):
        prev_indices = np.maximum(final_indices - k, 0)
        df[f'Bit_Prev_{k}'] = bits[prev_indices]

    full_path = os.path.join(save_dir, filename)
    df.to_csv(full_path, index=False, float_format='%.6e')
    return full_path

def batch_generate(frequencies, output_dir="datasets"):
    """
    批量生成不同频率的数据集
    """
    print(f"📦 开始批量生成 {len(frequencies)} 个数据集...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for freq in frequencies:
        # 文件名格式: tie_data_10kHz.csv, tie_data_1.5MHz.csv
        if freq < 1e6:
            name_freq = f"{int(freq/1e3)}kHz"
        else:
            name_freq = f"{freq/1e6:.1f}MHz"
            
        filename = f"tie_data_{name_freq}.csv"
        generate_aligned_dataset(filename=filename, save_dir=output_dir, pj_freq=freq)
        
    print("✅ 批量生成完成！")

if __name__ == "__main__":
    # 定义要生成的频率列表
    freq_list = [10e3, 50e3, 100e3, 500e3, 1e6, 5e6, 10e6]
    batch_generate(freq_list)
