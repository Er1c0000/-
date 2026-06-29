import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

# 忽略数值计算中的 RuntimeWarning
warnings.filterwarnings("ignore")

# 导入现有模型
from sbl_model import sbl_jitter_separation
from lasso_model import lasso_jitter_separation
from ls_model import ls_jitter_separation

# ==========================================
# 1. 设置：指定您的真实数据文件路径
# ==========================================
# 请确保这个路径是正确的，如果在 windows 下报错，尝试把 \ 改为 /
SOURCE_FILE = "datasets/synthetic/exp_freq/freq_100kHz.csv" 

def prepare_slice_data(full_df, filename, n_samples):
    """
    从完整数据中切出前 n_samples 行，并保存为临时文件供模型读取
    """
    # 1. 切片
    if n_samples > len(full_df):
        print(f"⚠️ 警告: 请求长度 {n_samples} 超过文件总长 {len(full_df)}，将使用全部数据。")
        df_slice = full_df.copy()
    else:
        df_slice = full_df.iloc[:n_samples].copy()
    
    # 2. 【关键安全检查】确保有 'Bit' 列
    # 如果您的原文件只有 TIE 没有 Bit (比如只为 SBL 生成的)，LS 会报错。
    # 这里我们自动补全一列随机 Bit，保证 LS 能跑通。
    if 'Bit' not in df_slice.columns:
        # print("  (自动补全 'Bit' 列以满足 LS 模型输入要求)")
        df_slice['Bit'] = np.random.randint(0, 2, len(df_slice))
        
    # 3. 保存临时文件
    df_slice.to_csv(filename, index=False)

# ==========================================
# 2. 主实验逻辑
# ==========================================
def run_runtime_experiment():
    print(f"⏱️ --- 开始 Experiment 4: 运行时间测试 (基于真实数据) ---")
    print(f"📂 读取源文件: {SOURCE_FILE}")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ 错误: 找不到文件 {SOURCE_FILE}")
        return

    # 读取完整数据
    try:
        full_df = pd.read_csv(SOURCE_FILE)
        print(f"✅ 读取成功，总数据量: {len(full_df)} 行")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return

    # 定义要测试的长度 N
    # SBL 比较慢，我们只测前 500 个点，足以画出趋势
    sample_sizes = [100, 200, 300, 400, 500]
    
    # 如果源文件不够长，就调整测试范围
    sample_sizes = [n for n in sample_sizes if n <= len(full_df)]
    
    n_repeats = 3 
    results = []
    temp_file = "temp_runtime_slice.csv"
    
    output_dir = "results/experiment_4"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for N in sample_sizes:
        print(f"\n📏 测试切片长度 N = {N} ...")
        
        # 准备切片数据
        prepare_slice_data(full_df, temp_file, n_samples=N)
        
        t_ls_sum = 0
        t_lasso_sum = 0
        t_sbl_sum = 0
        
        for i in range(n_repeats):
            print(f"   Run {i+1}/{n_repeats}...", end="", flush=True)
            
            # --- LS ---
            start = time.perf_counter()
            ls_jitter_separation(temp_file, bit_rate=2e9, train_len=N, silent=True)
            t_ls_sum += (time.perf_counter() - start)
            
            # --- LASSO ---
            start = time.perf_counter()
            lasso_jitter_separation(temp_file, bit_rate=2e9, train_len=N, alpha=0.1, silent=True)
            t_lasso_sum += (time.perf_counter() - start)
            
            # --- SBL ---
            start = time.perf_counter()
            sbl_jitter_separation(temp_file, bit_rate=2e9, train_len=N, silent=True)
            t_sbl_sum += (time.perf_counter() - start)
            
            print(" Done.")

        avg_ls = t_ls_sum / n_repeats
        avg_lasso = t_lasso_sum / n_repeats
        avg_sbl = t_sbl_sum / n_repeats
        
        print(f"   [平均耗时] LS: {avg_ls:.4f}s | LASSO: {avg_lasso:.4f}s | SBL: {avg_sbl:.4f}s")
        
        results.append({
            "Sample_Size": N,
            "Time_LS": avg_ls,
            "Time_LASSO": avg_lasso,
            "Time_SBL": avg_sbl
        })

    # 清理临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)

    # ==========================================
    # 3. 保存与绘图
    # ==========================================
    df_res = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, "runtime_comparison_realdata.csv")
    df_res.to_csv(csv_path, index=False)
    
    plt.figure(figsize=(8, 6))
    
    # 使用半对数坐标 (Y轴取对数)，因为 SBL 比 LS 慢几个数量级
    plt.semilogy(df_res['Sample_Size'], df_res['Time_LS'], 's--', color='gray', label='LS (FFT-based)')
    plt.semilogy(df_res['Sample_Size'], df_res['Time_LASSO'], 'o--', color='blue', label='LASSO')
    plt.semilogy(df_res['Sample_Size'], df_res['Time_SBL'], '*-', color='red', linewidth=2, label='SBL (Proposed)')
    
    plt.xlabel('Data Length (Number of Samples)')
    plt.ylabel('Execution Time (seconds) [Log Scale]')
    plt.title('Computational Complexity Comparison (Using Real Data Slice)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.3)
    
    plot_path = os.path.join(output_dir, "fig4_runtime.png")
    plt.savefig(plot_path, dpi=300)
    print(f"\n📊 图表已生成: {plot_path}")
    print("✅ 基于真实数据的运行时间测试完成！")

if __name__ == "__main__":
    run_runtime_experiment()