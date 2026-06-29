import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import time
import multiprocessing  # 导入多进程模块
from functools import partial
import sys

# Get the absolute path of the current script file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to get the project root directory
project_root = os.path.dirname(os.path.dirname(current_dir))
# Add the project root to the Python path
sys.path.insert(0, project_root)

from core.sbl_model import sbl_jitter_separation

# 设置绘图风格
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 定义单次实验的工作函数
# ==========================================
def worker_task(task_params, datasets_dir, true_vals):
    """
    单个进程执行的任务：加载数据 + 运行SBL
    task_params: (freq, repeat_idx)
    """
    freq, i = task_params
    TRUE_PJ_PKPK, TRUE_RJ_RMS, TRUE_DCD = true_vals
    
    freq_label = f"{int(freq/1e3)}kHz" if freq < 1e6 else f"{freq/1e6:.1f}MHz"
    
    try:
        # 1. 加载数据
        filename = f"tie_data_{freq_label}_rep{i}.csv"
        file_path = os.path.join(datasets_dir, filename)
        
        if not os.path.exists(file_path):
            return {"error": f"Data file not found: {filename}. Please run generate_experiment_data.py first."}
        
        # 2. 运行 SBL 算法 (必须设为 silent=True，否则多进程打印会错乱)
        metrics = sbl_jitter_separation(file_path, train_len=140000, silent=True)
        
        if metrics:
            return {
                "注入PJ频率": freq_label,
                "Frequency_Hz": freq,
                "Repeat": i,
                "注入PJ(ps)": TRUE_PJ_PKPK,
                "SBL预测PJ(ps)": metrics['pj_pkpk'],
                "PJ误差(ps)": abs(metrics['pj_pkpk'] - TRUE_PJ_PKPK),
                "注入RJ(ps)": TRUE_RJ_RMS,
                "SBL预测RJ(ps)": metrics['rj_rms'],
                "RJ误差(ps)": abs(metrics['rj_rms'] - TRUE_RJ_RMS),
                "注入DCD(ps)": TRUE_DCD,
                "SBL预测DCD(ps)": metrics['dcd'],
                "DCD误差(ps)": abs(metrics['dcd'] - TRUE_DCD)
            }
    except Exception as e:
        return {"error": f"Freq {freq_label} Rep {i}: {str(e)}"}
    return None

# ==========================================
# 2. 主实验逻辑
# ==========================================
def run_accuracy_experiment_parallel():
    # 实验参数
    frequencies = [10e3, 50e3, 100e3, 500e3, 1e6, 5e6, 10e6]
    repeats = 5
    true_vals = (15.0, 2.0, 1.0) # PJ, RJ, DCD
    
    # 路径准备
    output_dir = "results/accuracy"
    datasets_dir = os.path.join(output_dir, "datasets")
    plots_dir = os.path.join(output_dir, "plots")
    for d in [datasets_dir, plots_dir]:
        if not os.path.exists(d): os.makedirs(d)

    # 构造任务列表
    tasks = [(f, i) for f in frequencies for i in range(repeats)]
    
    print(f"🚀 开始并行实验...")
    print(f"💻 检测到 CPU 核心数: {multiprocessing.cpu_count()}")
    print(f"📦 待处理任务总数: {len(tasks)}")

    start_time = time.time()

    # 使用进程池执行任务
    # processes 参数建议设为核心数的 80%，避免系统卡死
    # num_cpus = max(1, multiprocessing.cpu_count() - 2)
    num_cpus = 6
    
    results = []
    # 使用 partial 固定不变的参数
    func = partial(worker_task, datasets_dir=datasets_dir, true_vals=true_vals)
    
    with multiprocessing.Pool(processes=num_cpus) as pool:
        # 使用 imap 可以配合 tqdm 显示进度条
        for res in tqdm(pool.imap_unordered(func, tasks), total=len(tasks), desc="并行计算中"):
            if res and "error" not in res:
                results.append(res)
            elif res and "error" in res:
                print(f"\n❌ {res['error']}")

    duration = time.time() - start_time
    print(f"\n✅ 实验完成! 总耗时: {duration:.2f} 秒")
    
    # 保存与可视化
    df_results = pd.DataFrame(results)
    df_results.to_csv(os.path.join(output_dir, "accuracy_results.csv"), index=False)
    visualize_results(df_results, plots_dir)

def visualize_results(df, save_dir):
    print("🎨 正在生成可视化图表...")
    
    # 按频率分组计算平均误差和标准差
    grouped = df.groupby('Frequency_Hz').agg({
        'PJ误差(ps)': ['mean', 'std'],
        'RJ误差(ps)': ['mean', 'std'],
        'DCD误差(ps)': ['mean', 'std'],
        '注入PJ频率': 'first'  # 保留标签
    }).reset_index()
    
    # 扁平化列名
    grouped.columns = ['Frequency_Hz', 'PJ_Error_Mean', 'PJ_Error_Std', 
                       'RJ_Error_Mean', 'RJ_Error_Std', 
                       'DCD_Error_Mean', 'DCD_Error_Std', 'Label']
    
    # 确保按频率排序
    grouped = grouped.sort_values('Frequency_Hz')
    labels = grouped['Label']
    x = np.arange(len(labels))
    width = 0.25

    # --- 1. 误差条形图 ---
    plt.figure(figsize=(12, 6))
    
    plt.bar(x - width, grouped['PJ_Error_Mean'], width, label='PJ Error', yerr=grouped['PJ_Error_Std'], capsize=5, alpha=0.8)
    plt.bar(x, grouped['RJ_Error_Mean'], width, label='RJ Error', yerr=grouped['RJ_Error_Std'], capsize=5, alpha=0.8)
    plt.bar(x + width, grouped['DCD_Error_Mean'], width, label='DCD Error', yerr=grouped['DCD_Error_Std'], capsize=5, alpha=0.8)
    
    plt.xlabel('Frequency')
    plt.ylabel('Absolute Error (ps)')
    plt.title('SBL Estimation Error by Frequency (Mean ± Std)')
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'error_bar_chart.png'), dpi=300)
    plt.close()
    
    # --- 2. 真值 vs 估计值 散点图 (PJ) ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Frequency_Hz', y='SBL预测PJ(ps)', hue='注入PJ频率', s=100)
    plt.axhline(y=15.0, color='r', linestyle='--', label='Ground Truth (15.0 ps)')
    plt.xscale('log')
    plt.ylabel('Estimated PJ (ps)')
    plt.title('PJ Estimation vs Frequency')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'pj_estimation_scatter.png'), dpi=300)
    plt.close()

    print(f"🖼️ 图表已保存至: {save_dir}")

if __name__ == "__main__":
    # 在 Windows 系统下使用多进程，必须放在 __main__ 中运行
    run_accuracy_experiment_parallel()
