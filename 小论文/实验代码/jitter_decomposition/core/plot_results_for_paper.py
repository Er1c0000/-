import pandas as pd
import matplotlib.pyplot as plt
import os

# 设置全局绘图风格 (学术风格 - IEEE/SCI 标准)
def setup_plot_style():
    plt.style.use('seaborn-v0_8-paper')
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": 300,
        "savefig.bbox": 'tight',
        
        # 刻度线设置 (Ticks)
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True
    })
    
    # 确保输出目录存在
    os.makedirs("results/final_figure", exist_ok=True)

def plot_exp1_freq():
    """读取 Exp 1 (频率扫描) 并画图"""
    csv_path = "results/experiment_1/exp1_freq_summary.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️ 找不到文件: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    plt.figure(figsize=(7, 5))
    
    plt.plot(df['Freq_MHz'], df['Error_LS'], 's--', label='Least Squares (LS)', color='gray', alpha=0.6, markersize=5)
    plt.plot(df['Freq_MHz'], df['Error_LASSO'], 'o--', label='LASSO (alpha=0.1)', color='#1f77b4', alpha=0.8, markersize=5)
    plt.plot(df['Freq_MHz'], df['Error_SBL'], '*-', label='SBL (Proposed)', color='#d62728', linewidth=2, markersize=8)
    
    plt.xscale('log')
    plt.xlabel(r'Periodic Jitter Frequency $f_{PJ}$ (MHz)')
    plt.ylabel(r'Estimation Error $\sigma$ (ps)')
    # plt.title('Exp 1: Estimation Accuracy vs. PJ Frequency') # 移除内部标题
    plt.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.legend(frameon=True)
    
    output_path = "results/final_figure/fig1_freq_accuracy.png"
    plt.savefig(output_path)
    print(f"✅ 已生成高质量图表: {output_path}")

def plot_exp2_noise():
    """读取 Exp 2 (噪声鲁棒性) 并画图"""
    csv_path = "results/experiment_2/exp2_noise_summary.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️ 找不到文件: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    plt.figure(figsize=(7, 5))
    
    plt.plot(df['RJ_ps'], df['Error_LS'], 's--', label='LS', color='gray', alpha=0.6)
    plt.plot(df['RJ_ps'], df['Error_LASSO'], 'o--', label='LASSO', color='#1f77b4', alpha=0.8)
    plt.plot(df['RJ_ps'], df['Error_SBL'], '*-', label='SBL (Proposed)', color='#d62728', linewidth=2, markersize=8)
    
    plt.xlabel(r'Injected Random Jitter $\sigma_{RJ}$ (ps RMS)')
    plt.ylabel(r'PJ Estimation Error $\sigma$ (ps)')
    # plt.title('Exp 2: Robustness to Random Jitter') # 移除内部标题
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(frameon=True)
    
    output_path = "results/final_figure/fig2_noise_robustness.png"
    plt.savefig(output_path)
    print(f"✅ 已生成高质量图表: {output_path}")

def plot_exp3_dual_tone():
    """读取 Exp 3 (双音频谱) 并画图"""
    csv_path = "results/experiment_3/exp3_dual_tone_summary.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️ 找不到文件: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    
    # 子图1: LS
    axes[0].plot(df['Freq_MHz'], df['Spec_LS'], 'k-', alpha=0.5, label='LS Spectrum')
    axes[0].fill_between(df['Freq_MHz'], 0, df['Spec_LS'], color='gray', alpha=0.2)
    axes[0].set_ylabel(r"Amplitude (ps)")
    # axes[0].set_title("Least Squares (LS)", loc='left', fontweight='bold') # 移除标题
    axes[0].text(0.02, 0.9, "(a) LS Spectrum", transform=axes[0].transAxes, fontweight='bold', fontsize=12) # 子图标签
    axes[0].grid(True, linestyle='--', alpha=0.3)
    axes[0].text(1.1, max(df['Spec_LS'])*0.7, "Spectral Leakage", color='#d62728', fontsize=10)

    # 子图2: LASSO
    axes[1].stem(df['Freq_MHz'], df['Spec_LASSO'], basefmt=" ", linefmt='#1f77b4', markerfmt='bo', label='LASSO')
    axes[1].set_ylabel(r"Amplitude (ps)")
    # axes[1].set_title("LASSO ($L_1$ Regularization)", loc='left', fontweight='bold') # 移除标题
    axes[1].text(0.02, 0.9, "(b) LASSO Spectrum", transform=axes[1].transAxes, fontweight='bold', fontsize=12) # 子图标签
    axes[1].grid(True, linestyle='--', alpha=0.3)

    # 子图3: SBL
    axes[2].stem(df['Freq_MHz'], df['Spec_SBL'], basefmt=" ", linefmt='#d62728', markerfmt='r*', label='Proposed SBL')
    axes[2].set_xlabel(r"Frequency $f$ (MHz)")
    axes[2].set_ylabel(r"Amplitude (ps)")
    # axes[2].set_title("SBL (Proposed)", loc='left', fontweight='bold', color='#d62728') # 移除标题
    axes[2].text(0.02, 0.9, "(c) Proposed SBL", transform=axes[2].transAxes, fontweight='bold', fontsize=12) # 子图标签
    axes[2].grid(True, linestyle='--', alpha=0.3)

    # 统一设置
    for ax in axes:
        ax.axvline(1.0, color='green', linestyle=':', alpha=0.6)
        ax.axvline(1.2, color='green', linestyle=':', alpha=0.6)
        ax.set_xlim(0.8, 1.4) # 聚焦在关键区域
        ax.tick_params(labelsize=9)

    plt.tight_layout()
    output_path = "results/final_figure/fig3_dual_tone.png"
    plt.savefig(output_path)
    print(f"✅ 已生成高质量图表: {output_path}")

def plot_exp4_runtime():
    """读取 Exp 4 (运行时间) 并画图"""
    csv_path = "results/experiment_4/runtime_comparison_realdata.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️ 找不到文件: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    plt.figure(figsize=(7, 5))
    
    plt.bar(df['Sample_Size'].astype(str), df['Time_SBL'], color='#d62728', alpha=0.7, label='SBL Runtime')
    
    plt.xlabel(r'Number of Samples $N$')
    plt.ylabel(r'Runtime $t$ (Seconds)')
    # plt.title('Exp 4: Computational Time of SBL') # 移除内部标题
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    
    # 在柱状图上方标出数值
    for i, val in enumerate(df['Time_SBL']):
        plt.text(i, val + 2, f'{val:.1f}s', ha='center', va='bottom', fontsize=9)

    output_path = "results/final_figure/fig4_runtime.png"
    plt.savefig(output_path)
    print(f"✅ 已生成高质量图表: {output_path}")

if __name__ == "__main__":
    setup_plot_style()
    plot_exp1_freq()
    plot_exp2_noise()
    plot_exp3_dual_tone()
    plot_exp4_runtime()
    print("\n🎉 所有论文用图已生成至 results/final_figure/ 目录！")
