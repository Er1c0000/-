import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
import pywt
from scipy.fft import fft, fftfreq
from scipy.stats import norm
from scipy.optimize import curve_fit
import warnings

# --- 0. 环境与配置 ---
# 忽略在GMM拟合中可能出现的收敛警告，不影响实验结论
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')
# 设置全局字体以支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# --- 1. 核心算法模块 ---

def analyze_with_gmm(tie_signal_ps, n_components=3):
    """使用GMM模型分析TIE信号并估计RJ"""
    tie_reshaped = tie_signal_ps.reshape(-1, 1)
    gmm = GaussianMixture(n_components=n_components, random_state=0, n_init=5)
    gmm.fit(tie_reshaped)
    # 假设RJ是均值最接近0的高斯分量
    rj_component_index = np.argmin(np.abs(gmm.means_))
    estimated_rj_sigma_ps = np.sqrt(gmm.covariances_[rj_component_index][0][0])
    return estimated_rj_sigma_ps

def tail_fit_function(x, mu, sigma):
    """Dual-Dirac模型的CDF尾部拟合函数 (使用误差函数)"""
    # Q函数 Q(x) = 0.5 * erfc(x / sqrt(2))
    # 我们拟合的是CDF的尾部，即 1 - CDF = Q((x-mu)/sigma)
    return 0.5 * (1 - norm.cdf(x, loc=mu, scale=sigma))

def analyze_with_tailfit(tie_signal_ps):
    """使用Dual-Dirac Tail-Fit算法估计RJ"""
    hist, bin_edges = np.histogram(tie_signal_ps, bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # 计算累积分布函数 (CDF)
    cdf = np.cumsum(hist) * (bin_centers[1] - bin_centers[0])
    
    # 提取CDF的右尾部用于拟合 (通常选择CDF在0.8到0.999之间的部分)
    tail_indices = np.where((cdf > 0.8) & (cdf < 0.9999))[0]
    if len(tail_indices) < 2:
        return np.nan # 如果尾部数据太少，无法拟合

    x_tail = bin_centers[tail_indices]
    y_tail = 1 - cdf[tail_indices] # 我们拟合的是 1 - CDF

    # 使用curve_fit进行非线性拟合
    try:
        # 初始猜测值：mu=均值, sigma=标准差
        p_initial = [np.mean(tie_signal_ps), np.std(tie_signal_ps)]
        popt, _ = curve_fit(tail_fit_function, x_tail, y_tail, p0=p_initial, maxfev=5000)
        # popt[1] 是拟合出的sigma，即RJ
        return abs(popt[1])
    except RuntimeError:
        return np.nan # 如果拟合失败，返回NaN


# --- 2. 信号生成与实验流程模块 ---

def generate_tie_signal(params):
    """根据参数生成复杂的TIE信号"""
    N = params['N']
    fs = params['fs']
    t = np.arange(N) / fs

    # 2.1 生成RJ分量
    rj = np.random.normal(0, params['rj_sigma_s'], N)

    # 2.2 生成SSC (非平庸DJ) 分量
    tri_wave = 2 * np.abs(2 * (t * params['fm'] - np.floor(t * params['fm'] + 0.5))) - 1
    inst_freq = params['f0'] + params['delta_f'] * tri_wave
    phase = 2 * np.pi * np.cumsum(inst_freq) / fs
    ssc_dj = params['ssc_amplitude_s'] * np.sin(phase)

    # 2.3 (扩展) 生成并叠加周期性抖动 (PJ)
    pj = params.get('pj_amplitude_s', 0) * np.sin(2 * np.pi * params.get('pj_freq', 0) * t)

    # 2.4 合成总信号
    tie_signal = rj + ssc_dj + pj
    return tie_signal

def run_single_experiment(params):
    """运行一次独立的仿真实验"""
    # 1. 生成信号
    tie_signal = generate_tie_signal(params)
    tie_signal_ps = tie_signal * 1e12

    # 2. 使用不同方法进行分析
    gmm_rj_est = analyze_with_gmm(tie_signal_ps)
    tailfit_rj_est = analyze_with_tailfit(tie_signal_ps)
    
    # 3. 返回结果
    return {
        'true_rj': params['rj_sigma_s'] * 1e12,
        'gmm_rj_est': gmm_rj_est,
        'tailfit_rj_est': tailfit_rj_est
    }

# --- 3. 主程序与参数扫描 ---

def main():
    """主函数：定义实验、运行参数扫描、汇总并展示结果"""
    
    print("开始执行抖动分解算法性能对比实验...")

    # --- 实验参数定义 ---
    base_params = {
        'N': 80000, 'fs': 1e9,
        'f0': 100e6, 'fm': 1e6, 'delta_f': 5e6,
        'ssc_amplitude_s': 20e-12,
        'pj_amplitude_s': 5e-12, 'pj_freq': 50e6  # 新增的PJ参数
    }

    # --- 参数扫描：改变RJ标准差 (即改变信噪比) ---
    rj_scan_values_ps = np.linspace(2, 12, 10) # 从2ps扫描到12ps，共10个点
    results = []
    
    print(f"将对 {len(rj_scan_values_ps)} 个不同的RJ水平进行扫描...")
    for i, rj_ps in enumerate(rj_scan_values_ps):
        print(f"  正在运行实验 {i+1}/{len(rj_scan_values_ps)} (真实RJ = {rj_ps:.2f} ps)...")
        current_params = base_params.copy()
        current_params['rj_sigma_s'] = rj_ps / 1e12
        
        exp_result = run_single_experiment(current_params)
        results.append(exp_result)
    
    print("所有实验运行完毕！")

    # --- 结果处理与可视化 ---
    true_rjs = [r['true_rj'] for r in results]
    gmm_estimates = [r['gmm_rj_est'] for r in results]
    tailfit_estimates = [r['tailfit_rj_est'] for r in results]

    gmm_errors = [abs(est - true) / true * 100 for est, true in zip(gmm_estimates, true_rjs)]
    # 过滤掉tailfit失败的结果
    valid_tailfit_indices = [i for i, est in enumerate(tailfit_estimates) if not np.isnan(est)]
    tailfit_errors = [abs(tailfit_estimates[i] - true_rjs[i]) / true_rjs[i] * 100 for i in valid_tailfit_indices]

    # --- 绘制最终的性能对比图 ---
    plt.figure(figsize=(10, 6))
    plt.plot(true_rjs, gmm_errors, 'o-', label='GMM 方法', linewidth=2, markersize=8)
    if valid_tailfit_indices:
        plt.plot(np.array(true_rjs)[valid_tailfit_indices], tailfit_errors, 's--', label='Dual-Dirac Tail-Fit 方法', linewidth=2, markersize=8)
    
    plt.title('GMM 与 Tail-Fit 方法在不同噪声水平下的RJ估计误差对比', fontsize=16)
    plt.xlabel('真实随机抖动 (RJ) 标准差 (ps)', fontsize=12)
    plt.ylabel('相对误差 (%)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--')
    plt.ylim(bottom=0)
    plt.show()


if __name__ == '__main__':
    main()
