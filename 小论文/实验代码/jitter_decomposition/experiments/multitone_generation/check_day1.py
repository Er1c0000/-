import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# 尝试导入新的多频生成器
try:
    from tie_generate_multitone import generate_multitone_dataset
except ImportError:
    # 如果作为脚本直接运行导致路径问题，尝试添加当前目录
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from tie_generate_multitone import generate_multitone_dataset

def verify_day1():
    print("🚀 开始 Day 1 验证...")
    
    # Define output directory (Relative to CWD)
    output_dir = "Day1_Check"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 2. Generate dual-tone data
    print("正在生成双频数据...")
    
    filename = "test_dual_tone.csv"
    
    # 【关键修改】：调用新函数 generate_multitone_dataset
    csv_path = generate_multitone_dataset(
        filename=filename, 
        save_dir=output_dir, 
        pj_freqs=[100000, 110000], # 100kHz, 110kHz
        pj_amps=[10e-12, 10e-12],  # 10ps
        seed=42
    )
    
    print(f"数据已保存至: {csv_path}")
    
    # 3. FFT Analysis and Plotting
    print("正在分析数据...")
    df = pd.read_csv(csv_path)
    
    tie_data = df['TIE_Picoseconds'].values
    
    # Time domain plot (first 500 points)
    plt.figure(figsize=(12, 10))
    
    plt.subplot(2, 1, 1)
    plt.plot(tie_data[:500])
    plt.title("Time Domain Waveform (First 500 points)")
    plt.xlabel("Sample Index")
    plt.ylabel("TIE (ps)")
    plt.grid(True, alpha=0.3)
    
    # FFT Analysis
    N = len(tie_data)
    
    # Retrieve time stamps to estimate sampling rate
    # The csv has Edge_Index. Sample Rate of high-res is 80e9.
    time_vals = df['Edge_Index'].values / 80e9
    avg_dt = np.mean(np.diff(time_vals))
    fs_eff = 1.0 / avg_dt
    print(f"有效采样率: {fs_eff/1e6:.2f} MHz")
    
    # FFT
    yf = np.fft.fft(tie_data)
    xf = np.fft.fftfreq(N, d=avg_dt)
    
    # Normalize amplitude: 2/N * |FFT|
    amplitude = 2.0 / N * np.abs(yf)
    
    # Only positive frequencies
    idx_pos = np.where(xf >= 0)
    xf = xf[idx_pos]
    amplitude = amplitude[idx_pos]
    
    plt.subplot(2, 1, 2)
    plt.plot(xf, amplitude)
    plt.xlim(0, 200000) # 0 to 200kHz
    plt.title("FFT Spectrum (Resolution Challenge)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (ps)")
    plt.grid(True, alpha=0.3)
    
    # Mark theoretical positions
    plt.axvline(x=100000, color='r', linestyle='--', label='100 kHz')
    plt.axvline(x=110000, color='g', linestyle='--', label='110 kHz')
    plt.legend()
    
    save_plot_path = os.path.join(output_dir, "verification.png")
    plt.savefig(save_plot_path)
    print(f"图片已保存至: {save_plot_path}")
    print("✅ 验证完成！请检查图片确认 FFT 是否无法区分这两个频率。")

if __name__ == "__main__":
    verify_day1()