import os
import pandas as pd
# 导入三个模型
from sbl_model import sbl_jitter_separation
from lasso_model import lasso_jitter_separation
from ls_model import ls_jitter_separation

def run_comparison():
    # 1. 指定测试文件 (任选一个刚刚生成的)
    test_file = "datasets\synthetic\exp_freq\\freq_10.0MHz.csv" 
    
    if not os.path.exists(test_file):
        print(f"❌ 找不到测试文件: {test_file}")
        print("请先运行 run_all_experiments.py 生成数据！")
        return

    print("="*50)
    print(f"⚔️  开始单次对比测试 (文件: {os.path.basename(test_file)})")
    print("="*50)

    # 2. 设定参数 (保持一致)
    params = {
        'file_path': test_file,
        'bit_rate': 2e9,       # 2Gbps
        'train_len': 50000,    # 训练长度
        'silent': True         # 静默模式，只看结果
    }

    # 3. 运行三个模型
    print("⏳ 正在运行 SBL ...")
    res_sbl = sbl_jitter_separation(**params)
    
    print("⏳ 正在运行 LASSO ...")
    res_lasso = lasso_jitter_separation(alpha=0.1, **params) # alpha 可以调
    
    print("⏳ 正在运行 LS ...")
    res_ls = ls_jitter_separation(**params)

    # 4. 打印对比表
    print("\n" + "="*65)
    print(f"{'Metric':<15} | {'True (Approx)':<12} | {'SBL':<10} | {'LASSO':<10} | {'LS':<10}")
    print("-" * 65)
    
    # 真值参考 (基于 tie_generate.py 的设定)
    # PJ Amp = 7.5ps, PkPk = 15ps
    # RJ RMS = 2.0ps
    truth_pj = 15.0
    truth_rj = 2.0
    
    print(f"{'PJ Pk-Pk (ps)':<15} | {truth_pj:<12.1f} | {res_sbl['pj_pkpk']:<10.2f} | {res_lasso['pj_pkpk']:<10.2f} | {res_ls['pj_pkpk']:<10.2f}")
    print(f"{'RJ RMS (ps)':<15} | {truth_rj:<12.1f} | {res_sbl['rj_rms']:<10.2f} | {res_lasso['rj_rms']:<10.2f} | {res_ls['rj_rms']:<10.2f}")
    print("-" * 65)
    
    # 简单的胜负判断
    err_sbl = abs(res_sbl['pj_pkpk'] - truth_pj)
    err_lasso = abs(res_lasso['pj_pkpk'] - truth_pj)
    err_ls = abs(res_ls['pj_pkpk'] - truth_pj)
    
    winner = "SBL" if (err_sbl <= err_lasso and err_sbl <= err_ls) else "Others"
    print(f"\n🏆 本轮胜者: {winner} (误差: {err_sbl:.3f} ps)")

if __name__ == "__main__":
    run_comparison()