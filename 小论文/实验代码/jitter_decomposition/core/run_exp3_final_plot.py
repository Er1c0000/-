import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import ARDRegression, Lasso, LinearRegression
import os

def run_final_comparison():
    # 1. 准备数据
    file_path = "datasets\synthetic\exp_dual\dual_tone_1.0M_1.2M.csv"
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return

    print(f"⚔️  开始最终对比: SBL vs LASSO vs LS (双音测试)...")
    df = pd.read_csv(file_path)
    
    # 统一参数
    bit_rate = 2e9
    train_len = 30000
    
    # 数据预处理
    real_len = min(train_len, len(df))
    data_slice = df.iloc[:real_len]
    
    # 自动单位转换
    if 'TIE_Seconds' in df.columns:
        tie_data_ps = (data_slice['TIE_Seconds'].values * 1e12).astype(np.float32)
    elif 'TIE_UI' in df.columns:
        ui_ps = (1 / bit_rate) * 1e12
        tie_data_ps = (data_slice['TIE_UI'].values * ui_ps).astype(np.float32)
    else:
        # 默认假设是 ps
        tie_data_ps = data_slice.iloc[:, 0].values.astype(np.float32)
    
    # 去直流
    tie_data_ps = tie_data_ps - np.mean(tie_data_ps)
    N = len(tie_data_ps)

    # 时间轴
    if 'Edge_Index' in data_slice.columns:
        time_axis = (data_slice['Edge_Index'].values * (1 / bit_rate)).astype(np.float32)
    else:
        time_axis = (np.arange(N) * (1 / bit_rate)).astype(np.float32)

    # 2. 构建高分辨率字典
    print("🏗️ 构建高分辨率字典矩阵...")
    f_candidates = np.arange(0.5e6, 2.02e6, 0.02e6).astype(np.float32)
    
    pj_features = []
    for f in f_candidates:
        pj_features.append(np.sin(2 * np.pi * f * time_axis).astype(np.float32))
        pj_features.append(np.cos(2 * np.pi * f * time_axis).astype(np.float32))
    mat_pj = np.column_stack(pj_features).astype(np.float32)
    n_pj_cols = mat_pj.shape[1]
    
    col_dcd = np.where(data_slice['Bit'].values == 1, 1.0, -1.0).reshape(-1, 1).astype(np.float32)
    H_M = np.hstack((mat_pj, col_dcd))
    
    # 3. 运行三个模型
    print("🏃‍♂️ 正在训练 SBL (可能需要1分钟)...")
    clf_sbl = ARDRegression(compute_score=True, fit_intercept=False, max_iter=300)
    clf_sbl.fit(H_M, tie_data_ps)
    w_sbl = clf_sbl.coef_[:n_pj_cols]
    
    print("🏃‍♂️ 正在训练 LASSO...")
    clf_lasso = Lasso(alpha=0.01, fit_intercept=False, max_iter=5000)
    clf_lasso.fit(H_M, tie_data_ps)
    w_lasso = clf_lasso.coef_[:n_pj_cols]
    
    print("🏃‍♂️ 正在训练 LS...")
    clf_ls = LinearRegression(fit_intercept=False)
    clf_ls.fit(H_M, tie_data_ps)
    w_ls = clf_ls.coef_[:n_pj_cols]

    # 4. 计算频谱幅度
    def get_spectrum(weights):
        amps = []
        for i in range(0, len(weights), 2):
            amp = np.sqrt(weights[i]**2 + weights[i+1]**2)
            amps.append(amp)
        return np.array(amps)

    spec_sbl = get_spectrum(w_sbl)
    spec_lasso = get_spectrum(w_lasso)
    spec_ls = get_spectrum(w_ls)
    freqs_mhz = f_candidates / 1e6

    # --- 保存 CSV 数据 ---
    df_exp3 = pd.DataFrame({
        'Freq_MHz': freqs_mhz,
        'Spec_SBL': spec_sbl,
        'Spec_LASSO': spec_lasso,
        'Spec_LS': spec_ls
    })
    csv_exp3 = "results/experiment_3/exp3_dual_tone_summary.csv"
    os.makedirs(os.path.dirname(csv_exp3), exist_ok=True)
    df_exp3.to_csv(csv_exp3, index=False)
    print(f"✅ 频谱数据已保存至: {csv_exp3}")

    # 5. 画图
    print("📊 正在绘图...")
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # 子图1: LS
    axes[0].plot(freqs_mhz, spec_ls, 'k-', alpha=0.6)
    axes[0].fill_between(freqs_mhz, 0, spec_ls, color='gray', alpha=0.3)
    axes[0].set_title("Least Squares (LS) Spectrum", fontsize=14)
    axes[0].set_ylabel("Amplitude (ps)")
    axes[0].grid(True, alpha=0.3)
    axes[0].text(1.1, max(spec_ls)*0.8, "Severe Leakage\n(Cannot distinguish)", color='red', ha='center')

    # 子图2: LASSO
    axes[1].stem(freqs_mhz, spec_lasso, basefmt=" ", linefmt='b-', markerfmt='bo')
    axes[1].set_title("LASSO Spectrum (L1 Regularization)", fontsize=14)
    axes[1].set_ylabel("Amplitude (ps)")
    axes[1].grid(True, alpha=0.3)
    
    # 子图3: SBL
    axes[2].stem(freqs_mhz, spec_sbl, basefmt=" ", linefmt='r-', markerfmt='r*')
    axes[2].set_title("SBL Spectrum (Sparse Bayesian Learning)", fontsize=14, color='red')
    axes[2].set_xlabel("Frequency (MHz)", fontsize=12)
    axes[2].set_ylabel("Amplitude (ps)")
    axes[2].grid(True, alpha=0.3)
    
    for ax in axes:
        ax.axvline(1.0, color='green', linestyle='--', alpha=0.5)
        ax.axvline(1.2, color='green', linestyle='--', alpha=0.5)
        ax.set_xlim(0.5, 1.8)
    
    plt.tight_layout()
    save_path = "results/experiment_3/fig3_dual_tone_comparison.png"
    plt.savefig(save_path, dpi=300)
    print(f"✅ 对比图已生成: {save_path}")

if __name__ == "__main__":
    run_final_comparison()
