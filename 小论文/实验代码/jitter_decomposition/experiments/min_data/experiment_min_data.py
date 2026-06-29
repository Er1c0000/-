import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Get the absolute path of the current script file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to get the project root directory
project_root = os.path.dirname(os.path.dirname(current_dir))
# Add the project root to the Python path
sys.path.insert(0, project_root)

from core.sbl_model import sbl_jitter_separation

def check_performance(csv_path, length, target=15.0):
    """
    运行一次 SBL 并检查是否达标
    """
    result = sbl_jitter_separation(csv_path, train_len=length, silent=True)
    if result is None:
        return False
        
    pj_val = result['pj_pkpk']
    error_pct = abs(pj_val - target) / target * 100
    
    # 判定标准：误差 < 10% 且 PJ > 10ps
    if error_pct < 10.0 and pj_val > 10.0:
        return True
    return False

def get_dataset_path(freq, base_dir="Least Squares/datasets"):
    if freq < 1e6:
        name_freq = f"{int(freq/1e3)}kHz"
    else:
        name_freq = f"{freq/1e6:.1f}MHz"
    
    filename = f"tie_data_{name_freq}.csv"
    return os.path.join(base_dir, filename)

def run_experiment_optimized():
    print("🚀 开始运行最小数据量测试实验 (读取预生成数据)...")
    
    # 测试频率列表 (需与生成的一致)
    frequencies = [10e3, 50e3, 100e3, 500e3, 1e6, 5e6, 10e6]
    min_data_requirements = []
    
    # 定义搜索范围
    MIN_LEN = 2000
    MAX_LEN = 140000
    TOLERANCE = 2000 # 搜索精度
    
    for freq in frequencies:
        print(f"\n📡 测试频率: {freq/1e3:.1f} kHz")
        
        # 1. 获取对应的数据文件路径
        csv_path = get_dataset_path(freq)
        if not os.path.exists(csv_path):
            print(f"   ❌ 数据文件未找到: {csv_path}")
            min_data_requirements.append(np.nan)
            continue
            
        print(f"   📂 读取文件: {os.path.basename(csv_path)}")
        
        # 2. 二分查找最小长度
        low = MIN_LEN
        high = MAX_LEN
        best_len = -1
        
        # 先检查最大长度是否达标
        if not check_performance(csv_path, MAX_LEN):
            print(f"   ⚠️ 最大长度 {MAX_LEN} 仍未达标，跳过")
            min_data_requirements.append(np.nan)
            continue
            
        print("   🔍 正在进行二分查找...")
        while high - low > TOLERANCE:
            mid = (low + high) // 2
            mid = int(mid / 100) * 100
            
            if check_performance(csv_path, mid):
                high = mid # mid 可能是最小，继续向左找
                best_len = mid
                print(f"      长度 {mid} ✅ 达标 -> 尝试更小")
            else:
                low = mid # mid 不行，必须更大
                print(f"      长度 {mid} ❌ 未达标 -> 尝试更大")
        
        print(f"   🏆 找到最小所需数据量: {high}")
        min_data_requirements.append(high)

    # ================= 结果绘图 =================
    plt.figure(figsize=(10, 6))
    
    valid_indices = ~np.isnan(min_data_requirements)
    freqs_valid = np.array(frequencies)[valid_indices]
    reqs_valid = np.array(min_data_requirements)[valid_indices]
    
    # 主曲线
    plt.plot(freqs_valid, reqs_valid, 'bo-', linewidth=2, markersize=8, label='Measured SBL Requirement')
    
    # 理论参考曲线
    theoretical = 1e9 / np.array(frequencies)
    plt.plot(frequencies, theoretical, 'r--', alpha=0.5, label='Theoretical 1-Period Limit')
    
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    plt.xlabel('PJ Frequency (Hz)')
    plt.ylabel('Minimum Data Points Required')
    plt.title('Minimum Data Requirements vs PJ Frequency (SBL)')
    plt.legend()
    
    output_img = 'Least Squares/result/min_data_requirement.png'
    plt.savefig(output_img)
    print(f"\n📊 实验结果图已保存至: {output_img}")
    
    print("\nSUMMARY TABLE:")
    print(f"{'Freq (kHz)':<15} | {'Min Points':<15} | {'Time (approx)'}")
    print("-" * 60)
    for f, n in zip(frequencies, min_data_requirements):
        time_us = n * 1e-3
        print(f"{f/1e3:<15.1f} | {n:<15} | {time_us:.1f} us")

if __name__ == "__main__":
    run_experiment_optimized()
