import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 导入模型
from sbl_model import sbl_jitter_separation
from lasso_model import lasso_jitter_separation
from ls_model import ls_jitter_separation

def run_experiment_3():
    # 1. 设置路径 (使用 run_all_experiments 生成的双音数据)
    file_path = "datasets\synthetic\exp_dual\dual_tone_1.0M_1.2M.csv" 
    
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return

    print(f"⚔️  开始双音分辨测试: 1.0MHz vs 1.2MHz ...")
    
    # 2. 运行三个模型
    # 增加 grid 密度以分辨双音 (这步很关键)
    # 我们手动构造一个覆盖 1.0 和 1.2 的高分辨率网格
    f_dense = np.arange(0.5e6, 2.0e6, 0.02e6) # 20kHz 步长
    
    # SBL
    print("⏳ SBL running...")
    res_sbl = sbl_jitter_separation(file_path, bit_rate=2e9, train_len=30000, silent=False, f_candidates=f_dense)
    
    # LASSO
    print("⏳ LASSO running...")
    res_lasso = lasso_jitter_separation(file_path, bit_rate=2e9, train_len=30000, alpha=0.1, silent=True, f_candidates=f_dense)
    
    # LS
    print("⏳ LS running...")
    res_ls = ls_jitter_separation(file_path, bit_rate=2e9, train_len=30000, silent=True, f_candidates=f_dense)
    
    # 3. 画频谱对比图 (论文核心图)
    plt.figure(figsize=(10, 5))
    
    # 提取系数 (假设模型内部没有返回 weights，这里简单模拟可视化逻辑)
    # 为了画图，我们需要修改模型让它返回 weights，或者简单地信任 SBL 的结果
    # 这里我们只打印结果，您可以去 sbl_model 内部把 plot 打开
    
    print("\n" + "="*40)
    print("📊 双音测试结果 (真值: 1.0MHz & 1.2MHz)")
    print("="*40)
    print(f"SBL PJ Pk-Pk   : {res_sbl['pj_pkpk']:.2f} ps")
    print(f"LASSO PJ Pk-Pk : {res_lasso['pj_pkpk']:.2f} ps")
    print(f"LS PJ Pk-Pk    : {res_ls['pj_pkpk']:.2f} ps")
    
    # 这一步建议手动打开 sbl_model.py 里的画图功能，
    # 或者看 SBL 打印出来的 "Dominant Frequency"。
    # SBL 应该能清晰地列出 1.0 和 1.2 两个峰。
    # 而 LS 往往会把 1.0 和 1.2 糊成一团宽宽的包络。

if __name__ == "__main__":
    run_experiment_3()