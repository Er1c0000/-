import pandas as pd
import numpy as np
import os
import sys

# Get the absolute path of the current script file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to get the project root directory
project_root = os.path.dirname(os.path.dirname(current_dir))
# Add the project root to the Python path
sys.path.insert(0, project_root)

from core.sbl_model import sbl_jitter_separation
from core.tie_generate import generate_aligned_dataset

def run_systematic_test(freq_list):
    results = []
    
    # 注入的真值 (Ground Truth) - 需与生成脚本中的参数保持一致
    TRUE_PJ_PKPK = 15.0  # ps
    TRUE_RJ_RMS = 2.0    # ps
    TRUE_DCD = 1.0       # ps
    
    print(f"开始自动化实验，共 {len(freq_list)} 组测试用例...")
    
    for freq in freq_list:
        # 1. 生成数据
        label = f"{int(freq/1e3)}kHz" if freq < 1e6 else f"{freq/1e6:.1f}MHz"
        filename = f"datasets/tie_data_{label}.csv"
        file_path = generate_aligned_dataset(filename=filename, pj_freq=freq)
        
        # 2. 运行 SBL 分离 (silent=True 不打印中间过程)
        metrics = sbl_jitter_separation(file_path, train_len=140000, silent=True)
        
        if metrics:
            # 3. 计算误差
            res = {
                "Freq_Hz": freq,
                "Label": label,
                "PJ_True": TRUE_PJ_PKPK,
                "PJ_Est": metrics['pj_pkpk'],
                "PJ_Error_ps": metrics['pj_pkpk'] - TRUE_PJ_PKPK,
                "RJ_True": TRUE_RJ_RMS,
                "RJ_Est": metrics['rj_rms'],
                "RJ_Error_ps": metrics['rj_rms'] - TRUE_RJ_RMS,
                "DCD_True": TRUE_DCD,
                "DCD_Est": metrics['dcd'],
                "DCD_Error_ps": metrics['dcd'] - TRUE_DCD
            }
            results.append(res)
            print(f"✅ 完成频率 {label}: PJ误差 {res['PJ_Error_ps']:.3f} ps")

    # 4. 导出结果
    df_results = pd.DataFrame(results)
    df_results.to_csv("SBL_Performance_Analysis.csv", index=False)
    print("\n" + "="*30)
    print("📊 实验报告已生成: SBL_Performance_Analysis.csv")
    print("="*30)
    return df_results

if __name__ == "__main__":
    # 覆盖从低频到高频的典型范围
    test_frequencies = [10e3, 50e3, 100e3, 500e3, 1e6, 5e6, 10e6]
    report = run_systematic_test(test_frequencies)
    
    # 打印简要平均误差
    print(f"平均 PJ 绝对误差: {report['PJ_Error_ps'].abs().mean():.3f} ps")
