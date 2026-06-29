import numpy as np
import pandas as pd
from scipy import signal
import os

# ==========================================
# 1. 核心生成引擎 (修复版：增加过零检测)
# ==========================================
def generate_flexible_data(filename, save_dir, pj_config, rj_rms=2.0e-12, seed=42):
    """
    参数说明:
    pj_config: 可以是单个频率(float)，或者是列表 [(freq1, amp1), (freq2, amp2)...]
    rj_rms: 随机抖动 RMS 值 (秒)
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    print(f"🚀 生成: {filename} | RJ={rj_rms*1e12:.2f}ps | PJ配置={pj_config}")

    # --- 保持 2Gbps 基准参数 ---
    bit_rate = 2e9          
    ui_width = 1 / bit_rate # 500 ps
    sample_rate = 80e9      
    dt = 1 / sample_rate
    num_bits = 300000       
    sps = int(sample_rate / bit_rate)

    # 生成比特
    np.random.seed(seed)
    bits = np.random.randint(0, 2, num_bits)
    transition_mask = np.diff(bits) != 0
    edges_indices = np.where(transition_mask)[0] + 1
    aligned_bits = bits[edges_indices]
    num_edges = len(edges_indices)
    ideal_edge_times = edges_indices * ui_width

    # --- 注入抖动 ---
    
    # A. PJ (支持单音或多音)
    pj_jitter = np.zeros(num_edges)
    if isinstance(pj_config, (float, int)):
        freq = pj_config
        amp = 7.5e-12 
        pj_jitter = amp * np.sin(2 * np.pi * freq * ideal_edge_times)
    elif isinstance(pj_config, list):
        for (f, a) in pj_config:
            pj_jitter += a * np.sin(2 * np.pi * f * ideal_edge_times)

    # B. RJ
    rj_jitter = np.random.normal(0, rj_rms, num_edges)

    # C. DCD
    dcd_val = 1.0e-12
    dcd_jitter = np.where(aligned_bits == 1, dcd_val/2, -dcd_val/2)

    # D. ISI (修复核心逻辑)
    waveform_ideal = np.repeat(bits, sps).astype(float) - 0.5
    f_cutoff = 2e9
    nyquist = sample_rate / 2
    b, a = signal.bessel(4, f_cutoff / nyquist, 'low')
    waveform_isi = signal.lfilter(b, a, waveform_ideal)
    
    isi_ties = []
    
    # 【修复点】 必须在窗口内搜索过零点，且必须检查符号翻转
    for edge_idx in edges_indices:
        center_sample = edge_idx * sps
        # 搜索范围 +/- 3 个采样点，应对 filter group delay
        search_range = range(center_sample - 3, center_sample + 3)
        
        found_crossing = False
        t_offset = 0.0
        
        for i in search_range:
            if i + 1 >= len(waveform_isi): break
            y1 = waveform_isi[i]
            y2 = waveform_isi[i+1]
            
            # 只有当符号不同（穿过零点）时才计算
            if np.sign(y1) != np.sign(y2): 
                # 线性插值
                if y2 - y1 != 0:
                    delta_t = -y1 / (y2 - y1) * dt
                    # 实际过零时刻 = i*dt + delta_t
                    # 理想时刻 = edge_idx * sps * dt
                    # TIE = 实际 - 理想 = (i - edge_idx*sps)*dt + delta_t
                    t_offset = (i - center_sample) * dt + delta_t
                    found_crossing = True
                    break
        
        if found_crossing:
            isi_ties.append(t_offset)
        else:
            isi_ties.append(0.0) # 没找到过零点，设为0 (避免爆炸)

    isi_jitter = np.array(isi_ties)
    isi_jitter = isi_jitter - np.mean(isi_jitter) # 去直流

    # 合成
    min_len = min(len(pj_jitter), len(isi_jitter))
    total_tie = (pj_jitter[:min_len] + rj_jitter[:min_len] + 
                 dcd_jitter[:min_len] + isi_jitter[:min_len])
    
    # 保存
    df = pd.DataFrame({
        'TIE_Seconds': total_tie,
        'TIE_Picoseconds': total_tie * 1e12,
        'Bit': aligned_bits[:min_len],
        'Edge_Index': edges_indices[:min_len]
    })
    
    # 历史比特
    for k in range(1, 11):
        prev_indices = np.maximum(edges_indices[:min_len] - k, 0)
        df[f'Bit_Prev_{k}'] = bits[prev_indices]

    full_path = os.path.join(save_dir, filename)
    df.to_csv(full_path, index=False)

# ==========================================
# 2. 批量执行逻辑 (保持不变)
# ==========================================
if __name__ == "__main__":
    base_dir = "datasets/synthetic"
    
    print("\n📦 --- 正在生成 Experiment 1 (频率扫描) ---")
    freqs = [10e3, 100e3, 500e3, 1e6, 5e6, 10e6, 15e6]
    for f in freqs:
        name = f"freq_{f/1e6:.1f}MHz.csv" if f>=1e6 else f"freq_{int(f/1e3)}kHz.csv"
        generate_flexible_data(name, os.path.join(base_dir, "exp_freq"), f, 2.0e-12)

    print("\n📦 --- 正在生成 Experiment 2 (抗噪测试) ---")
    rj_list_ps = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0] 
    for rj_ps in rj_list_ps:
        generate_flexible_data(f"noise_rj_{rj_ps:.1f}ps.csv", os.path.join(base_dir, "exp_noise"), 1e6, rj_ps*1e-12)

    print("\n📦 --- 正在生成 Experiment 3 (双音测试) ---")
    generate_flexible_data("dual_tone_1.0M_1.2M.csv", os.path.join(base_dir, "exp_dual"), [(1e6, 4e-12), (1.2e6, 4e-12)], 2.0e-12)

    print("\n✅ 修复版数据生成完毕！")