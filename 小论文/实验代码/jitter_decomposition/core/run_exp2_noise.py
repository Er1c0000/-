import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# 导入模型
from sbl_model import sbl_jitter_separation
from lasso_model import lasso_jitter_separation
from ls_model import ls_jitter_separation

def run_experiment_2():
    # 1. 设置路径
    data_dir = "datasets\synthetic\exp_noise"
    result_file = "results/experiment_2/exp2_noise_summary.csv"
    
    # 自动创建目录防报错
    if not os.path.exists(os.path.dirname(result_file)):
        os.makedirs(os.path.dirname(result_file))
    
    # 获取文件并按噪声大小排序
    files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    def parse_rj(fname):
        # 格式: noise_rj_1.0ps.csv
        return float(fname.replace("noise_rj_", "").replace("ps.csv", ""))
    
    files.sort(key=parse_rj)
    
    print(f"📦 准备处理 {len(files)} 个文件 (抗噪测试)...")
    
    results = []
    truth_pj = 15.0 # 真值
    
    for fname in files:
        rj_val = parse_rj(fname)
        file_path = os.path.join(data_dir, fname)
        
        print(f"🌊 处理噪声 RJ={rj_val}ps ...", end="", flush=True)
        
        # 训练长度 15000 足够
        curr_len = 15000
        
        # SBL
        res_sbl = sbl_jitter_separation(file_path, bit_rate=2e9, train_len=curr_len, silent=True)
        err_sbl = abs(res_sbl['pj_pkpk'] - truth_pj)
        
        # LASSO
        res_lasso = lasso_jitter_separation(file_path, bit_rate=2e9, train_len=curr_len, alpha=0.3, silent=True)
        err_lasso = abs(res_lasso['pj_pkpk'] - truth_pj)
        
        # LS
        res_ls = ls_jitter_separation(file_path, bit_rate=2e9, train_len=curr_len, silent=True)
        err_ls = abs(res_ls['pj_pkpk'] - truth_pj)
        
        print(f" [SBL误差: {err_sbl:.2f} | LS误差: {err_ls:.2f}]")
        
        results.append({
            'RJ_ps': rj_val,
            'Error_SBL': err_sbl,
            'Error_LASSO': err_lasso,
            'Error_LS': err_ls
        })
        
    # 保存与画图
    df = pd.DataFrame(results)
    df.to_csv(result_file, index=False)
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['RJ_ps'], df['Error_LS'], 's--', label='LS', color='gray')
    plt.plot(df['RJ_ps'], df['Error_LASSO'], 'o--', label='LASSO', color='blue')
    plt.plot(df['RJ_ps'], df['Error_SBL'], '*-', label='SBL', color='red', linewidth=2)
    
    plt.xlabel('Noise Level (RJ RMS in ps)')
    plt.ylabel('PJ Estimation Error (ps)')
    plt.title('Figure 2: Robustness against Noise')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig("results/experiment_2/fig2_noise_robustness.png", dpi=300)
    print(f"📊 图表已生成: results/fig2_noise_robustness.png")

if __name__ == "__main__":
    run_experiment_2()