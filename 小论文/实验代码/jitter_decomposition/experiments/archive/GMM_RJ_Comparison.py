import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture

# --- 0. 环境设置 ---
# 设置中文字体，以防绘图时出现乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. 仿真参数定义 ---
N = 80000  # 采样点数
fs = 1e9   # 采样率 (1 GHz)
t = np.arange(N) / fs  # 时间轴

# 随机抖动 (RJ) 参数
rj_sigma_s = 5e-12  # RJ的标准差 (5 ps, 单位：秒)

# 确定性抖动 (DJ) - 扩频时钟 (SSC) 参数
f0 = 100e6  # 中心频率 (100 MHz)
fm = 1e6    # SSC调制频率 (1 MHz) - 三角波的频率
delta_f = 5e6 # 频率调制深度/偏移 (5 MHz)
ssc_amplitude_s = 20e-12 # SSC抖动的幅度 (20 ps, 单位：秒)

# --- 1. 仿真参数定义 ---
N = 80000  # 采样点数
fs = 1e9   # 采样率 (1 GHz)
t = np.arange(N) / fs  # 时间轴

# 随机抖动 (RJ) 参数
rj_sigma_s = 5e-12  # RJ的标准差 (5 ps, 单位：秒)

# 确定性抖动 (DJ) - 简单正弦波
dj_amplitude_s = 5e-12 # DJ的幅度 (5 ps, 单位：秒) - 降低幅度
dj_freq = 50e6 # DJ的频率 (50 MHz)
simple_dj = dj_amplitude_s * np.sin(2 * np.pi * dj_freq * t)

# 确定性抖动 (DJ) - 扩频时钟 (SSC) 参数
f0 = 100e6  # 中心频率 (100 MHz)
fm = 1e6    # SSC调制频率 (1 MHz) - 三角波的频率
delta_f = 5e6 # 频率调制深度/偏移 (5 MHz)
ssc_amplitude_s = 10e-12 # SSC抖动的幅度 (10 ps, 单位：秒) - 降低幅度

# 构建SSC DJ信号 (与GMM_CWT.py中相同)
tri_wave = 2 * np.abs(2 * (t * fm - np.floor(t * fm + 0.5))) - 1
inst_freq = f0 + delta_f * tri_wave
phase = 2 * np.pi * np.cumsum(inst_freq) / fs
ssc_dj = ssc_amplitude_s * np.sin(phase)

# --- 2. 实验场景一: 包含随机抖动 (RJ) 和确定性抖动 (DJ) ---
print("="*60)
print(" " * 8 + "实验场景一: 包含随机抖动 (RJ) 和确定性抖动 (DJ)")
print("="*60)

rj_scenario1 = np.random.normal(0, rj_sigma_s, N)
tie_signal_scenario1 = rj_scenario1 + simple_dj

tie_signal_ps_scenario1 = tie_signal_scenario1 * 1e12
tie_reshaped_ps_scenario1 = tie_signal_ps_scenario1.reshape(-1, 1)

# 对于RJ+DJ，我们假设GMM能识别出多个分量，其中一个代表RJ
# 尝试使用更多的分量来更好地拟合复杂的分布
gmm_scenario1 = GaussianMixture(n_components=7, random_state=0, n_init=50) # 增加n_init
gmm_scenario1.fit(tie_reshaped_ps_scenario1)

# 找到最接近0均值且方差最小的分量作为RJ
# 遍历所有分量，找到均值最接近0的，并且其方差最小的作为RJ分量
rj_component_index_scenario1 = -1
min_abs_mean = float('inf')
min_variance_for_rj = float('inf')

for i in range(gmm_scenario1.n_components):
    current_mean = gmm_scenario1.means_[i][0]
    current_variance = gmm_scenario1.covariances_[i][0][0]
    if abs(current_mean) < min_abs_mean:
        min_abs_mean = abs(current_mean)
        min_variance_for_rj = current_variance # 更新最小方差
        rj_component_index_scenario1 = i
    elif abs(current_mean) == min_abs_mean and current_variance < min_variance_for_rj:
        min_variance_for_rj = current_variance
        rj_component_index_scenario1 = i

estimated_rj_sigma_ps_scenario1 = np.sqrt(gmm_scenario1.covariances_[rj_component_index_scenario1][0][0])

true_rj_ps = rj_sigma_s * 1e12
relative_error_scenario1 = abs(estimated_rj_sigma_ps_scenario1 - true_rj_ps) / true_rj_ps * 100

print(f"  - 预设真实 RJ (Ground Truth): {true_rj_ps:>10.2f} ps")
print(f"  - GMM 估计 RJ:              {estimated_rj_sigma_ps_scenario1:>10.2f} ps")
print(f"  - 相对误差 (Relative Error):  {relative_error_scenario1:>9.2f}%")
print(f"  - GMM 均值 (Means):         {gmm_scenario1.means_.flatten()}")
print(f"  - GMM 方差 (Covariances):   {gmm_scenario1.covariances_.flatten()}")
print(f"  - 选定的RJ分量索引:         {rj_component_index_scenario1}")


# --- 2. 实验场景二: 包含随机抖动 (RJ)、确定性抖动 (DJ) 和非平稳抖动 (SSC DJ) ---
print("\n" + "="*60)
print(" " * 4 + "实验场景二: 包含随机抖动 (RJ)、确定性抖动 (DJ) 和非平稳抖动 (SSC DJ)")
print("="*60)

rj_scenario2 = np.random.normal(0, rj_sigma_s, N)
tie_signal_scenario2 = rj_scenario2 + simple_dj + ssc_dj

tie_signal_ps_scenario2 = tie_signal_scenario2 * 1e12
tie_reshaped_ps_scenario2 = tie_signal_ps_scenario2.reshape(-1, 1)

# 对于RJ+DJ+SSC DJ，GMM可能需要更多分量来拟合复杂的分布
gmm_scenario2 = GaussianMixture(n_components=9, random_state=0, n_init=50) # 增加n_init
gmm_scenario2.fit(tie_reshaped_ps_scenario2)

# 找到最接近0均值且方差最小的分量作为RJ
rj_component_index_scenario2 = -1
min_abs_mean = float('inf')
min_variance_for_rj = float('inf')

for i in range(gmm_scenario2.n_components):
    current_mean = gmm_scenario2.means_[i][0]
    current_variance = gmm_scenario2.covariances_[i][0][0]
    if abs(current_mean) < min_abs_mean:
        min_abs_mean = abs(current_mean)
        min_variance_for_rj = current_variance
        rj_component_index_scenario2 = i
    elif abs(current_mean) == min_abs_mean and current_variance < min_variance_for_rj:
        min_variance_for_rj = current_variance
        rj_component_index_scenario2 = i

estimated_rj_sigma_ps_scenario2 = np.sqrt(gmm_scenario2.covariances_[rj_component_index_scenario2][0][0])

relative_error_scenario2 = abs(estimated_rj_sigma_ps_scenario2 - true_rj_ps) / true_rj_ps * 100

print(f"  - 预设真实 RJ (Ground Truth): {true_rj_ps:>10.2f} ps")
print(f"  - GMM 估计 RJ:              {estimated_rj_sigma_ps_scenario2:>10.2f} ps")
print(f"  - 相对误差 (Relative Error):  {relative_error_scenario2:>9.2f}%")
print(f"  - GMM 均值 (Means):         {gmm_scenario2.means_.flatten()}")
print(f"  - GMM 方差 (Covariances):   {gmm_scenario2.covariances_.flatten()}")
print(f"  - 选定的RJ分量索引:         {rj_component_index_scenario2}")

# --- 3. 结果可视化 ---
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('GMM分离随机抖动效果对比', fontsize=16)

# 场景一: 包含随机抖动 (RJ) 和确定性抖动 (DJ)
axes[0].hist(tie_signal_ps_scenario1, bins=100, density=True, label='RJ+DJ信号直方图', alpha=0.6)
x_axis_scenario1 = np.linspace(np.min(tie_signal_ps_scenario1), np.max(tie_signal_ps_scenario1), 1000).reshape(-1, 1)
log_prob_scenario1 = gmm_scenario1.score_samples(x_axis_scenario1)
axes[0].plot(x_axis_scenario1, np.exp(log_prob_scenario1), 'r-', label='GMM拟合PDF')

# 绘制GMM的每个高斯分量
for i in range(gmm_scenario1.n_components):
    mean = gmm_scenario1.means_[i][0]
    variance = gmm_scenario1.covariances_[i][0][0]
    weight = gmm_scenario1.weights_[i]
    gaussian_pdf = weight * (1 / np.sqrt(2 * np.pi * variance)) * np.exp(-0.5 * ((x_axis_scenario1 - mean)**2 / variance))
    axes[0].plot(x_axis_scenario1, gaussian_pdf, linestyle='--', label=f'GMM分量 {i+1}')

axes[0].set_title('场景一: RJ + DJ')
axes[0].set_xlabel('抖动幅值 (ps)')
axes[0].set_ylabel('概率密度')
axes[0].legend()
axes[0].grid(True)

# 场景二: 包含随机抖动 (RJ)、确定性抖动 (DJ) 和非平稳抖动 (SSC DJ)
axes[1].hist(tie_signal_ps_scenario2, bins=100, density=True, label='RJ+DJ+SSC信号直方图', alpha=0.6)
x_axis_scenario2 = np.linspace(np.min(tie_signal_ps_scenario2), np.max(tie_signal_ps_scenario2), 1000).reshape(-1, 1)
log_prob_scenario2 = gmm_scenario2.score_samples(x_axis_scenario2)
axes[1].plot(x_axis_scenario2, np.exp(log_prob_scenario2), 'r-', label='GMM拟合PDF')

# 绘制GMM的每个高斯分量
for i in range(gmm_scenario2.n_components):
    mean = gmm_scenario2.means_[i][0]
    variance = gmm_scenario2.covariances_[i][0][0]
    weight = gmm_scenario2.weights_[i]
    gaussian_pdf = weight * (1 / np.sqrt(2 * np.pi * variance)) * np.exp(-0.5 * ((x_axis_scenario2 - mean)**2 / variance))
    axes[1].plot(x_axis_scenario2, gaussian_pdf, linestyle='--', label=f'GMM分量 {i+1}')

axes[1].set_title('场景二: RJ + DJ + SSC DJ')
axes[1].set_xlabel('抖动幅值 (ps)')
axes[1].set_ylabel('概率密度')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

print("\n" + "="*60)
print("实验总结: 对比了GMM在不同抖动场景下分离随机抖动的效果。")
print("="*60 + "\n")
