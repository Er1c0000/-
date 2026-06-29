# verify_tie_extraction.py
import numpy as np
import matplotlib.pyplot as plt
from pybert.pybert import PyBERT

def run_simulation_and_extract_tie():
    print("🚀 1. 启动 PyBERT 仿真...")
    
    # --- A. 设置 PyBERT ---
    bert = PyBERT()
    bert.bit_rate = 10.0    # 10 Gbps
    bert.nbits    = 5000    # 跑 5000 个比特
    bert.pattern_len = 7    # PRBS-7
    bert.pj_freq  = 20.0    # 20 MHz PJ
    bert.pj_amp   = 0.2     # 0.2 UI
    
    # 强制运行
    try:
        if hasattr(bert, 'simulate'):
            bert.simulate(None)
    except Exception:
        pass 

    if not hasattr(bert, 'chnl_out') or len(bert.chnl_out) == 0:
        print("❌ 严重错误：未能获取波形数据 (chnl_out)")
        return

    # 【修复】更稳健地获取采样率参数
    if hasattr(bert, 'spui'):
        samps_per_ui = bert.spui
    elif hasattr(bert, 'oversampling'):
        samps_per_ui = bert.oversampling
    else:
        print("⚠️ 未找到采样率参数，默认为 32")
        samps_per_ui = 32

    waveform = bert.chnl_out
    ui_period = 1.0 / (bert.bit_rate * 1e9) # 秒
    
    print(f"✅ 获取波形成功! 长度: {len(waveform)}")
    print(f"   -> 采样率: {samps_per_ui} pts/UI")

    # --- B. 核心算法：从波形提取 TIE ---
    print("⚙️ 2. 执行过零检测与 TIE 提取...")
    
    # 1. 过零检测
    # 找出信号穿过 0 电平的位置索引
    crossings_idx = np.where(np.diff(np.sign(waveform)))[0]
    
    # 2. 线性插值精确定位时间
    # t = t0 + (0 - y0) * (t1 - t0) / (y1 - y0)
    # 因为 t1 - t0 = 1 (采样点间隔), 所以简化为: fraction = -y0 / (y1 - y0)
    y0 = waveform[crossings_idx]
    y1 = waveform[crossings_idx + 1]
    
    # 避免除以零（极罕见情况）
    denominator = y1 - y0
    denominator[denominator == 0] = 1e-12 
    
    fraction = -y0 / denominator
    exact_crossing_time = (crossings_idx + fraction) * (ui_period / samps_per_ui)
    
    # 3. 恢复理想时钟 (CDR)
    if len(exact_crossing_time) < 2:
        print("❌ 错误：找到的过零点太少，无法计算 TIE")
        return

    # 简单线性拟合计算平均周期
    # (在实际CDR中会用锁相环，这里用统计平均即可)
    avg_period = np.mean(np.diff(exact_crossing_time))
    
    # 估算每个过零点对应的是第几个 UI
    # ideal_crossing_index = round(t / T_avg)
    estimated_ui_count = np.round(exact_crossing_time / avg_period)
    
    # 理想到达时间
    ideal_time = estimated_ui_count * avg_period
    
    # 移除常数相位偏差 (去直流)
    phase_offset = np.mean(exact_crossing_time - ideal_time)
    ideal_time += phase_offset
    
    # 4. 计算 TIE
    tie_seconds = exact_crossing_time - ideal_time
    tie_ui = tie_seconds / avg_period 

    print(f"✅ TIE 提取完成! 捕获到 {len(tie_ui)} 个边沿。")
    print(f"   -> TIE 峰峰值: {np.ptp(tie_ui):.4f} UI")

    # --- C. 可视化验证 ---
    plt.figure(figsize=(10, 5))
    # 只画前 200 个点，看得清楚正弦波
    plt.plot(tie_ui[:200], '.-', label='Extracted TIE')
    plt.title(f"Check: Is this a sine wave? (PJ Freq={bert.pj_freq} MHz)")
    plt.xlabel("Edge Index")
    plt.ylabel("TIE (UI)")
    plt.grid(True, alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    run_simulation_and_extract_tie()