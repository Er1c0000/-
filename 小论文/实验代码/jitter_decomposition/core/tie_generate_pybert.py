import os
import time
import numpy as np
import pandas as pd
from pybert.pybert import PyBERT

# ================= 配置区域 =================
OUTPUT_DIR = "datasets/pybert_generated"

BASE_CONFIG = {
    'bit_rate': 25.78125,   # [Gbps]
    'nbits':    150000,      # [bits]
    'pattern':  13,         # PRBS-13
    'samps_per_ui': 32,     # 采样率
    'mod_type': 'NRZ',      # 明确指定字符串
}

SCENARIOS = [
    {'pj_freq': 4.3,   'pj_amp': 0.05, 'rj_rms': 0.002, 'case_name': 'LowFreq_4.3MHz'},
    {'pj_freq': 18.5,  'pj_amp': 0.05, 'rj_rms': 0.002, 'case_name': 'MidFreq_18.5MHz'},
    {'pj_freq': 87.0,  'pj_amp': 0.05, 'rj_rms': 0.002, 'case_name': 'HighFreq_87MHz'},
    {'pj_freq': 156.25, 'pj_amp': 0.05, 'rj_rms': 0.002, 'case_name': 'RefClk_156.25MHz'},
]
# ===========================================

def process_waveform(waveform, spui, ui_period):
    """
    核心处理函数：
    1. 提取 TIE (抖动)
    2. 恢复时钟
    3. 硬判决恢复比特流 (Hard Decision)
    """
    # --- 1. 过零检测 (用于 TIE) ---
    # 找到波形穿过 0 电平的位置
    sign_transitions = np.diff(np.sign(waveform))
    crossings_idx = np.where(sign_transitions)[0]
    
    if len(crossings_idx) < 100:
        return None

    # 线性插值精确定位过零点
    y0 = waveform[crossings_idx]
    y1 = waveform[crossings_idx + 1]
    denom = y1 - y0
    denom[denom == 0] = 1e-12
    fraction = -y0 / denom
    exact_crossing_time = (crossings_idx + fraction) * (ui_period / spui)
    
    # --- 2. 理想时钟恢复 (线性回归) ---
    edge_numbers = np.arange(len(exact_crossing_time))
    p = np.polyfit(edge_numbers, exact_crossing_time, 1)
    avg_period = p[0]
    start_offset = p[1]
    
    ideal_time_edges = edge_numbers * avg_period + start_offset
    tie_seconds = exact_crossing_time - ideal_time_edges
    tie_seconds = tie_seconds - np.mean(tie_seconds)
    
    # --- 3. 恢复比特流 (Hard Decision) ---
    # 我们不仅需要边沿处的 TIE，还需要知道这个边沿之前是什么比特 (用于 ISI 计算)
    # 策略：在每个理想 UI 的中心位置采样
    
    # 估算总比特数
    total_time = len(waveform) * (ui_period / spui)
    total_bits = int(total_time / avg_period)
    
    # 生成采样点时间 (UI中心: 0.5, 1.5, 2.5...)
    sample_times_ui = (np.arange(total_bits) + 0.5) * avg_period + start_offset
    # 转换为采样点索引
    sample_indices = np.round(sample_times_ui / (ui_period / spui)).astype(int)
    # 限制范围
    sample_indices = np.clip(sample_indices, 0, len(waveform) - 1)
    
    # 采样并判决 (>0 为 1, <0 为 0)
    recovered_bits = (waveform[sample_indices] > 0).astype(int)
    
    # --- 4. 关联 TIE 和 比特历史 ---
    # 计算每个边沿对应的 UI 索引 (Edge Index)
    # 例如：edge 0 发生在 bit 0 和 bit 1 之间 -> index 1 (approx)
    edge_ui_indices = np.round((exact_crossing_time - start_offset) / avg_period).astype(int)
    
    # 确保索引不越界
    edge_ui_indices = np.clip(edge_ui_indices, 1, len(recovered_bits) - 1)
    
    # 获取边沿类型 (Bit): Rising(0->1)=1, Falling(1->0)=0
    # 我们直接用边沿后的比特值来代表
    bits_at_edge = recovered_bits[edge_ui_indices]
    
    # 为了 SBL 的 DCD 矩阵构建：
    # SBL 代码里: col_dcd = np.where(bits == 1, 1.0, -1.0)
    # Rising Edge (0->1): 后一位是 1。
    # Falling Edge (1->0): 后一位是 0。
    # 所以 bits_at_edge 正好对应 Rising=1, Falling=0。符合 SBL 要求。

    return {
        'tie_seconds': tie_seconds,
        'edge_indices': edge_ui_indices,
        'bits_at_edge': bits_at_edge,
        'full_bit_stream': recovered_bits
    }

def run_single_case(config, k_isi=5):
    print(f"⚙️  正在运行: {config['case_name']} | Rate={BASE_CONFIG['bit_rate']}G | PJ={config['pj_freq']}MHz")
    
    # 1. 初始化 PyBERT
    bert = PyBERT()
    bert.bit_rate = BASE_CONFIG['bit_rate']
    bert.nbits    = BASE_CONFIG['nbits']
    bert.pattern_len = BASE_CONFIG['pattern']
    bert.samps_per_ui = BASE_CONFIG['samps_per_ui']
    bert.mod_type = BASE_CONFIG['mod_type'] # 直接使用 'NRZ'
    
    # 2. 应用抖动
    bert.pj_freq = config['pj_freq'] * 1e6
    bert.pj_amp  = config['pj_amp']
    bert.rn = 1e-3 # 极低底噪，利于硬判决恢复
    
    # 3. 运行仿真
    try:
        if hasattr(bert, 'run'): bert.run()
        elif hasattr(bert, 'simulate'): bert.simulate(initial_run=True)
        else:
            from pybert.results import calc_results
            calc_results(bert)
    except Exception:
        pass # 忽略非致命警告

    # 4. 获取波形
    waveform = getattr(bert, 'chnl_out', None)
    spui = getattr(bert, 'samps_per_ui', 32)
    ui_period = 1.0 / (bert.bit_rate * 1e9)
    
    if waveform is None:
        print("   ❌ 失败: 无法获取波形")
        return False

    # 5. 处理波形 (提取 TIE + 恢复比特)
    # --- 不再依赖 bert.tx_ids ---
    res = process_waveform(waveform, spui, ui_period)
    
    if res is None:
        print("   ❌ 失败: TIE 提取失败 (过零点不足)")
        return False

    # 6. 构建数据表
    df = pd.DataFrame({
        'Edge_Index': res['edge_indices'],
        'TIE_Seconds': res['tie_seconds'],
        'Bit': res['bits_at_edge']
    })
    
    # 添加 ISI 历史位 (从恢复的比特流中获取)
    full_stream = res['full_bit_stream']
    for k in range(1, k_isi + 1):
        # 边沿发生在 index 处，前一位是 index-1
        # 但因为 Edge_Index 是基于最近的 UI 网格，我们取:
        # Prev_1 = full_stream[edge_index - 1]
        prev_indices = (df['Edge_Index'] - k).astype(int)
        
        # 处理边界 (负索引设为0)
        prev_indices = np.clip(prev_indices, 0, len(full_stream)-1)
        
        df[f'Bit_Prev_{k}'] = full_stream[prev_indices]

    # 7. 保存
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    filename = os.path.join(OUTPUT_DIR, f"tie_{config['case_name']}.csv")
    df.to_csv(filename, index=False)
    
    pk_pk_ps = (np.max(res['tie_seconds']) - np.min(res['tie_seconds'])) * 1e12
    print(f"   ✅ 成功! 保存至: {filename}")
    print(f"      -> TIE 峰峰值: {pk_pk_ps:.3f} ps")
    return True

def main():
    print(f"🚀 开始模拟 (硬判决模式)，共 {len(SCENARIOS)} 个场景")
    print(f"📂 输出目录: {os.path.abspath(OUTPUT_DIR)}\n")
    
    start = time.time()
    count = 0
    for cfg in SCENARIOS:
        if run_single_case(cfg):
            count += 1
            
    print(f"\n🎉 结束! 成功: {count}/{len(SCENARIOS)}")
    print(f"⏱️  耗时: {time.time() - start:.2f} s")

if __name__ == '__main__':
    main()