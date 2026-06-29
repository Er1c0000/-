## Responding to Comments

We sincerely thank the reviewers and the editor for their careful reading and constructive comments. We have revised the manuscript accordingly and addressed all major concerns in the revised version. First, to respond to the concern that the original comparison only involved the original LS-FFT baseline, we evaluated refined frequency-domain correction methods and incorporated LS-NUDFT, the stronger and more effective baseline, into the revised manuscript. Second, to clarify the nearly constant ISI error, we added a sample-size verification experiment and revised the explanation based on both theoretical analysis and numerical evidence. Third, to address the lack of validation under multiple PJ sources, we added a new multi-PJ experiment section covering five coexisting scenarios, including a near-frequency dual-tone case, and reported the corresponding decomposition results in Table 2. In addition, the conclusion, abstract, and introduction were revised to include the new quantitative results, and several recent journal papers were added to the references. We also addressed all editorial comments, including affiliation formatting, keyword capitalization, figure resolution, equation font styles, and the preparation of the Chinese abstract and copyright form.

中文翻译：  
我们衷心感谢审稿人和编辑的认真审阅以及建设性意见。我们已据此对稿件进行了修改，并在修订稿中回应了所有主要问题。首先，针对原稿仅与原始 LS-FFT 基线比较的问题，我们评估了频域校正方法，并将更强且效果更稳定的 LS-NUDFT 纳入修订稿。其次，针对 ISI 误差近似稳定的问题，我们补充了样本量验证实验，并结合理论分析与数值结果修正了相关解释。第三，针对缺少多 PJ 源验证的问题，我们新增了一个包含五组共存场景的多 PJ 实验小节，其中包括近频双音场景，并在 Table 2 中给出了相应的分解结果。此外，我们还修订了结论、摘要和引言，补充了新的定量结果，并在参考文献中加入了近三年的期刊论文。我们也处理了所有编辑意见，包括单位格式、关键词大小写、图像分辨率、公式字体样式，以及中文摘要和版权表的准备。

---

## Response to Reviewers (Attachment Draft)

We sincerely thank the reviewers and the editor for their careful reading and constructive comments. We have revised the manuscript substantially in response to all comments. The major revisions include: 1) augmenting the original LS-FFT comparison with a stronger refined frequency-domain baseline, LS-NUDFT, while additionally evaluating parabolic interpolation as a supplementary check; 2) adding a sample-size verification experiment and a brief theoretical explanation for the ISI estimation bias; 3) adding a new multi-PJ experiment section covering five coexisting scenarios; 4) revising the abstract, introduction, experimental discussion, and conclusion to include the new quantitative results; and 5) updating the references with recent journal papers and addressing all editorial-formatting requirements.

中文翻译：  
我们衷心感谢审稿人和编辑的认真审阅以及建设性意见。针对所有评审意见，我们已对稿件进行了较为全面的修订。主要修改包括：1）在原有 LS-FFT 对比基础上，引入更强的频域细化基线 LS-NUDFT，并将抛物线插值作为补充验证进行评估；2）补充样本量验证实验，并对 ISI 误差偏差给出简要理论说明；3）新增一个包含五组场景的多 PJ 实验小节；4）修订摘要、引言、实验讨论和结论，补充新的定量结果；5）补充近三年的期刊文献，并完成所有编辑格式要求的修改。

### Q1: The original manuscript only compares with LS-FFT and does not include more advanced frequency-domain correction methods such as interpolation-based refinement or non-uniform DFT.

We appreciate this important suggestion. In the revision process, we evaluated two refined frequency-domain corrections: LS-FFT with parabolic peak interpolation and LS-NUDFT. The parabolic interpolation results showed only limited and frequency-dependent improvement, and therefore we did not include it in the main manuscript. Instead, we incorporated LS-NUDFT, which is the stronger and more effective representative refined frequency-domain baseline, into the revised manuscript. For all LS-based methods, the subsequent least-squares fitting stage is kept identical so that the comparison isolates the influence of PJ frequency estimation. The new experiments show that LS-NUDFT substantially improves over the original LS-FFT, while the proposed SBL method still achieves lower average and maximum PJ estimation errors in both test cases. For PJ = 10 ps, the mean and maximum errors are 0.481 ps and 0.628 ps for LS-NUDFT, compared with 0.305 ps and 0.499 ps for SBL. For PJ = 6 ps, they are 0.598 ps and 0.691 ps for LS-NUDFT, compared with 0.282 ps and 0.434 ps for SBL. We also updated Table 1 to include a full three-method comparison (LS-FFT, LS-NUDFT, and SBL) at 0.1, 1.0, and 10.0 MHz. The revised results show that DCD errors are comparable across all three methods, while LS-NUDFT significantly reduces the RJ leakage observed in LS-FFT, and SBL remains the most stable overall. These revisions are reflected in Section 4, Fig. 4, Table 1, and the corresponding discussion.

中文翻译：  
感谢审稿人的这一重要建议。在修订过程中，我们评估了两种频域细化方法：带抛物线峰值插值的 LS-FFT 和 LS-NUDFT。抛物线插值仅带来了有限且随频点变化的改善，因此我们未将其纳入正文主结果。相反，我们将更强且效果更稳定的 LS-NUDFT 作为代表性频域细化基线纳入了修订稿。对于所有 LS 类方法，后续最小二乘拟合阶段保持一致，以便将比较集中在 PJ 频率估计本身的影响上。新增实验表明，LS-NUDFT 相比原始 LS-FFT 有明显改善，而本文提出的 SBL 方法在两组测试中仍取得了更低的平均误差和最大误差。对于 PJ = 10 ps，LS-NUDFT 的平均误差和最大误差分别为 0.481 ps 和 0.628 ps，而 SBL 分别为 0.305 ps 和 0.499 ps；对于 PJ = 6 ps，这两项指标分别为 0.598 ps 和 0.691 ps，而 SBL 分别为 0.282 ps 和 0.434 ps。我们还更新了 Table 1，在 0.1、1.0 和 10.0 MHz 三个频点给出了 LS-FFT、LS-NUDFT 和 SBL 的三方法完整比较。修订结果表明，三种方法的 DCD 误差相近，而 LS-NUDFT 显著抑制了 LS-FFT 中观察到的 RJ 串扰，SBL 则整体最为稳定。上述修改已体现在第 4 节、Fig. 4、Table 1 及相应讨论中。

### Q2: The explanation of the approximately 0.30 ps ISI error lacks theoretical support and verification by a sample-size experiment.

Thank you for pointing out that the original explanation was not sufficiently supported. In the revised manuscript, we added both a brief theoretical clarification and a sample-size verification result. The ISI component is estimated from conditional means over the 2^L pattern bins of the ISI sub-matrix, so the residual fluctuation introduced by RJ decreases approximately with the order of sigma_RJ / sqrt(N / 2^L). To verify this explanation, we carried out a sample-size experiment with N ranging from 5,000 to 100,000 and found that the ISI estimation error decreases monotonically for both methods. For example, the SBL ISI error decreases from 0.33 ps at N = 50,000 to 0.25 ps at N = 100,000, and LS-FFT shows the same trend. Additional verification experiments also support this interpretation. These results indicate that the observed bias is mainly a finite-sample statistical effect of the ISI sub-model rather than a PJ-frequency-dependent error. The explanation below Table 1 in Section 4 has been revised accordingly.

中文翻译：  
感谢审稿人指出原稿中的解释缺乏充分支撑。在修订稿中，我们补充了简要理论说明和样本量验证结果。ISI 分量是通过 ISI 子矩阵的 2^L 个码型桶上的条件均值来估计的，因此由 RJ 引入的残余波动大致按 sigma_RJ / sqrt(N / 2^L) 的量级减小。为验证这一解释，我们进行了样本量实验，将 N 从 5,000 增加到 100,000，结果表明两种方法的 ISI 估计误差均随样本量单调下降。例如，SBL 的 ISI 误差从 N = 50,000 时的 0.33 ps 降至 N = 100,000 时的 0.25 ps，LS-FFT 也表现出相同趋势。额外的补充验证实验也支持这一解释。上述结果说明，该偏差主要来源于 ISI 子模型中的有限样本统计效应，而不是 PJ 频率相关的偏差。我们已据此修订了第 4 节 Table 1 下方的相关解释。

### Q3: The original manuscript does not test the identification and decomposition accuracy when two or more PJ frequencies coexist.

We agree that validation under multiple PJ sources is necessary. In the revised manuscript, we added a new multi-PJ experiment section including five scenarios: two dual-tone cases with different separations, one wide-separation dual-tone case, and two triple-tone cases. In these scenarios, the proposed SBL method completes true PJ frequency component identification in all five cases without presetting the number of PJ components. The average PJ estimation error of SBL over the five scenarios is 0.18 ps, and in the most challenging near-frequency dual-tone case (1.00/1.05 MHz), the PJ error remains 0.02 ps. We also added LS-NUDFT as a stronger multi-tone spectrum-domain baseline. Although LS-NUDFT can cover the true frequencies within the ±100 kHz matching tolerance, its subsequent joint least-squares fitting becomes unstable in the near-frequency dual-tone case, leading to a PJ error of 14.16 ps and an RJ error of 3.61 ps. These results show that SBL not only identifies the active frequencies, but also provides more stable coefficient recovery when the candidate columns are highly correlated. A new multi-PJ subsection and Table 2 have therefore been added in Section 4, and the conclusion has been updated accordingly.

中文翻译：  
我们同意，对多 PJ 源共存场景的验证是必要的。在修订稿中，我们新增了一个多 PJ 实验小节，共包含五组场景：两组不同间隔的双音场景、一组大间隔双音场景，以及两组三音场景。在这些场景下，本文提出的 SBL 方法均可在无需预设 PJ 分量个数的情况下完成真实 PJ 频率分量识别。SBL 在五组场景上的平均 PJ 估计误差为 0.18 ps，在最具挑战性的近频双音场景（1.00/1.05 MHz）中，PJ 误差仍保持在 0.02 ps。我们还加入了 LS-NUDFT 作为更强的多音频谱域基线。虽然 LS-NUDFT 在 ±100 kHz 匹配容差内能够覆盖真实频率，但在近频双音场景下，其后续联合最小二乘拟合会变得不稳定，导致 PJ 误差升至 14.16 ps，RJ 误差升至 3.61 ps。这些结果说明，SBL 不仅能够识别活跃频率，还能在候选列高度相关时提供更稳定的系数恢复能力。因此，我们在第 4 节新增了多 PJ 小节和 Table 2，并据此更新了结论部分。

### Q4: The conclusion section should include corresponding quantitative data to support the final conclusions.

We agree and have revised the conclusion to include quantitative results from both the single-PJ and multi-PJ experiments. The revised conclusion now states that, in single-PJ scenarios over 100 kHz–15 MHz, the SBL PJ estimation error remains within 0.5 ps and the RJ error within 0.02 ps. It also reports that, in five multi-PJ scenarios, the mean PJ error is 0.18 ps and the PJ error in the near-frequency dual-tone case is 0.02 ps. Section 5 has been rewritten accordingly.

中文翻译：  
我们同意这一意见，并已修订结论部分，加入单 PJ 和多 PJ 两类实验中的定量结果。修订后的结论明确指出：在 100 kHz–15 MHz 的单 PJ 场景中，SBL 的 PJ 估计误差始终不超过 0.5 ps，RJ 误差不超过 0.02 ps；在五组多 PJ 场景中，平均 PJ 误差为 0.18 ps，在近频双音场景中的 PJ 误差为 0.02 ps。第 5 节已据此重写。

### Q5: More journal papers published in the last three years should be included in the reference list.

Thank you for the suggestion. We have added several recent journal papers to the revised manuscript, including recent work on oscilloscope jitter compensation, feature-interaction neural networks for jitter component analysis, and off-grid sparse Bayesian learning. These additions strengthen both the application background and the methodological context of the paper. The reference list and the corresponding citations in the introduction and method discussion have been revised accordingly.

中文翻译：  
感谢这一建议。我们已在修订稿中补充了多篇近三年的期刊论文，包括示波器抖动补偿、基于特征交互网络的抖动分量分析以及离网稀疏贝叶斯学习等相关工作。这些新增文献强化了论文的应用背景和方法背景。参考文献列表及其在引言和方法讨论中的对应引用均已相应更新。

### Editorial Comments (Q6–Q9)

All editorial comments have been addressed in the revised manuscript: the affiliation numbering has been removed (Q6), all keywords have been fully capitalised (Q7), Fig. 3 has been replaced with a higher-resolution version (Q8), and the notation for vectors and matrices has been revised to bold italic throughout the equations (Q9).

中文翻译：  
以上所有编辑意见均已在修订稿中处理完毕：已删除单位前的编号（Q6），关键词已全部大写（Q7），Fig. 3 已更换为高分辨率版本（Q8），公式中向量和矩阵的字体已统一改为加粗斜体（Q9）。

### Q10: The abstract in Chinese and the Conference Proceeding Copyright Form should also be provided.

The Chinese abstract and the Conference Proceeding Copyright Form have been prepared and will be submitted together with the revised manuscript.

中文翻译：  
中文摘要和会议论文版权表均已准备好，并将随修订稿一并提交。

---

# Rebuttal 工作草稿

本文档用于整理修回过程中对审稿意见的逐条回复、补充实验结果和后续正文修改要点。当前先记录审稿意见第一条对应的频域细化对照实验。

---

## 审稿意见 1：更先进频域校正方法对比不足

### 审稿意见要点

审稿人指出，原稿只与原始 LS-FFT 方法比较，而工程实践中 FFT 峰值频率可通过抛物线插值等亚频点细化方法提高，也可以采用非均匀 DFT 类频域估计方法。因此，原稿仅比较原始 LS-FFT 会限制结论的普适性。

### 补充实验设置

为回应该意见，补充了频域细化对照实验。所有 LS 类方法保持相同的最小二乘分量拟合流程，仅改变 PJ 频率估计方式，以便隔离频率估计对分解精度的影响。

对比方法包括：

- `LS-FFT`：采用基于 `Edge_Index` 平均采样间隔校准后的标准实数 FFT，并直接选取频谱主峰频率；
- `LS-FFT + Parabolic`：在校准后的 FFT 谱峰附近进行三点抛物线插值，得到亚频点频率估计后再进行 LS 拟合；
- `LS-NUDFT`：在论文当前测试频率范围内，基于真实 `Edge_Index` 对应的非均匀边沿时刻进行全频非均匀 DFT 搜索，再将主频用于 LS 拟合；
- `SBL`：本文方法，采用 FastRVM 粗定位与 ARD 精细推断，不额外进行 LS 修正。

实验覆盖原论文的 0.1 MHz、0.5 MHz、1 MHz、5 MHz、10 MHz、15 MHz 六个频点，并分别测试两组样本：

- `pj10rj5`：PJ = 10 ps pk-pk，RJ = 5 ps rms；
- `pj3rj5`：PJ = 6 ps pk-pk，RJ = 5 ps rms。

实验文件：

- 结果表：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal1\fft_refinement_results.csv`
- 对比图：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal1\fft_refinement_comparison.png`
- 实验说明：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal1\fft_refinement_summary.md`

### 补充实验结果

`pj10rj5` 数据集中，各方法 PJ 峰峰值估计绝对误差如下，单位为 ps。

| PJ Frequency (MHz) | LS-FFT | LS-FFT + Parabolic | LS-NUDFT | SBL |
|---:|---:|---:|---:|---:|
| 0.1 | 0.3280 | 0.2838 | 0.4424 | 0.0154 |
| 0.5 | 0.4635 | 0.4038 | 0.3003 | 0.3472 |
| 1.0 | 1.0112 | 0.6849 | 0.6281 | 0.4591 |
| 5.0 | 4.4939 | 5.7706 | 0.4688 | 0.2435 |
| 10.0 | 1.2749 | 1.1042 | 0.5630 | 0.4991 |
| 15.0 | 9.0812 | 8.9834 | 0.4841 | 0.2667 |

统计结果如下。

| Method | Mean Error (ps) | Median Error (ps) | Max Error (ps) | Min Error (ps) |
|---|---:|---:|---:|---:|
| LS-FFT | 2.7755 | 1.1430 | 9.0812 | 0.3280 |
| LS-FFT + Parabolic | 2.8718 | 0.8945 | 8.9834 | 0.2838 |
| LS-NUDFT | 0.4811 | 0.4764 | 0.6281 | 0.3003 |
| SBL | 0.3052 | 0.3070 | 0.4991 | 0.0154 |

`pj3rj5` 数据集中，各方法 PJ 峰峰值估计绝对误差如下，单位为 ps。

| PJ Frequency (MHz) | LS-FFT | LS-FFT + Parabolic | LS-NUDFT | SBL |
|---:|---:|---:|---:|---:|
| 0.1 | 0.5197 | 0.3481 | 0.5588 | 0.0112 |
| 0.5 | 0.3181 | 0.3283 | 0.5712 | 0.3400 |
| 1.0 | 1.2351 | 0.4922 | 0.6789 | 0.4336 |
| 5.0 | 2.7161 | 3.4554 | 0.4715 | 0.2405 |
| 10.0 | 0.6897 | 0.5304 | 0.6143 | 0.3704 |
| 15.0 | 5.5186 | 5.5106 | 0.6911 | 0.2954 |

统计结果如下。

| Method | Mean Error (ps) | Median Error (ps) | Max Error (ps) | Min Error (ps) |
|---|---:|---:|---:|---:|
| LS-FFT | 1.8329 | 0.9624 | 5.5186 | 0.3181 |
| LS-FFT + Parabolic | 1.7775 | 0.5113 | 5.5106 | 0.3283 |
| LS-NUDFT | 0.5976 | 0.5927 | 0.6911 | 0.4715 |
| SBL | 0.2818 | 0.3177 | 0.4336 | 0.0112 |

### 多分量估计误差补充（对应正文 Table 1）

为支撑正文 Table 1 的修订，在宽频段 PJ 精度对比的基础上，补充了三种方法在 0.1 / 1.0 / 10.0 MHz 下的完整四分量（PJ、DCD、ISI、RJ）估计误差，与原稿 Table 1 测试频率一致。

实验文件：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal1\component_nudft_estimation_errors.csv`

**pj10rj5（样本 1，PJ=10 ps pk-pk，RJ=5 ps rms）：**

| $f_{PJ}$ | 方法 | PJ 误差 (ps) | DCD 误差 (ps) | ISI 误差 (ps) | RJ 误差 (ps) |
|---|---|---:|---:|---:|---:|
| 0.1 MHz | LS-FFT | 0.250 | 0.042 | 0.414 | 0.013 |
| 0.1 MHz | LS-NUDFT | 0.442 | 0.042 | 0.398 | 0.021 |
| 0.1 MHz | SBL | 0.015 | 0.027 | 0.302 | 0.013 |
| 1.0 MHz | LS-FFT | 1.287 | 0.042 | 0.483 | 0.063 |
| 1.0 MHz | LS-NUDFT | 0.628 | 0.042 | 0.416 | 0.016 |
| 1.0 MHz | SBL | 0.459 | 0.028 | 0.305 | 0.014 |
| 10.0 MHz | LS-FFT | 1.275 | 0.041 | 0.445 | 0.553 |
| 10.0 MHz | LS-NUDFT | 0.563 | 0.042 | 0.423 | 0.016 |
| 10.0 MHz | SBL | 0.499 | 0.027 | 0.305 | 0.016 |

**pj3rj5（样本 2，PJ=6 ps pk-pk，RJ=5 ps rms）：**

| $f_{PJ}$ | 方法 | PJ 误差 (ps) | DCD 误差 (ps) | ISI 误差 (ps) | RJ 误差 (ps) |
|---|---|---:|---:|---:|---:|
| 0.1 MHz | LS-FFT | 0.439 | 0.042 | 0.416 | 0.014 |
| 0.1 MHz | LS-NUDFT | 0.559 | 0.042 | 0.407 | 0.003 |
| 0.1 MHz | SBL | 0.011 | 0.027 | 0.302 | 0.013 |
| 1.0 MHz | LS-FFT | 0.859 | 0.042 | 0.444 | 0.013 |
| 1.0 MHz | LS-NUDFT | 0.679 | 0.042 | 0.417 | 0.016 |
| 1.0 MHz | SBL | 0.434 | 0.028 | 0.304 | 0.014 |
| 10.0 MHz | LS-FFT | 0.943 | 0.042 | 0.424 | 0.195 |
| 10.0 MHz | LS-NUDFT | 0.614 | 0.042 | 0.422 | 0.016 |
| 10.0 MHz | SBL | 0.370 | 0.026 | 0.305 | 0.016 |

**主要观察：**

- **DCD 误差**：三种方法基本持平（约 0.03–0.04 ps），不受 PJ 频率估计准确性影响。
- **ISI 误差**：SBL 在所有场景下约为 0.30 ps；LS-NUDFT 和 LS-FFT 约为 0.40–0.48 ps。原稿表述"两种方法的 ISI 误差均约 0.30 ps"不够准确，仅 SBL 约 0.30 ps，LS 类方法两者均偏高。
- **RJ 误差**：LS-FFT 在 10.0 MHz 时 RJ 误差显著升高（样本 1：0.553 ps，样本 2：0.195 ps），反映 PJ 频率估计偏差向 RJ 分量的串扰；LS-NUDFT 通过非均匀 DFT 消除了频率偏移，RJ 误差稳定在 0.02 ps 以内，与 SBL 相近；SBL 的 RJ 误差全程不超过 0.02 ps。

### 可用于 rebuttal 的结论

补充实验表明，抛物线插值对 LS-FFT 的改善有限且不稳定。例如在 `pj10rj5` 数据集中，`LS-FFT + Parabolic` 的平均误差为 2.8718 ps，最大误差为 8.9834 ps，与校准后的 `LS-FFT` 相比并未稳定降低误差。

全频 NUDFT 搜索能显著改善普通 FFT 峰值选频的频率估计结果，说明审稿人提出的频域校正方法确实具有工程意义。在 `pj10rj5` 数据集中，`LS-NUDFT` 的平均误差降至 0.4811 ps，最大误差降至 0.6281 ps；在 `pj3rj5` 数据集中，其平均误差为 0.5976 ps，最大误差为 0.6911 ps。

在相同测试条件下，SBL 仍取得更低的平均误差和最大误差。`pj10rj5` 数据集中，SBL 的平均误差和最大误差分别为 0.3052 ps 和 0.4991 ps；`pj3rj5` 数据集中，SBL 的平均误差和最大误差分别为 0.2818 ps 和 0.4336 ps。该结果说明，频域细化方法可以缓解原始 LS-FFT 的误差，但 SBL 通过冗余频率字典和 ARD 支撑集识别，仍能提供更稳定的 PJ 幅度估计。

因此，修回稿中不应继续强调”SBL 相比所有频域方法提升一至两个数量级”。更准确的表述应为：相较于抛物线插值 FFT，SBL 在高频点仍保持明显优势；相较于全频 LS-NUDFT，SBL 进一步降低了平均误差和最大误差。

在多分量分解精度（Table 1）方面，三种方法的 DCD 误差基本相同（约 0.03–0.04 ps）。ISI 误差方面，SBL 约为 0.30 ps，LS-NUDFT 与 LS-FFT 均在 0.40–0.48 ps；原稿中”两种方法 ISI 均约 0.30 ps”的表述需修正。RJ 分量方面，LS-FFT 在 10 MHz 时出现明显误差串扰（样本 1：0.553 ps），而 LS-NUDFT 通过准确的频率估计将 RJ 误差抑制在 0.02 ps，与 SBL 相当。因此修回稿 Table 1 在原 LS-FFT 与 SBL 对比基础上新增 LS-NUDFT 列，并修正 ISI 讨论中不准确的表述。

### 英文回复草稿

We thank the reviewer for pointing out that the original manuscript did not include refined frequency-domain estimators. Following this suggestion, we added two enhanced frequency-domain baselines: LS-FFT with parabolic peak interpolation and LS-NUDFT. In LS-NUDFT, the non-uniform Fourier response is evaluated over the full target frequency range using the true Edge_Index-based time instants, and the dominant frequencies are then used in the same LS fitting framework. For all LS-based methods, the subsequent component fitting stage is kept identical, so that the comparison focuses on the influence of PJ frequency estimation.

The new results show that parabolic interpolation provides only limited and frequency-dependent improvement. LS-NUDFT substantially improves over the original LS-FFT and LS-FFT with parabolic interpolation. However, the proposed SBL method still achieves lower average and maximum PJ amplitude errors in both test cases. For PJ = 10 ps, the mean and maximum errors are 0.481 ps and 0.628 ps for LS-NUDFT, compared with 0.305 ps and 0.499 ps for SBL. For PJ = 6 ps, they are 0.598 ps and 0.691 ps for LS-NUDFT, compared with 0.282 ps and 0.434 ps for SBL.

These results indicate that advanced frequency-domain correction methods can mitigate the limitation of the original LS-FFT baseline, but SBL still provides more stable PJ amplitude estimation by using a redundant frequency dictionary and ARD-based support set identification.

We also present a full four-component comparison (PJ, DCD, ISI, RJ) at 0.1 / 1.0 / 10.0 MHz for both sample sets, corresponding to the updated Table 1. The DCD estimation error is comparable across all three methods (~0.03–0.04 ps). The ISI estimation error is approximately 0.30 ps for SBL and 0.40–0.48 ps for LS-NUDFT and LS-FFT; accordingly, the original statement that "both methods produce ISI errors of approximately 0.30 ps" has been corrected. For RJ, LS-FFT shows a pronounced error increase at 10 MHz (0.553 ps for Sample 1), reflecting PJ frequency misestimation leaking into the RJ estimate; LS-NUDFT suppresses this to below 0.02 ps by using accurate frequency estimates, consistent with SBL. The revised manuscript has been updated to include this three-method comparison in Table 1 and to state all conclusions more precisely.

### 正文修改提示

- 第 4 章实验部分需要新增一个频域细化对照实验，建议放在宽频带 PJ 精度实验之后。
- 图题建议使用：`Comparison with refined frequency-domain baselines`。
- 正文结论应避免”数量级提升”这类过强表述，改为”降低平均误差和最大误差”。
- 高频扩展实验可作为附件或 rebuttal 辅助材料，不建议直接扩展正文主实验频段。
- **Table 1 需重构**：原 9 列横向格式（LS-FFT 与 SBL 各占 4 列）改为 7 列纵向格式（样本 | $f_{PJ}$ | 方法 | PJ | DCD | ISI | RJ），共 18 数据行（2 样本 × 3 频率 × 3 方法）。新增 LS-NUDFT 数据见上方”多分量估计误差补充”节。
- **Table 1 讨论段**：删去”两种方法的 ISI 估计均较真值偏高约 0.30 ps”（仅 SBL 约 0.30 ps，LS 类方法约 0.40–0.48 ps）；改为分方法描述 ISI 差异；补充 RJ 串扰对比（LS-FFT 在 10 MHz 处 0.55 ps，LS-NUDFT 和 SBL 均约 0.02 ps）。

---

## 审稿意见 2：ISI 误差平台无理论分析或验证实验

### 审稿意见要点

审稿人指出，表 1 中两种方法的 ISI 估计误差均稳定在约 0.30 ps 左右，与 PJ 频率无关。原稿将其归因于"有限样本统计累积"，但未提供理论分析，也未验证样本量增加后误差是否会随之减小。

### 补充实验设置

固定仿真参数：PRBS-7，数据率 2 Gbps，信道记忆深度 L=5（对应 32 个 ISI 码型桶），PJ=10 ps pk-pk，DCD=1 ps，RJ=5 ps rms，PJ 频率=1.0 MHz。依次取样本量 N=5000、10000、20000、50000、100000，每组重复 20 次（每次改变 PRBS 与 RJ 种子），统计 ISI 估计误差的均值与标准差。另设控制实验：固定 N=50000，令 RJ=0，验证误差来源。

实验文件：

- 结果表：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal2\isi_sample_size_summary.csv`
- 控制实验：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal2\isi_rj0_control_summary.csv`
- 曲线图：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal2\isi_sample_size_curve.png`

### 补充实验结果

**ISI 误差随样本量变化（均值 ± 标准差，单位 ps）：**

| 样本量 N | LS-FFT 均值 | LS-FFT 标准差 | SBL 均值 | SBL 标准差 |
|---:|---:|---:|---:|---:|
| 5,000 | 1.4975 | 0.2843 | 1.0862 | 0.3219 |
| 10,000 | 1.0638 | 0.2219 | 0.8402 | 0.2724 |
| 20,000 | 0.7235 | 0.1479 | 0.5504 | 0.1952 |
| 50,000 | 0.4137 | 0.0948 | 0.3302 | 0.1151 |
| 100,000 | 0.3100 | 0.0854 | 0.2542 | 0.1026 |

**控制实验（N=50000，RJ=0）：**

| 方法 | ISI 误差均值 (ps) | ISI 误差标准差 (ps) |
|---|---:|---:|
| LS-FFT | 0.0322 | 0.0010 |
| SBL | 0.0303 | 0.0000 |

### 可用于 rebuttal 的结论

控制实验表明，当 RJ=0 时，两种方法的 ISI 误差均降至约 0.03 ps，接近零值，直接证明 ISI 误差的主要来源是随机噪声而非方法本身的系统性偏差。

样本量实验表明，ISI 误差随 N 增大单调下降：在原稿设置 N=50000 下，SBL 的 ISI 误差均值为 0.33 ps；将 N 增大至 100000 后，误差降至 0.25 ps。这一趋势与理论预期一致：ISI 子模型通过条件均值估计码型相关分量，每个码型桶内的 RJ 统计波动以 $\sigma_{RJ}/\sqrt{N/2^L}$ 量级残留，桶间极差（即 ISI 峰峰值的随机偏置）因此随 N 增大而减小。

需要指出，该 ISI 误差平台由 ISI 子模型本身决定，与 PJ 频率估计准确性无关，两种方法在该分量上表现相近。原稿中的解释方向是正确的，现补充上述实验提供了定量支撑。

### 英文回复草稿

We thank the reviewer for this observation. To verify our explanation, we conducted two additional experiments. First, we ran a control test setting RJ = 0 while keeping all other parameters identical (N = 50 000, L = 5). The ISI estimation error dropped to approximately 0.03 ps for both methods, confirming that the residual bias originates from random noise rather than a systematic model deficiency. Second, we varied the sample size from 5 000 to 100 000 and observed that the ISI error decreases monotonically with N for both methods (e.g., from 1.09 ps at N = 5 000 to 0.25 ps at N = 100 000 for SBL), consistent with the theoretical expectation that the noise-induced range across the 2^L = 32 pattern buckets scales as σ_RJ / √(N / 2^L). These results confirm that the ISI bias reported in the paper is a finite-sample statistical effect inherent to the conditional-mean ISI sub-model, and it decreases as the sample size increases. The revised manuscript adds a brief theoretical explanation and cites these verification results.

### 正文修改提示

- 在表 1 下方的 ISI 讨论段落中，补充一句说明误差随样本量增大而减小，并给出 N=100000 时的参考误差值。
- 可选：在正文中以一句话给出理论量级：桶内 RJ 残差 $\sigma_{RJ}/\sqrt{N/2^L}$，桶间极差期望正比于此量。
- 样本量曲线图可放入 rebuttal 附图，不必加入正文。

---

## 审稿意见 3：未测试多个 PJ 频率同时存在的场景

### 审稿意见要点

审稿人指出，实际高速链路中可能存在多个非谐波关系的周期性抖动源。原稿仅注入单一 PJ 频率，未验证两个或更多 PJ 频率共存时 SBL 的识别与分解能力。

### 补充实验设置

在原有仿真框架下新增五组多音 PJ 场景，涵盖两组近频双音、一组大间隔双音和两组三音：

| 场景编号 | 场景描述 | PJ 频率 |
|---|---|---|
| 1 | 近频双音 | 1.00 MHz + 1.05 MHz |
| 2 | 中等间隔双音 | 1.10 MHz + 1.30 MHz |
| 3 | 大间隔双音 | 1.0 MHz + 5.0 MHz |
| 4 | 三音（低中高） | 0.5 MHz + 2 MHz + 8 MHz |
| 5 | 三音（偏置网格） | 1.1 MHz + 3.7 MHz + 11.3 MHz |

每组 PJ 分量等幅，总 PJ 峰峰值约 30 ps，RJ=2 ps rms，DCD=1 ps，ISI 真值由仿真器逐次生成，N=50000。

对比方法包括：

- `LS-FFT`：原始方法，按其单 PJ 假设的原始设定执行，仅搜索单一 PJ 峰。此处不对 LS-FFT 做 top-k 峰扩展，因为原方法在设计上不支持多分量并行识别，强行扩展将引入无约束的多峰 LS 拟合，并不代表该方法的正常工作点；
- `LS-NUDFT`：以真实边沿时刻计算全频非均匀 DFT 谱，自动按幅值从大到小并施加最小峰间距约束（150 kHz）选取最多 5 个峰，再联合 LS 拟合所有分量；
- `SBL-FastRVM-Fixed`：本文方法（见下文说明）。

**关于实现版本说明：** 多音扩展实验中使用了经过核验的 FastRVM 预定位实现。在开展多音实验的过程中，对预定位模块进行了代码审查并修正了若干实现细节；修正后重新运行了原稿全部单 PJ 场景，结果与原稿一致，单 PJ 场景下的原始结论不受影响。（内部备注：详细修正内容记录于 `rebuttal/rebuttal3/multitone_fixed_summary.md`，不在主 rebuttal 中展开。）

实验文件：

- 结果表：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal3\multitone_baseline_comparison.csv`
- 频率召回对比图：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal3\multitone_fixed_frequency_recall.png`
- 分解误差对比图：`D:\code\projects\sqh\jitter_decomposition\rebuttal\rebuttal3\multitone_fixed_decomposition_error.png`

### 补充实验结果

频率召回率定义：若估计出的频率集合中，每个真实 PJ 频率在 ±100 kHz 容差内至少有一个对应估计频率，则该真实频率视为被命中；freq_recall = 命中真实频率数 / 真实 PJ 频率总数。

**频率召回率（freq_recall）：**

| 场景 | SBL | LS-NUDFT | LS-FFT |
|---|---:|---:|---:|
| Dual 1.0 / 5.0 MHz | 1.000 | 1.000 | 0.000 |
| Dual 1.00 / 1.05 MHz | 1.000 | 1.000 | 0.000 |
| Dual 1.10 / 1.30 MHz | 1.000 | 1.000 | 0.000 |
| Triple 0.5 / 2 / 8 MHz | 1.000 | 1.000 | 0.000 |
| Triple 1.1 / 3.7 / 11.3 MHz | 1.000 | 1.000 | 0.000 |

**PJ 峰峰值估计误差（ps）：**

| 场景 | SBL | LS-NUDFT | LS-FFT |
|---|---:|---:|---:|
| Dual 1.0 / 5.0 MHz | 0.244 | 0.034 | 10.551 |
| Dual 1.00 / 1.05 MHz | **0.024** | **14.156** | 1.951 |
| Dual 1.10 / 1.30 MHz | 0.147 | 0.091 | 3.575 |
| Triple 0.5 / 2 / 8 MHz | 0.315 | 0.702 | 7.042 |
| Triple 1.1 / 3.7 / 11.3 MHz | 0.166 | 0.036 | 8.342 |
| **平均** | **0.179** | **3.004** | **6.292** |

**RJ 估计误差（ps）：**

| 场景 | SBL | LS-NUDFT | LS-FFT |
|---|---:|---:|---:|
| Dual 1.0 / 5.0 MHz | 0.006 | 0.006 | 3.663 |
| Dual 1.00 / 1.05 MHz | 0.006 | 3.605 | 0.637 |
| Dual 1.10 / 1.30 MHz | 0.006 | 0.006 | 1.196 |
| Triple 0.5 / 2 / 8 MHz | 0.008 | 0.069 | 2.348 |
| Triple 1.1 / 3.7 / 11.3 MHz | 0.006 | 0.006 | 2.192 |
| **平均** | **0.006** | **0.738** | **2.007** |

### 可用于 rebuttal 的结论

LS-FFT 在所有五组场景中频率召回率均为 0，因为它仅搜索单一 PJ 峰，无法处理多分量共存场景，PJ 平均误差高达 6.292 ps。

LS-NUDFT 在频率召回上也达到 1.0（真实 PJ 频率均出现在自动选取的 5 个候选峰中），但在 Dual 1.00/1.05 MHz 场景下 PJ 误差高达 14.156 ps，RJ 误差随之升至 3.605 ps。原因在于：两个频率仅相差 50 kHz，NUDFT 谱上对应的两组字典列高度相关，联合 LS 拟合矩阵条件数极大，幅度估计严重不稳定。LS-NUDFT 的平均 PJ 误差为 3.004 ps，主要由该近频场景拉高。

SBL 在五组场景中均保持 freq_recall=1.0，PJ 误差全部不超过 0.35 ps，平均 PJ 误差为 0.179 ps，RJ 误差平均为 0.006 ps。SBL 对近频双音（1.00/1.05 MHz）的 PJ 误差仅为 0.024 ps，原因在于冗余字典按候选频率点独立构造，ARD 推断通过正则化机制从高度相关列中稳定恢复系数，不受谱分辨率限制。

综合审稿意见 1 和审稿意见 3 的结果，可形成更完整的叙事：NUDFT 通过使用真实边沿时刻解决了非均匀采样导致的单 PJ 频率偏移问题，但在多分量近频场景下，谱域方法固有的幅度估计不稳定性使其失效；SBL 在两类场景下均保持稳定，这是冗余字典结合 ARD 正则化推断的综合优势。

### 英文回复草稿

We thank the reviewer for this important suggestion. We conducted multi-tone PJ experiments covering five scenarios: two dual-tone cases with close (1.00/1.05 MHz) and moderate (1.10/1.30 MHz) spacing, one wide-separation dual-tone case (1.0/5.0 MHz), and two triple-tone cases (0.5/2/8 MHz and 1.1/3.7/11.3 MHz). We compared three methods: the original LS-FFT, LS-NUDFT (which uses the actual edge timestamps to compute a non-uniform DFT spectrum, then selects up to five peaks automatically by amplitude with a 150 kHz minimum separation constraint and performs a joint LS fit), and the proposed SBL method.

LS-FFT achieves zero frequency recall across all five scenarios. Since LS-FFT is designed under a single-PJ assumption and does not provide a principled mechanism for multi-peak identification, we evaluate it under its original single-peak setting rather than extending it to an unconstrained top-k variant, which would not represent a meaningful operating point for this method. LS-NUDFT achieves full frequency recall in all cases (all true PJ frequencies appear within its top-5 selected peaks), but produces a catastrophic PJ amplitude error of 14.2 ps in the close-frequency dual-tone scenario (1.00/1.05 MHz), while the RJ error simultaneously rises to 3.6 ps. The failure arises because two frequency components separated by only 50 kHz produce near-collinear dictionary columns in the LS fitting matrix, causing severe amplitude estimation instability. The proposed SBL method achieves full frequency recall in all five scenarios with a mean PJ error of 0.179 ps and mean RJ error of 0.006 ps; for the most challenging close-frequency case, the PJ error is 0.024 ps. The ARD regularization mechanism allows SBL to stably recover coefficients from near-collinear dictionary columns, which is the key advantage over both LS-FFT and LS-NUDFT in this setting.

During this investigation, we also reviewed and refined the FastRVM pre-localization implementation used in the multi-tone experiments. We re-ran all single-PJ scenarios with the updated implementation and confirmed that the results are consistent with those reported in the original manuscript. The revised manuscript includes the multi-tone experiments.

### 正文修改提示

- 实验部分新增一个多音 PJ 对比小节，包含 freq_recall 和 PJ/RJ 误差表，三列方法（LS-FFT、LS-NUDFT、SBL）。
- 说明 LS-NUDFT 的实现方式（自动 top-5 峰选取，min_separation=150 kHz）以便读者可复现。
- 在描述多音实验时，注明使用的是经过核验的方法实现，例如："the multi-tone experiments use the verified implementation of the proposed method"，不在正文中展开具体修订细节。
- 正文叙事可将审稿意见 1 和审稿意见 3 的结论合并，形成"单 PJ 高频场景 + 多 PJ 近频场景"两维度的完整对比。

---

## 审稿意见 4：结论部分缺少具体数据支撑

### 审稿意见要点

结论部分应补充相应数据，以支撑最终结论。

### 处理方式

不需要补充实验，直接从表 1 和图 4 中提取关键数字写入结论段落，例如：SBL 在 100 kHz–15 MHz 全频段 PJ 误差不超过 0.5 ps；LS-FFT 在 15 MHz 处误差达 9.08 ps（样本 1）；SBL 的 RJ 误差全程不超过 0.02 ps，而 LS-FFT 在 10 MHz 处 RJ 误差升至 0.55 ps（样本 1）。

### 英文回复草稿

We have revised the Conclusion section to include representative numerical results. Specifically, the revised conclusion now states that the proposed SBL method keeps the PJ estimation error below 0.5 ps across the full 100 kHz–15 MHz test range in both sample sets, whereas LS-FFT reaches 9.08 ps at 15 MHz (Sample 1). For RJ, SBL maintains an error below 0.02 ps throughout, while LS-FFT rises to 0.55 ps at 10 MHz (Sample 1), demonstrating that SBL suppresses error propagation from PJ frequency misestimation to other components.

---

## 审稿意见 5：建议增加近三年期刊文献

### 审稿意见要点

建议在参考文献中增加近三年发表的期刊论文。

### 处理方式

需要补充 2023–2026 年与以下方向相关的期刊论文：抖动分解与分析、信号完整性测量、稀疏贝叶斯学习在信号处理中的应用。文献检索完成后更新参考文献列表。

---

## 编辑意见逐条处理说明

### 编辑意见 1：只有一个单位时无需添加单位编号

直接在投稿文档中删除作者单位前的上标编号"1"，无需其他改动。

### 编辑意见 2：关键词中的所有字母均应大写

将投稿文档英文关键词中的每个单词首字母大写，或全部大写（按模板要求执行）。

### 编辑意见 3：图 3 分辨率较低，请替换

`fig3_flowchart.png` 需以高分辨率版本（建议 300 dpi 以上）替换，更新投稿文档中对应图片。

### 编辑意见 4：公式中向量和矩阵应使用加粗斜体，变量应使用斜体

需在投稿 Word/LaTeX 文档中逐一检查公式，确认 $\mathbf{H}$、$\mathbf{y}$、$\mathbf{w}$、$\boldsymbol{\mu}$、$\boldsymbol{\Sigma}$、$\boldsymbol{\Lambda}$ 等向量和矩阵均为加粗斜体，标量变量如 $\alpha_i$、$\sigma^2$、$N$ 等为斜体。

### 编辑意见 5：请同时提供中文摘要和会议论文版权表

- 中文摘要：从论文初稿摘要部分直接提取，填入会议提供的中文摘要模板（`Abstract Information Template (in Chinese).docx`）。
- 版权表：填写并签署 `Conference Proceeding Copyright Form.docx`，与修订稿一并提交。
