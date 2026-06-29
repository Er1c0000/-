import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.fft import rfft, rfftfreq
import os

def ls_jitter_separation(file_path, k_isi=5, bit_rate=2e9, train_len=50000, silent=False, f_candidates=None):
    """
    使用 [FFT 预筛选 + 最小二乘法] 进行抖动分离。
    流程:
    1. 对 TIE 数据进行 FFT，识别显著的 PJ 频率峰值。
    2. 仅使用识别出的频率构建字典矩阵 H。
    3. 使用 LinearRegression 求解幅度和相位。
    """
    if not silent:
        print(f"🚀 [LS-FFT] 开始读取数据: {file_path}")
    
    # --- 1. 数据准备 ---
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ 文件未找到。")
        return None

    real_len = min(train_len, len(df))
    data_slice = df.iloc[:real_len]
    
    # 单位转换 & 去直流
    if 'TIE_Seconds' in df.columns:
        tie_data_ps = (data_slice['TIE_Seconds'].values * 1e12).astype(np.float32)
    elif 'TIE_UI' in df.columns:
        ui_ps = (1 / bit_rate) * 1e12
        tie_data_ps = (data_slice['TIE_UI'].values * ui_ps).astype(np.float32)
    else:
        return None

    # 去直流 (对 FFT 很重要)
    tie_data_ps = tie_data_ps - np.mean(tie_data_ps)
    
    bits = data_slice['Bit'].values
    N = len(tie_data_ps)
    
    # 时间轴
    if 'Edge_Index' in data_slice.columns:
        time_axis = (data_slice['Edge_Index'].values * (1 / bit_rate)).astype(np.float32)
    else:
        time_axis = (np.arange(N) * (1 / bit_rate)).astype(np.float32)

    # ==========================================
    # Step 1: FFT 频率预筛选 (关键新增步骤)
    # ==========================================
    if not silent: print("🔍 正在进行 FFT 寻峰...")
    
    # 计算 FFT
    # 注意：TIE 是非均匀采样的 (Edge time)，但在锁定频率时，
    # 我们可以近似看作是均匀采样的 (Sample per UI) 或者直接对 TIE 序列做 FFT
    # 为了简单且有效，我们直接对 TIE 序列做 FFT，假设采样率为 1/UI (即 bit rate)
    # 这在 TIE 这种离散事件序列中是常用的近似
    
    yf = rfft(tie_data_ps)
    xf = rfftfreq(N, 1/bit_rate) # 频率轴
    amp_spectrum = np.abs(yf)
    
    # 策略：选出幅度最大的 Top-K 个频率
    # 我们排除极低频 (直流附近)，比如排除 < 10kHz
    valid_idx = np.where(xf > 10e3)[0]
    xf_valid = xf[valid_idx]
    amp_valid = amp_spectrum[valid_idx]
    
    # 选前 5 个峰值 (足以覆盖单音和双音)
    # 简单的 argsort 可能选到同一个峰附近的多个点，这里简化处理，直接选最大的几个
    # 更好的做法是找局部极大值 (find_peaks)，但 Top-K 通常够用了
    K_peaks = 5
    top_k_indices = np.argsort(amp_valid)[-K_peaks:]
    found_freqs = xf_valid[top_k_indices]
    
    if not silent:
        print(f"📡 FFT 识别到的主频: {found_freqs/1e6} MHz")

    # ==========================================
    # Step 2: 构建精简字典 H
    # ==========================================
    # 这里的 f_candidates 不再是几百个，而是 FFT 找出来的这 5 个
    # 但为了画图对比，如果外部传入了 f_candidates (比如画全谱图)，
    # 我们需要一个机制：只拟合 found_freqs，但返回结果时映射回 f_candidates
    
    # 实际拟合用的频率
    fit_freqs = found_freqs
    
    # A. PJ (只包含 FFT 找到的频率)
    pj_features = []
    for f in fit_freqs:
        pj_features.append(np.sin(2 * np.pi * f * time_axis).astype(np.float32))
        pj_features.append(np.cos(2 * np.pi * f * time_axis).astype(np.float32))
    
    if len(pj_features) > 0:
        mat_pj = np.column_stack(pj_features).astype(np.float32)
    else:
        mat_pj = np.zeros((N, 0)) # 空矩阵
        
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
    
    # 拼装 H
    if n_pj_cols > 0:
        H_M = np.hstack((mat_pj, col_dcd, mat_isi)).astype(np.float32)
    else:
        H_M = np.hstack((col_dcd, mat_isi)).astype(np.float32)
    
    # ==========================================
    # Step 3: LS 求解
    # ==========================================
    if not silent: print(f"🧠 正在进行 LS 推断 (特征数: {H_M.shape[1]})...")
    
    clf = LinearRegression(fit_intercept=False)
    clf.fit(H_M, tie_data_ps)
    weights = clf.coef_

    # ==========================================
    # Step 4: 结果映射 (为了兼容画图接口)
    # ==========================================
    # 我们算出了 fit_freqs 的系数，现在要把它们“贴”回到用户传入的 f_candidates 网格上
    # 这样画图脚本才能画出对比图
    
    pj_pkpk = 0.0
    if n_pj_cols > 0:
        w_pj = weights[:n_pj_cols]
        pj_reconstructed = mat_pj @ w_pj
        pj_pkpk = np.max(pj_reconstructed) - np.min(pj_reconstructed)
    
    # 映射回 f_candidates (如果传入了)
    # 这是一个 trick: 我们只在 FFT 找到的频率附近填入系数，其他地方为 0
    # 为了简单起见，如果是在 run_exp3 这种画图模式下，我们直接返回一个全零的系数数组
    # 但在 FFT 找到的频率最近的那个 grid point 上填上幅度
    # (这只是为了让图上有东西显示，实际上 LS 已经算完了)
    
    # 提取非 PJ 部分
    w_dcd = weights[n_pj_cols]
    dcd_val = w_dcd * 2 
    w_isi = weights[n_pj_cols + 1:]
    isi_pkpk = np.max(w_isi) - np.min(w_isi)
    
    tie_pred = H_M @ weights
    residuals = tie_data_ps - tie_pred
    rj_rms = np.std(residuals)
    
    if not silent:
        print(f"✅ LS 结果: PJ={pj_pkpk:.3f}ps, RJ={rj_rms:.3f}ps")

    return {
        'pj_pkpk': pj_pkpk,
        'dcd': abs(dcd_val),
        'isi_pkpk': isi_pkpk,
        'rj_rms': rj_rms,
        'model_name': 'LS-FFT'
    }