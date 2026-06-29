import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import ARDRegression
import os

def sbl_jitter_separation(file_path, k_isi=5, bit_rate=2e9, train_len=2000, silent=False, f_candidates=None):
    """
    使用稀疏贝叶斯学习 (SBL/ARD) 进行抖动分离。
    返回: dict 包含分离出的各项抖动值
    """
    if not silent:
        print(f"🚀 [SBL] 开始读取数据: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ 文件未找到。")
        return None

    # 1. 数据准备
    # 确保数据够长，不够就截断到最大长度
    real_len = min(train_len, len(df))
    data_slice = df.iloc[:real_len]
    
    # ===【关键修正】=== 
    # 将 TIE 从 "秒" 转换为 "皮秒 (ps)"
    # [Memory Optimization] 强制转换为 float32
    tie_data_ps = (data_slice['TIE_Seconds'].values * 1e12).astype(np.float32)
    
    bits = data_slice['Bit'].values
    N = len(tie_data_ps)
    
    if 'Edge_Index' in data_slice.columns:
        time_axis = (data_slice['Edge_Index'].values * (1 / bit_rate)).astype(np.float32)
    else:
        time_axis = (data_slice.index.values * (1 / bit_rate)).astype(np.float32)
    
    if not silent:
        print(f"📊 使用数据长度: {N}")
        print(f"⚖️ 数据已缩放至 ps 量级 (Mean: {np.mean(tie_data_ps):.3f}, Std: {np.std(tie_data_ps):.3f})")

    # ==========================================
    # 第一步：构建"过完备"字典 H_M
    # ==========================================
    
    if f_candidates is None:
        # 频率扫描范围：对数全频段扫描 (Log-space)
        # 覆盖 5 kHz 到 15 MHz，保证全频段覆盖且低频分辨率足够
        # 200 个点在 4 个数量级上 (优化速度)
        # f_candidates = np.logspace(np.log10(5e3), np.log10(15e6), 1000)

        # 针对 100kHz 以上不准的问题：
        # 1MHz 以下用对数分布 (保证低频覆盖)；1MHz 以上用线性分布 (提升高频分辨率)
        f_low = np.logspace(np.log10(5e3), np.log10(1e6), 200) 
        f_high = np.linspace(1.1e6, 20e6, 600) 
        f_candidates = np.unique(np.concatenate([f_low, f_high])).astype(np.float32)
    else:
        # 使用自定义的频率列表
        f_candidates = np.array(f_candidates).astype(np.float32)
        
    if not silent:
        print(f"🏗️ 构建过完备字典矩阵 H_M (扫描频点数: {len(f_candidates)})...")
    
    # --- A. 构建 PJ 子矩阵 ---
    pj_features = []
    # [Memory Optimization] 强制 float32
    for f in f_candidates:
        pj_features.append(np.sin(2 * np.pi * f * time_axis).astype(np.float32))
        pj_features.append(np.cos(2 * np.pi * f * time_axis).astype(np.float32))
    
    mat_pj = np.column_stack(pj_features).astype(np.float32)
    n_pj_cols = mat_pj.shape[1]
    
    # --- B. 构建 DCD 子矩阵 ---
    col_dcd = np.where(bits == 1, 1.0, -1.0).reshape(-1, 1).astype(np.float32)
    
    # --- C. 构建 ISI 子矩阵 ---
    isi_pattern_indices = np.zeros(N, dtype=int)
    for k in range(1, k_isi + 1):
        col_name = f'Bit_Prev_{k}'
        if col_name in df.columns:
            prev_bits = df[col_name].values[:real_len]
            isi_pattern_indices += prev_bits * (2**(k-1))
    
    num_isi_cols = 2**k_isi
    mat_isi = np.eye(num_isi_cols, dtype=np.float32)[isi_pattern_indices]
    
    # --- 拼装总矩阵 H_M ---
    H_M = np.hstack((mat_pj, col_dcd, mat_isi)).astype(np.float32)
    
    # ==========================================
    # 第二步：稀疏贝叶斯训练
    # ==========================================
    if not silent:
        print("🧠 正在进行稀疏贝叶斯推断...")
    
    clf = ARDRegression(compute_score=True)
    clf.fit(H_M, tie_data_ps)
    weights = clf.coef_

    # ==========================================
    # 【新增步骤】 两步法 (Two-step): SBL 筛选 -> LS 重算
    # ==========================================
    if not silent:
        print("\n🔄 正在进行两步法优化 (SBL筛选 -> LS重算)...")
    
    valid_pj_indices = np.where(np.abs(weights[:n_pj_cols]) > 1e-20)[0]
    
    # 2. 构建精简矩阵
    dcd_idx = n_pj_cols
    isi_indices = np.arange(n_pj_cols + 1, H_M.shape[1])
    
    final_indices = np.concatenate([valid_pj_indices, [dcd_idx], isi_indices])
    final_indices = final_indices.astype(int)
    
    H_refined = H_M[:, final_indices]
    
    # 3. 使用 LS 重新拟合
    theta_refined, _, _, _ = np.linalg.lstsq(H_refined, tie_data_ps, rcond=None)
    
    weights_refined = np.zeros_like(weights)
    weights_refined[final_indices] = theta_refined
    
    weights = weights_refined
    
    if not silent:
        print("✅ 两步法优化完成。")

    # ==========================================
    # 第三步：分离与重构
    # ==========================================
    
    # 1. 提取 PJ
    w_pj = weights[:n_pj_cols]
    pj_reconstructed = mat_pj @ w_pj
    pj_pkpk = np.max(pj_reconstructed) - np.min(pj_reconstructed)
    
    # 2. 提取 DCD
    w_dcd = weights[n_pj_cols]
    dcd_val = w_dcd * 2 
    
    # 3. 提取 ISI
    w_isi = weights[n_pj_cols + 1:]
    isi_pkpk = np.max(w_isi) - np.min(w_isi)
    
    # 4. 提取 RJ
    tie_pred = H_M @ weights
    residuals = tie_data_ps - tie_pred
    rj_rms_empirical = np.std(residuals)
    rj_rms_estimated = np.sqrt(1.0 / clf.alpha_)

    # ==========================================
    # 第四步：结果展示 (可选)
    # ==========================================
    if not silent:
        print("\n" + "="*40)
        print("🔮 稀疏贝叶斯学习 (SBL/ARD) 分离结果")
        print("   (输入数据已缩放至 ps 量级)")
        print("="*40)
        print(f"PJ (Pk-Pk)      : {pj_pkpk:.3f} ps")
        print(f"DCD             : {abs(dcd_val):.3f} ps")
        print(f"ISI (Pk-Pk)     : {isi_pkpk:.3f} ps")
        print(f"RJ (RMS, Resid) : {rj_rms_empirical:.3f} ps")
        print(f"RJ (RMS, Model) : {rj_rms_estimated:.3f} ps")
        print("="*40)

        # --- 可视化 ---
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        pj_amps = []
        for i in range(0, n_pj_cols, 2):
            amp = np.sqrt(weights[i]**2 + weights[i+1]**2)
            pj_amps.append(amp)
        plt.stem(f_candidates/1000, pj_amps, basefmt=" ")
        plt.xscale('log')
        plt.title("SBL Sparse Spectrum (PJ Amplitudes)")
        plt.xlabel("Candidate Frequency (kHz)")
        plt.ylabel("Amplitude (ps)")
        plt.grid(True, which="both", alpha=0.3)
        
        plt.subplot(2, 1, 2)
        plot_len = min(200, len(tie_data_ps))
        plt.plot(tie_data_ps[:plot_len], label='Original TIE (ps)', alpha=0.6)
        plt.plot(tie_pred[:plot_len], label='SBL Recovered (DJ)', alpha=0.8, linestyle='--')
        plt.title(f"TIE Reconstruction (First {plot_len} points)")
        plt.ylabel("Jitter (ps)")
        plt.legend()
        plt.tight_layout()
        plt.savefig('results/sbl_model/sbl_result.png')
        print("📊 结果图已保存至 results/sbl_model/sbl_result.png")

    return {
        'pj_pkpk': pj_pkpk,
        'dcd': abs(dcd_val),
        'isi_pkpk': isi_pkpk,
        'rj_rms': rj_rms_empirical
    }

if __name__ == "__main__":
    csv_path = "datasets\synthetic\exp_noise\\noise_rj_8.0ps.csv"
    if os.path.exists(csv_path):
        # 使用 80000 个点进行训练 (覆盖 10kHz 周期)
        sbl_jitter_separation(csv_path, train_len=80000)
    else:
        print(f"请检查文件路径: {csv_path}")
