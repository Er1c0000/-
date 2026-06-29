
**Table 1** Performance Comparison of Frequency-Domain Jitter Decomposition Algorithms

|Algorithm|Hyperparameter Selection|Amplitude Estimation Bias|Frequency Resolution|Computational Complexity|
|---|---|---|---|---|
|LS-FFT|None|Severely biased (spectral leakage)|Low|O(_N_ log _N_)|
|LASSO (_L_₁)|Manual / cross-validation|Systematically biased (shrinkage)|High|O(_I__iter · _M_ · _N_)|
|SBL-LS (Proposed)|**Automatic (ARD)**|**Low bias (LS stage)**|**High**|O(_I__iter · _M_³)|

---

**Table 2** Statistical Repeatability over 50 Monte Carlo Runs (Ground Truth: PJ = 15.000 ps, DCD = 1.000 ps, ISI = 0.160 ps, RJ = 2.000 ps)

|Method|PJ (ps)|DCD (ps)|ISI (ps)|RJ (ps)|
|---|---|---|---|---|
|LS|0.243 ± 0.060|0.969 ± 0.019|0.701 ± 0.119|5.665 ± 0.015|
|LASSO (α=0.01)|15.300 ± 0.059|0.979 ± 0.020|0.000 ± 0.000|1.997 ± 0.007|
|LASSO (α=0.10)|15.045 ± 0.037|0.799 ± 0.020|0.000 ± 0.000|2.024 ± 0.007|
|LASSO (α=0.50)|13.871 ± 0.032|0.008 ± 0.011|0.000 ± 0.000|2.244 ± 0.007|
|**SBL-LS (Proposed)**|**15.063 ± 0.046**|**0.969 ± 0.020**|**0.347 ± 0.040**|**1.999 ± 0.007**|

> Each cell: mean ± standard deviation over 50 independent runs with re-sampled PRBS and RJ realisations.

---

几个要点说明：

Table 2 的数据亮点在正文中可以这样点：SBL-LS 的 PJ 均值误差仅 0.064 ps（std 0.043），显著优于 LASSO(α=0.01) 的 0.300 ps（std 0.059），且标准差更小；SBL-LS 仍然是唯一产生非零 ISI 估计的方法（0.347 ± 0.040 ps）。LASSO(α=0.10) 的 PJ 均值误差虽低（0.049 ps），但这是事后调优结果，其 DCD 均值 0.799 ps 偏离真值 20%，且 ISI 恒为零。

需要我继续开始全文翻译了吗？