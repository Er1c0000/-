import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from scipy.optimize import minimize
from scipy.signal import find_peaks

# 设置中文字体 (尝试使用常见中文字体，如果失败则回退到英文)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 信号生成 (Data Generation)
# ==========================================
# 依据论文 Table I 的设定:
# Ideal DJ (确定性抖动) = 100 ns (0.1 us)
# Ideal RJ (随机抖动) = 10 ns (0.01 us)
# 注意：为了方便绘图和计算，我们将单位统一为 ns 或保持相对比例
# 论文中的直方图 x 轴大约在 -0.1 到 0.1 之间 (单位可能是 us)，这里我们直接模拟数值
np.random.seed(42)
n_samples = 10000

ideal_dj = 0.100  # 100 ns -> 0.1 us
ideal_rj = 0.010  # 10 ns -> 0.01 us

# 双狄拉克模型 (Dual-Dirac): 两个高斯分布，均值分别为 -DJ/2 和 +DJ/2
mu1_true = -ideal_dj / 2
mu2_true = ideal_dj / 2

# 生成TIE数据
data_left = np.random.normal(mu1_true, ideal_rj, int(n_samples / 2))
data_right = np.random.normal(mu2_true, ideal_rj, int(n_samples / 2))
tie_data = np.concatenate([data_left, data_right])

print(f"原始信号生成完毕: 样本数={n_samples}, 理想DJ={ideal_dj*1000}ns, 理想RJ={ideal_rj*1000}ns")

# ==========================================
# 2. KDE 平滑处理 (KDE Smoothing)
# ==========================================
# 论文步骤 B: 使用交叉验证寻找最佳带宽
X = tie_data[:, np.newaxis]
bandwidths = np.linspace(0.001, 0.02, 20)
grid = GridSearchCV(KernelDensity(kernel='gaussian'),
                    {'bandwidth': bandwidths},
                    cv=5)
grid.fit(X)
best_bandwidth = grid.best_params_['bandwidth']
kde = grid.best_estimator_

# 生成平滑后的 PDF 曲线数据点
x_grid = np.linspace(min(tie_data)-0.05, max(tie_data)+0.05, 1000)
log_pdf = kde.score_samples(x_grid[:, np.newaxis])
pdf_smooth = np.exp(log_pdf)

print(f"KDE 最佳带宽 (Best Bandwidth): {best_bandwidth:.4f}")

# ==========================================
# 3. 对比试验 I: 拟合参数扫描 (Fig. 9 Reproduction)
# ==========================================
# 论文提到：通过遍历 mu 的值，计算 Fit 参数 (MSE)，找到极小值点。
# 这是一个非常关键的实验步骤，证明了如何通过算法自动找到双峰的位置。

def double_gaussian_fixed_sigma(x, mu_pos, sigma_val):
    """
    简化的双高斯模型用于扫描，假设左右对称。
    论文 Fig 9 显示的是 Fit 参数随 mu 的变化。
    这里我们模拟在这个平滑曲线上，假设我们去试探 mu 的位置。
    """
    # 假设对称的双峰
    # mu_pos 是正半轴的峰值位置 (即 mu2), 对应的 mu1 就是 -mu_pos
    # 为了简化扫描，我们假设 sigma 暂时固定或随 mu 优化，论文中是扫描 mu
    
    # 这里的 Fit 函数: 计算当前猜测的 mu 生成的双高斯 与 KDE曲线 的 MSE
    
    # 构建一个临时的双高斯分布 (归一化)
    g1 = np.exp(-(x - (-mu_pos))**2 / (2 * sigma_val**2))
    g2 = np.exp(-(x - mu_pos)**2 / (2 * sigma_val**2))
    y_est = g1 + g2
    # 归一化以匹配 PDF 面积
    y_est = y_est / (np.sum(y_est) * (x[1] - x[0]))
    return y_est

# 扫描范围：从 0 到 0.1 (覆盖半个 DJ 范围)
scan_mus = np.linspace(0.01, 0.08, 100) 
fit_errors = []

# 固定一个估计的 sigma (可以通过标准差粗略估计) 用于扫描实验
estimated_sigma = np.std(tie_data) / 2 

for mu_val in scan_mus:
    # 生成假设的分布
    y_est = double_gaussian_fixed_sigma(x_grid, mu_val, estimated_sigma)
    # 计算 MSE (Eq. 8 in paper)
    mse = np.mean((pdf_smooth - y_est)**2)
    fit_errors.append(mse)

# 找到误差最小的 mu
min_error_idx = np.argmin(fit_errors)
best_mu_scan = scan_mus[min_error_idx]

print(f"参数扫描实验完成: 最佳 mu (半轴) = {best_mu_scan:.4f}")

# ==========================================
# 4. 最终拟合与计算 (Final Calculation)
# ==========================================
# 使用扫描得到的 mu 作为初值，进行精确的最小二乘拟合

def double_gaussian_func(x, a1, mu1, sigma1, a2, mu2, sigma2):
    g1 = a1 * np.exp(-(x - mu1)**2 / (2 * sigma1**2))
    g2 = a2 * np.exp(-(x - mu2)**2 / (2 * sigma2**2))
    return g1 + g2

def objective_function(params, x_data, y_data):
    y_est = double_gaussian_func(x_data, *params)
    return np.mean((y_data - y_est)**2)

# 初值：利用扫描结果
# Peaks at -best_mu_scan and +best_mu_scan
initial_guess = [
    0.5, -best_mu_scan, estimated_sigma,
    0.5, best_mu_scan, estimated_sigma
]

res = minimize(objective_function, initial_guess, args=(x_grid, pdf_smooth), method='Nelder-Mead')
a1, m1, s1, a2, m2, s2 = res.x

# 计算 DJ 和 RJ
# DJ = 两个峰值位置之差的绝对值
calc_dj = abs(m2 - m1)
# RJ = 两个峰值标准差的平均值
calc_rj = (abs(s1) + abs(s2)) / 2

# 转换为 ns (因为输入是 0.1us = 100ns)
calc_dj_ns = calc_dj * 1000
calc_rj_ns = calc_rj * 1000
ideal_dj_ns = ideal_dj * 1000
ideal_rj_ns = ideal_rj * 1000

# 计算误差率
err_dj = abs(calc_dj_ns - ideal_dj_ns) / ideal_dj_ns * 100
err_rj = abs(calc_rj_ns - ideal_rj_ns) / ideal_rj_ns * 100

# ==========================================
# 5. 结果展示 (Visualization)
# ==========================================

plt.figure(figsize=(14, 10))

# 图 1: 原始直方图 vs KDE (对应论文 Fig 6 & Fig 8)
plt.subplot(2, 2, 1)
plt.hist(tie_data, bins=60, density=True, alpha=0.4, color='green', label='原始直方图 (Raw Histogram)')
plt.plot(x_grid, pdf_smooth, 'k-', linewidth=2, label='KDE 平滑曲线')
plt.title('对比试验 1: 原始直方图 vs KDE 平滑\n(对应论文 Fig. 6 & 8)')
plt.xlabel('Time Error (us)')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)

# 图 2: Fit Parameter 扫描曲线 (对应论文 Fig 9)
plt.subplot(2, 2, 2)
plt.plot(scan_mus, fit_errors, 'b.--', label='Fit Error (MSE)')
plt.axvline(x=best_mu_scan, color='r', linestyle='--', label=f'Best $\mu$={best_mu_scan:.3f}')
plt.title('对比试验 2: 拟合参数扫描 (Fit Parameter vs $\mu$)\n(对应论文 Fig. 9)')
plt.xlabel('$\mu$ value (Half DJ)')
plt.ylabel('Fit Parameter (MSE)')
plt.legend()
plt.grid(True, alpha=0.3)

# 图 3: 最终的双狄拉克拟合结果
plt.subplot(2, 1, 2)
plt.plot(x_grid, pdf_smooth, 'k-', linewidth=2, label='KDE Curve')
plt.plot(x_grid, double_gaussian_func(x_grid, *res.x), 'r--', linewidth=2, label='Dual-Dirac Fit')
# 标记 DJ 范围
plt.axvline(x=m1, color='blue', linestyle=':', alpha=0.6)
plt.axvline(x=m2, color='blue', linestyle=':', alpha=0.6)
plt.annotate('', xy=(m1, max(pdf_smooth)/2), xytext=(m2, max(pdf_smooth)/2),
             arrowprops=dict(arrowstyle='<->', color='blue'))
plt.text((m1+m2)/2, max(pdf_smooth)/2 + 0.5, f'DJ = {calc_dj_ns:.2f} ns', ha='center', color='blue')
plt.title('最终拟合结果展示 (Dual-Dirac Model Fitting)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ==========================================
# 6. 输出 Table I (Result Comparison)
# ==========================================
print("\n" + "="*50)
print("论文 Table I 复现: 拟合结果与理想结果的对比")
print("COMPARISON OF FITTING RESULTS WITH IDEAL RESULTS")
print("="*50)
print(f"{'Jitter Type':<15} | {'Actual (ns)':<15} | {'Ideal (ns)':<15} | {'Error (%)':<10}")
print("-" * 60)
print(f"{'DJ (确定性)':<15} | {calc_dj_ns:<15.2f} | {ideal_dj_ns:<15.2f} | {err_dj:<10.2f}")
print(f"{'RJ (随机)':<15} | {calc_rj_ns:<15.2f} | {ideal_rj_ns:<15.2f} | {err_rj:<10.2f}")
print("="*50)
print(f"注: 论文报告的误差约为 DJ:1.2%, RJ:4.7%。\n本次复现误差受随机噪声影响，通常在 5% 以内即为验证成功。")