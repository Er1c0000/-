# SBL 算法精度验证实验

本实验旨在自动化验证 SBL (Sparse Bayesian Learning) 抖动分离算法在不同 PJ (周期性抖动) 频率下的估计精度。

## 实验内容

实验通过生成包含已知 PJ、RJ、DCD 分量的合成数据，运行 SBL 算法进行分离，并计算估计误差。

- **测试频率**: 10 kHz, 100 kHz, 1 MHz, 5 MHz, 10 MHz
- **注入真值**:
  - PJ (Pk-Pk): 15.0 ps
  - RJ (RMS): 2.0 ps
  - DCD: 1.0 ps
- **重复次数**: 每个频率重复 5 次 (使用不同随机种子)

## 运行方法

在项目根目录下运行以下命令：

```bash
python "Least Squares/experiment_accuracy.py"
```

## 结果输出

实验结果将保存在 `Least Squares/experiment_results/` 目录下：

1.  **数据表格** (`accuracy_results.csv`):
    包含每次实验的详细输入真值、算法估计值及绝对误差。

2.  **可视化图表** (`plots/`):
    - `error_bar_chart.png`: 各频率下 PJ/RJ/DCD 的平均绝对误差条形图。
    - `pj_estimation_scatter.png`: PJ 估计值与真值的对比散点图。

3.  **生成的测试数据** (`datasets/`):
    实验过程中生成的 CSV 数据文件。

## 依赖库

- numpy
- pandas
- matplotlib
- seaborn
- tqdm
- scikit-learn
- scipy

## 注意事项

- 实验运行时间约 10 分钟。
- SBL 算法在高频 (如 5MHz, 10MHz) 下可能表现不佳，这属于算法本身的特性/局限性，实验结果如实反映了这一点。
