import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# 导入三个核心模型
from sbl_model import sbl_jitter_separation
from lasso_model import lasso_jitter_separation
from ls_model import ls_jitter_separation

def run_experiment_1():
    # 1. 设置路径
    data_dir = "datasets\synthetic\exp_freq"
    result_file = "results/experiment_1/exp1_freq_summary.csv"
    
    if not os.path.exists("results"): os.makedirs("results")
    
    # 获取所有频率文件并排序
    files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    # 按照频率大小排序 (文件名解析)
    def parse_freq(fname):
        name = fname.replace("freq_", "").replace(".csv", "")
        if "MHz" in name: return float(name.replace("MHz", "")) * 1e6
        if "kHz" in name: return float(name.replace("kHz", "")) * 1e3
        return 0
    
    files.sort(key=parse_freq)
    
    print(f"📦 准备处理 {len(files)} 个文件 (频率扫描)...")
    
    results = []
    
    # 2. 循环处理
    for fname in files:
        f_val = parse_freq(fname)
        file_path = os.path.join(data_dir, fname)
        
        print(f"🏃‍♂️ 正在处理: {fname} ...", end="",flush=True)
        
        # 设定真值 (根据 tie_generate.py)
        # 单音 PJ 幅度 = 7.5ps => PkPk = 15.0 ps
        truth_pj = 15.0
        
        # --- 运行 SBL ---
        t0 = time.time()
        res_sbl = sbl_jitter_separation(file_path, bit_rate=2e9, train_len=50000, silent=True)
        t_sbl = time.time() - t0
        err_sbl = abs(res_sbl['pj_pkpk'] - truth_pj)
        
        # --- 运行 LASSO ---
        res_lasso = lasso_jitter_separation(file_path, bit_rate=2e9, train_len=50000, alpha=0.5, silent=True)
        err_lasso = abs(res_lasso['pj_pkpk'] - truth_pj)
        
        # --- 运行 LS ---
        res_ls = ls_jitter_separation(file_path, bit_rate=2e9, train_len=50000, silent=True)
        err_ls = abs(res_ls['pj_pkpk'] - truth_pj)
        
        print(f" [Done] SBL误差: {err_sbl:.2f}ps | LASSO误差: {err_lasso:.2f}ps")
        
        results.append({
            'Freq_Hz': f_val,
            'Freq_MHz': f_val / 1e6,
            'Error_SBL': err_sbl,
            'Error_LASSO': err_lasso,
            'Error_LS': err_ls,
            'Time_SBL': t_sbl
        })
        
    # 3. 保存结果
    df_res = pd.DataFrame(results)

    output_dir = os.path.dirname(result_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📂 已自动创建目录: {output_dir}")

    df_res.to_csv(result_file, index=False)
    print(f"\n✅ 实验完成! 结果已保存至 {result_file}")
    
    # 4. 自动画图 (预览)
    plt.figure(figsize=(10, 6))
    plt.plot(df_res['Freq_MHz'], df_res['Error_LS'], 's--', label='LS (Least Squares)', color='gray', alpha=0.5)
    plt.plot(df_res['Freq_MHz'], df_res['Error_LASSO'], 'o--', label='LASSO (alpha=0.1)', color='blue', alpha=0.7)
    plt.plot(df_res['Freq_MHz'], df_res['Error_SBL'], '*-', label='SBL (Proposed)', color='red', linewidth=2)
    
    plt.xlabel('PJ Frequency (MHz)')
    plt.ylabel('PJ Estimation Error (ps)')
    plt.title('Figure 1: PJ Amplitude Estimation Accuracy vs Frequency')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()
    plt.xscale('log') # 对数坐标看低频更清楚
    
    img_path = "results/experiment_1/fig1_freq_accuracy.png"
    plt.savefig(img_path, dpi=300)
    print(f"📊 图表已生成: {img_path}")
    plt.show()

if __name__ == "__main__":
    run_experiment_1()