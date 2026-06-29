import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso
import os

def lasso_jitter_separation(file_path, k_isi=5, bit_rate=2e9, train_len=50000, alpha=0.01, silent=False, f_candidates=None):
    """
    使用 LASSO (L1 正则化) 进行抖动分离。
    核心区别：需要手动调节 alpha 参数。
    """
    if not silent:
        print(f"🚀 [LASSO] 开始读取数据: {file_path}")
    
    # --- 1. 数据准备 (与 SBL 完全一致) ---
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ 文件未找到。")
        return None

    real_len = min(train_len, len(df))
    data_slice = df.iloc[:real_len]
    
    # 统一转换为 ps
    if 'TIE_Seconds' in df.columns:
        tie_data_ps = (data_slice['TIE_Seconds'].values * 1e12).astype(np.float32)
    elif 'TIE_UI' in df.columns:
        ui_ps = (1 / bit_rate) * 1e12
        tie_data_ps = (data_slice['TIE_UI'].values * ui_ps).astype(np.float32)
    else:
        print("❌ 错误：CSV 中未找到 TIE 列")
        return None

    bits = data_slice['Bit'].values
    N = len(tie_data_ps)
    
    # 时间轴
    if 'Edge_Index' in data_slice.columns:
        time_axis = (data_slice['Edge_Index'].values * (1 / bit_rate)).astype(np.float32)
    else:
        time_axis = (np.arange(N) * (1 / bit_rate)).astype(np.float32)

    # --- 2. 构建矩阵 H (与 SBL 完全一致) ---
    if f_candidates is None:
        # 频率扫描范围 (2Gbps 场景: 10kHz - 15MHz)
        f_low = np.logspace(np.log10(10e3), np.log10(1e6), 100)
        f_high = np.linspace(1.1e6, 20e6, 600)
        f_candidates = np.unique(np.concatenate([f_low, f_high])).astype(np.float32)
    else:
        f_candidates = np.array(f_candidates).astype(np.float32)
        
    # A. PJ
    pj_features = []
    for f in f_candidates:
        pj_features.append(np.sin(2 * np.pi * f * time_axis).astype(np.float32))
        pj_features.append(np.cos(2 * np.pi * f * time_axis).astype(np.float32))
    mat_pj = np.column_stack(pj_features).astype(np.float32)
    n_pj_cols = mat_pj.shape[1]
    
    # B. DCD
    col_dcd = np.where(bits == 1, 1.0, -1.0).reshape(-1, 1).astype(np.float32)
    
    # C. ISI
    isi_pattern_indices = np.zeros(N, dtype=int)
    for k in range(1, k_isi + 1):
        col_name = f'Bit_Prev_{k}'
        if col_name in df.columns:
            prev_bits = df[col_name].values[:real_len]
            isi_pattern_indices += prev_bits * (2**(k-1))
    num_isi_cols = 2**k_isi
    mat_isi = np.eye(num_isi_cols, dtype=np.float32)[isi_pattern_indices]
    
    H_M = np.hstack((mat_pj, col_dcd, mat_isi)).astype(np.float32)
    
    # --- 3. LASSO 求解 (核心不同点) ---
    if not silent:
        print(f"🧠 正在进行 LASSO 推断 (alpha={alpha})...")
    
    # Lasso 不需要 fit_intercept，因为 TIE 均值已去，且 ISI 包含直流分量
    clf = Lasso(alpha=alpha, fit_intercept=False, max_iter=5000, selection='random')
    clf.fit(H_M, tie_data_ps)
    weights = clf.coef_

    # --- 4. 结果提取 ---
    w_pj = weights[:n_pj_cols]
    pj_reconstructed = mat_pj @ w_pj
    pj_pkpk = np.max(pj_reconstructed) - np.min(pj_reconstructed)
    
    w_dcd = weights[n_pj_cols]
    dcd_val = w_dcd * 2 
    
    w_isi = weights[n_pj_cols + 1:]
    isi_pkpk = np.max(w_isi) - np.min(w_isi)
    
    tie_pred = H_M @ weights
    residuals = tie_data_ps - tie_pred
    rj_rms = np.std(residuals)
    
    if not silent:
        print(f"✅ LASSO 结果: PJ={pj_pkpk:.3f}ps, RJ={rj_rms:.3f}ps")

    return {
        'pj_pkpk': pj_pkpk,
        'dcd': abs(dcd_val),
        'isi_pkpk': isi_pkpk,
        'rj_rms': rj_rms,
        'model_name': 'LASSO'
    }