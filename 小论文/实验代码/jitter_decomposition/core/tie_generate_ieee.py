import numpy as np
import pandas as pd
import skrf as rf
from scipy import stats
import matplotlib.pyplot as plt
import os

def prbs(taps, n_bits):
    """生成 PRBS 序列"""
    reg_len = max(taps)
    register = np.ones(reg_len, dtype=int)
    feedback_taps = [tap - 1 for tap in taps]
    bits = []
    for _ in range(n_bits):
        feedback_val = np.bitwise_xor.reduce(register[feedback_taps])
        bits.append(register[-1])
        register[1:] = register[:-1]
        register[0] = feedback_val
    return np.array(bits)

def create_channel(freq_hz, f_nyquist, s_params_file=None):
    """创建或加载信道并返回冲激响应"""
    if not s_params_file or not os.path.exists(s_params_file):
        print("⚠️ 使用虚拟模型...")
        loss_db = 25 * np.sqrt(freq_hz / f_nyquist)
        s21_mag = 10**(-loss_db / 20.0)
        s21_phase = -2 * np.pi * freq_hz * 2e-9 # 2ns 延迟
        s21_complex = s21_mag * np.exp(1j * s21_phase)
    else:
        print(f"🔌 加载 S-参数: {os.path.basename(s_params_file)}")
        nw = rf.Network(s_params_file)
        if nw.nports == 4:
            nw.se2gmm(p=2)
            s21_orig = nw.s[:, 1, 0]
        else:
            s21_orig = nw.s[:, 1, 0]
        
        mag_orig = np.abs(s21_orig)
        phase_orig = np.unwrap(np.angle(s21_orig))
        s21_mag = np.interp(freq_hz, nw.f, mag_orig, right=0)
        s21_phase = np.interp(freq_hz, nw.f, phase_orig)
        s21_complex = s21_mag * np.exp(1j * s21_phase)

    s21_complex[0] = np.abs(s21_complex[0])
    impulse_response = np.fft.irfft(s21_complex)
    return impulse_response

def generate_waveform_and_tie(
    bit_rate=25e9, 
    sample_rate=200e9, 
    num_bits=20000, 
    pattern_type='prbs13', 
    s_params_file=None,
    rj_rms=0.3e-12, 
    pj_freq=1e4,
    pj_amp=1.5e-12, 
    snr_db=38
):
    ui = 1 / bit_rate
    dt = 1 / sample_rate
    
    # 1. 生成比特
    taps = [13, 12, 2, 1] if pattern_type == 'prbs13' else [31, 28]
    bits = prbs(taps, num_bits)
    
    # 2. Tx 端注入抖动
    ideal_edges = np.arange(num_bits + 1) * ui
    rj = np.random.normal(0, rj_rms, len(ideal_edges))
    pj = (pj_amp) * np.sin(2 * np.pi * pj_freq * ideal_edges)
    total_jitter = rj + pj
    jittered_edges = ideal_edges + total_jitter
    
    # 3. 生成 Tx 波形
    total_time = num_bits * ui
    time_axis = np.arange(0, total_time, dt)
    tx_waveform = np.zeros_like(time_axis)
    edge_idx_in_time = np.searchsorted(time_axis, jittered_edges)
    for i in range(len(edge_idx_in_time) - 1):
        start = edge_idx_in_time[i]
        end = edge_idx_in_time[i+1]
        tx_waveform[start:end] = bits[i] - 0.5

    # 4. 信道卷积与加噪
    freq_axis = np.linspace(0, sample_rate / 2, 2**14)
    channel_ir = create_channel(freq_axis, bit_rate/2, s_params_file)
    peak_sample = np.argmax(np.abs(channel_ir))
    
    waveform_after = np.convolve(tx_waveform, channel_ir, mode='full')[:len(time_axis)]
    sig_p = np.mean(waveform_after**2)
    noise = np.random.normal(0, np.sqrt(sig_p / (10**(snr_db/10))), len(waveform_after))
    final_waveform = waveform_after + noise

    # 5. TIE 提取与去趋势
    crossings = np.where(np.diff(np.sign(final_waveform)))[0]
    edge_bits_indices = np.where(np.diff(bits) != 0)[0] + 1
    
    actual_t = []
    ideal_t = []
    bit_values = []
    
    for eb in edge_bits_indices:
        target_t = eb * ui + (peak_sample * dt)
        nearest_cross_idx = crossings[np.argmin(np.abs(crossings * dt - target_t))]
        t1, v1 = nearest_cross_idx * dt, final_waveform[nearest_cross_idx]
        t2, v2 = (nearest_cross_idx + 1) * dt, final_waveform[nearest_cross_idx + 1]
        t_actual = t1 - v1 * (t2 - t1) / (v2 - v1)
        
        actual_t.append(t_actual)
        ideal_t.append(eb * ui)
        bit_values.append(bits[eb])

    actual_t = np.array(actual_t)
    ideal_t = np.array(ideal_t)
    raw_tie = actual_t - ideal_t
    
    # 线性去趋势
    slope, intercept, _, _, _ = stats.linregress(np.arange(len(raw_tie)), raw_tie)
    corrected_tie = raw_tie - (slope * np.arange(len(raw_tie)) + intercept)

    return {
        'time': time_axis,
        'waveform': final_waveform,
        'tie_s': corrected_tie,
        'tie_ps': corrected_tie * 1e12,
        'edge_index': edge_bits_indices,
        'bits_at_edges': bit_values,
        'all_bits': bits, # Return all bits
        'ui': ui
    }

if __name__ == "__main__":
    # --- 1. 设置路径 ---
    output_dir = os.path.join("datasets","synthetic", "ieee")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 已创建目录: {output_dir}")

    s4p_path = "assets\s_params\dataset_ieee/tracy_3ck_02_0119_orthoBP\DPO_IL_12dB\DPO_4in_Meg7_THRU.s4p"
    
    # --- 2. 运行仿真 ---
    res = generate_waveform_and_tie(s_params_file=s4p_path, pj_freq=4e6)

    # --- 3. 保存 TIE 数据到 CSV ---
    df = pd.DataFrame({
        'TIE_Seconds': res['tie_s'],
        'TIE_Picoseconds': res['tie_ps'],
        'Bit': res['bits_at_edges'],
        'Edge_Index': res['edge_index']
    })
    
    # 提取历史比特
    history_depth = 10
    all_bits = res['all_bits']
    final_indices = res['edge_index']
    for k in range(1, history_depth + 1):
        # Ensure indices do not go below zero
        prev_indices = np.maximum(final_indices - k, 0)
        # Handle the case where edge index is smaller than k
        # For now, we take from the start of the sequence if index is too small
        df[f'Bit_Prev_{k}'] = all_bits[prev_indices]

    csv_path = os.path.join(output_dir, "tie_data.csv")
    # Reorder columns to match the reference format
    column_order = ['TIE_Seconds', 'TIE_Picoseconds', 'Bit', 'Edge_Index'] + [f'Bit_Prev_{k}' for k in range(1, history_depth + 1)]
    df = df[column_order]
    
    df.to_csv(csv_path, index=False, float_format='%.6e')
    print(f"💾 数据已保存至: {csv_path}")

    # --- 4. 绘图并保存 ---
    plt.figure(figsize=(12, 10))
    
    # 眼图
    plt.subplot(2, 1, 1)
    eye_span = 2 * res['ui']
    num_segments = 500
    for i in range(100, 100 + num_segments):
        start_t = i * 2 * res['ui']
        idx = (res['time'] >= start_t) & (res['time'] < start_t + eye_span)
        plt.plot(res['time'][idx] - start_t, res['waveform'][idx], 'b-', alpha=0.1)
    plt.title("Fixed Eye Diagram (Aligned)")
    plt.grid(True)

    # TIE
    plt.subplot(2, 1, 2)
    plt.plot(res['edge_index'], res['tie_ps'])
    plt.title("Corrected TIE (Linear Trend Removed) - PJ=4MHz")
    plt.ylabel("TIE (ps)")
    plt.xlabel("Edge Index")
    plt.grid(True)

    plt.tight_layout()
    
    # 保存图片
    img_path = os.path.join(output_dir, "analysis_plot.png")
    plt.savefig(img_path, dpi=300)
    print(f"📊 图表已保存至: {img_path}")
    
    plt.show()
