# A Sparse Bayesian Learning Approach to Multi-Component Jitter Decomposition

## Abstract

Accurate decomposition of individual jitter components from a time interval error (TIE) sequence is essential for signal integrity assessment in high-speed digital communications. Existing frequency-domain methods estimate the periodic jitter (PJ) frequency by FFT peak-picking and fit the amplitudes by least squares. However, the non-uniform spacing of data transition edges in pseudo-random binary sequence (PRBS) signals violates the FFT's uniform-sampling assumption. The resulting frequency bias propagates to the amplitudes of all components. To address this limitation, a sparse Bayesian learning (SBL) approach to jitter decomposition is proposed. A redundant dictionary whose frequency resolution can be designed independently is constructed, and its active columns are identified by the automatic relevance determination (ARD) mechanism replacing FFT peak-picking. To accelerate the inference, the active frequencies are first localised on a coarse grid by the fast relevance vector machine (FastRVM); a fine ARD inference is then carried out within the resulting neighbourhoods. Experimental results show that the proposed method confines the PJ estimation error within 0.5 ps over the 100 kHz – 15 MHz band and suppresses error propagation to the RJ component; in multi-PJ scenarios, the ARD mechanism can identify the true frequency components without presetting the number of PJ frequencies, confirming the accuracy and robustness of the proposed approach.

**Keywords:** JITTER DECOMPOSITION; PERIODIC JITTER; SPARSE BAYESIAN LEARNING; REDUNDANT DICTIONARY

***

## 1 Introduction

As data rates in high-speed digital communications continue to rise, systems impose ever more stringent constraints on timing precision and signal integrity. Jitter, being the dominant factor that affects the bit error rate (BER), has become a key indicator in signal integrity assessment <sup>[1]</sup>. Acquiring the time interval error (TIE) sequence with an oscilloscope and decomposing it precisely into its constituent components is the foundation for evaluating system performance and locating sources of disturbance <sup>[2,3]</sup>. According to physical origin and statistical properties, total jitter (TJ) is conventionally split into random jitter (RJ) and deterministic jitter (DJ); the latter is further subdivided into inter-symbol interference (ISI), duty-cycle distortion (DCD) and periodic jitter (PJ) <sup>[4]</sup>.

Existing jitter decomposition methods can be broadly grouped into statistical-domain, time-domain and frequency-domain approaches. Statistical-domain methods, exemplified by tail fitting <sup>[5]</sup> and the dual-Dirac model <sup>[6, 7]</sup>, achieve a fast separation of RJ and DJ but provide no explicit model for the pattern dependence of ISI. Time-domain methods such as time lag correlation (TLC) <sup>[8]</sup> employ correlation functions to separate correlated and uncorrelated jitter components but cannot directly extract the frequency information of PJ. Frequency-domain methods such as the FFT-based spectral peak-picking <sup>[9]</sup> reveal the frequency structure of PJ intuitively but likewise lack an explicit model for the pattern dependence of ISI. Recently, deep-learning-based methods <sup>[10,11]</sup> have also made some progress, although they typically rely on large amounts of labelled data and offer limited interpretability.

Duan *et al.* <sup>[12]</sup> proposed a least-squares decomposition based on a linear superposition model of the TIE, in which the PJ frequency is located by FFT peak-picking and the amplitudes are then fitted by least squares (referred to here as LS-FFT). The method incorporates the four components — PJ, ISI, DCD and RJ — into a unified linear model, and the amplitude of each component can be estimated jointly from a small number of TIE samples. The accuracy of this method, however, hinges on an accurate FFT frequency estimate. The TIE is defined only at data transition edges; consecutive identical bits in real data patterns produce no transition, so adjacent TIE samples are not equally spaced on the time axis and the uniform-sampling assumption of the FFT is violated. The FFT peak therefore deviates from the true PJ frequency (Fig. 1). Furthermore, when the PJ frequency falls between two DFT bins, the picket-fence effect aggravates this bias. Fitting the PJ component with a frequency that has been shifted, the basis functions no longer align with the true signal; the amplitude estimate becomes inaccurate and errors propagate to the ISI and RJ components.

![[fig1_nonuniform_sampling.png]]

Fig. 1  Non-uniform edge distribution of a PRBS signal.

To address this issue, a multi-component jitter decomposition method based on sparse Bayesian learning (SBL) is proposed. Building upon the linear superposition model of Duan *et al.* <sup>[12]</sup>, a redundant dictionary containing a large set of candidate frequencies is constructed using the actual transition instants in place of a single frequency column, so that the spacing and number of candidate frequencies are no longer constrained by the number of samples. The automatic relevance determination (ARD) mechanism inherent in SBL is then used to select the true PJ frequency directly from the redundant dictionary. FFT peak-picking is no longer required, and the frequency-estimation bias caused by non-uniform sampling and the picket-fence effect is avoided. Furthermore, the ARD mechanism automatically determines the number of active components without presetting the number of PJ frequencies, making the method equally applicable to multi-PJ scenarios.


## 2 Signal Model and Dictionary Construction

### 2.1 Linear TIE Model

The TIE at the *k*th transition edge can be decomposed, according to its physical origin, into a linear superposition of deterministic components and random noise:

$$y(k) = y_{PJ}(k) + y_{ISI}(k) + y_{DCD}(k) + v(k) \tag{1}$$

where $v(k)$ comprises random jitter and observation noise. Stacking the TIE samples over $N$ transition edges in matrix form <sup>[12]</sup>:

$$\mathbf{y} = [\mathbf{A}(f_0) \mid \mathbf{B} \mid \mathbf{C}]\mathbf{x} + \mathbf{v} \tag{2}$$

The PJ sub-matrix $\mathbf{A}(f_0) \in \mathbb{R}^{N \times 2}$ has columns $d_n \cos(2\pi f_0 n / f_s)$ and $d_n \sin(2\pi f_0 n / f_s)$, where $d_n$ is the transition indicator (1 at a transition, 0 otherwise); the DCD sub-matrix $\mathbf{B} \in \mathbb{R}^{N \times 1}$ is set to $+1$ on rising edges and $-1$ on falling edges; the ISI sub-matrix $\mathbf{C} \in \mathbb{R}^{N \times 2^L}$ buckets the rows by the history pattern within memory depth $L$, placing a $1$ in the column corresponding to the current pattern of each row. 

The accuracy of the solution to (2) hinges on whether $\mathbf{A}(f_0)$ reflects the true phase structure of the PJ component on the TIE sequence. The phase term $2\pi f_0 n / f_s$ in the *n*th row of $\mathbf{A}(f_0)$ approximates the *n*th transition as a uniformly sampled point at $n/f_s$. Under PRBS patterns, however, consecutive identical bits produce no transition, so adjacent transitions are not equally spaced in time; the phase bias introduced by this approximation causes the FFT-based estimate of $f_0$ to deviate systematically from its true value, and the bias is propagated through the least-squares fit to the PJ and the other component amplitudes.


### 2.2 Redundant Frequency Dictionary

Rather than relying on FFT peak-picking, this paper places $K$ candidate frequencies in the target band, constructs the dictionary column for each candidate using the actual transition arrival times $t_n$, and identifies the active frequencies by SBL. Here $t_n$ denotes the ideal arrival time of the *n*th transition edge: in a PRBS test the transmitted pattern is known, so the transition positions can be determined directly from the pattern, $t_n = \text{edge\_index}(n) / f_s$, and this information is available when the TIE sequence is extracted.

For each candidate frequency $f_i$, a pair of cosine and sine basis columns is constructed:

$$\begin{aligned}
\mathbf{h}_{c,i} &= [d_1\cos(2\pi f_i t_1), \ldots, d_N\cos(2\pi f_i t_N)]^T \\
\mathbf{h}_{s,i} &= [d_1\sin(2\pi f_i t_1), \ldots, d_N\sin(2\pi f_i t_N)]^T
\end{aligned} \tag{3}$$

A PJ component with arbitrary initial phase can be expressed linearly as $a_i \mathbf{h}_{c,i} + b_i \mathbf{h}_{s,i}$, converting non-linear phase estimation into linear coefficient estimation. Concatenating the basis-column pairs of the $K$ candidate frequencies horizontally yields the PJ sub-dictionary

$$\mathbf{H}_{PJ} = [\mathbf{h}_{c,1}, \mathbf{h}_{s,1}, \ldots, \mathbf{h}_{c,K}, \mathbf{h}_{s,K}] \in \mathbb{R}^{N \times 2K} \tag{4}$$

The spacing and number of the candidate frequencies $f_1, \ldots, f_K$ are not constrained by the DFT grid $\Delta f = f_s/N$ and may be chosen flexibly according to the target band. Concatenating $\mathbf{H}_{PJ}$ with $\mathbf{B}$ and $\mathbf{C}$ yields the global redundant dictionary:

$$\mathbf{H} = [\mathbf{H}_{PJ} \mid \mathbf{B} \mid \mathbf{C}] \in \mathbb{R}^{N \times M}, \quad M = 2K + 1 + 2^L \tag{5}$$

After solving for the coefficient vector $\hat{\mathbf{x}}$, the physical quantity of each component is extracted as follows. The coefficient pair $(\hat{a}_i, \hat{b}_i)$ at an active frequency $f_i$ gives the peak-to-peak PJ amplitude

$$\text{Pk-Pk}_{PJ} = 2\sqrt{\hat{a}_i^2 + \hat{b}_i^2} \tag{6}$$

The DCD and ISI peak-to-peak values are $\text{Pk-Pk}_{DCD} = 2|\hat{x}_{DCD}|$ and $\text{Pk-Pk}_{ISI} = \max(\hat{\mathbf{x}}_{ISI}) - \min(\hat{\mathbf{x}}_{ISI})$, respectively; the RMS RJ is estimated from the fitting residual,

$$\hat{\sigma}_{RJ} = \sqrt{\frac{\|\mathbf{y} - \mathbf{H}\hat{\mathbf{x}}\|_2^2}{N - P}} \tag{7}$$

where $P$ is the number of active columns in $\mathbf{H}$.

Adjacent candidate-frequency columns of $\mathbf{H}$ are highly correlated, $\mathbf{H}^T\mathbf{H}$ is severely ill-conditioned, and a direct least-squares solution is numerically unstable. In a real system the number of PJ disturbance sources present simultaneously is small, so only a few entries of the coefficient vector are non-zero, and the problem reduces to identifying the columns associated with these non-zero coefficients and estimating their values. Sparse Bayesian learning (SBL) provides a probabilistic inference framework for sparse-recovery problems of this kind <sup>[13,14]</sup>.

***
## 3 SBL-Based Jitter Decomposition Algorithm

The frequency resolution of the redundant dictionary is not bounded by the number of samples, but a finer resolution implies a larger number of candidate columns. Were a fine dictionary with thousands of columns to be constructed directly, ARD would have to update all columns simultaneously, with a computational cost that grows quadratically in the number of columns and prohibitive single-pass inference times. FastRVM, by contrast, performs a sequential update that processes only one column at each step and is efficient on large coarse-grid dictionaries; the coarse spacing, however, limits the achievable frequency resolution. The inference is therefore carried out in two stages: FastRVM is first used on a coarse grid to localise the approximate intervals of the PJ frequencies, and a fine dictionary is then constructed within these intervals so that ARD can deliver an accurate frequency and amplitude estimate. Both stages identify the active frequency columns by maximising the marginal likelihood; the complete algorithmic flow is shown in Fig. 2.

![[图表/fig3_flowchart.png]]

Fig. 2  Flowchart of the SBL-based jitter decomposition algorithm.

### 3.1 FastRVM Coarse Localisation

The aim of the coarse-localisation stage is to determine the approximate intervals of the PJ frequencies within the 100 kHz – 15 MHz band.

SBL assigns an independent zero-mean Gaussian prior to each entry of the coefficient vector $\mathbf{w}$ <sup>[13]</sup>:

$$w_i \sim \mathcal{N}(0, \alpha_i^{-1}) \tag{8}$$

where $\alpha_i$ is the precision hyperparameter; $\alpha_i \to \infty$ effectively prunes the corresponding column from the model. The hyperparameters $\{\alpha_i\}$ are estimated from the data by maximisation of the marginal likelihood, and on convergence only a few columns retain a finite $\alpha_i$, achieving sparse recovery.

100 candidate frequencies are uniformly placed across 100 kHz – 15 MHz, giving a 200-column PJ sub-dictionary by (3)–(4); concatenation with $\mathbf{B}$ and $\mathbf{C}$ yields a coarse global dictionary of 233 columns. Sequential sparse inference <sup>[15]</sup> is then applied to this dictionary by FastRVM. Let the observation model be $\mathbf{y} = \mathbf{H}\mathbf{w} + \boldsymbol{\varepsilon}$ with $\boldsymbol{\varepsilon} \sim \mathcal{N}(\mathbf{0}, \sigma^2 \mathbf{I})$.

Rather than iterating on all columns simultaneously, FastRVM maintains an active set $\mathcal{A}$, initially empty, and at each step decides whether to add or remove a single column. When the *i*th column is examined, its quality factor $Q_i$ and sparsity factor $S_i$ relative to the current residual are computed:

$$Q_i = \mathbf{h}_i^T \boldsymbol{\Phi}^{-1} \mathbf{y}, \quad S_i = \mathbf{h}_i^T \boldsymbol{\Phi}^{-1} \mathbf{h}_i \tag{9}$$

where $\mathbf{h}_i$ is the *i*th dictionary column and $\boldsymbol{\Phi} = \sigma^2\mathbf{I} + \mathbf{H}_\mathcal{A}\boldsymbol{\Lambda}_\mathcal{A}^{-1}\mathbf{H}_\mathcal{A}^T$ is the marginal covariance for the current active set $\mathcal{A}$. $Q_i$ measures the contribution of column $i$ to fitting the residual and $S_i$ reflects its energy. Together, they form the sparsity–quality criterion <sup>[15]</sup>:

$$\theta_i = Q_i^2 - S_i \tag{10}$$

If $\theta_i > 0$, the fit improvement obtained by including the column outweighs the complexity penalty of admitting it; the column is added to the active set, and $\alpha_i$ is updated to its closed-form maximiser of the marginal likelihood:

$$\alpha_i^{\mathrm{new}} = \frac{S_i^2}{\theta_i} \tag{11}$$

If $\theta_i \leq 0$, $\alpha_i$ is set to infinity and the column is removed from the model. The above procedure is applied sequentially to each column and iterated until the active set no longer changes. After convergence, for every candidate frequency $f_k$ the relevances of its sine and cosine columns are summed, $1/\alpha_{2k-1} + 1/\alpha_{2k}$, and the candidates are ranked in decreasing order of this sum; the three highest are taken as the candidate centre frequencies $\hat{f}_1, \hat{f}_2, \hat{f}_3$ for the subsequent fine inference. The coarse-localisation result is shown in Fig. 3(a).

![[图表/fig2_fastrvm_compression.png]]

Fig. 3  FastRVM coarse localisation and ARD fine-dictionary construction.

### 3.2 ARD-Based Fine Frequency Identification

The frequency resolution of FastRVM on the coarse grid is approximately 150 kHz, so $\hat{f}_1, \hat{f}_2, \hat{f}_3$ provide only the approximate location of the true frequencies; a fine dictionary is required in the surrounding neighbourhoods to deliver an accurate frequency and amplitude estimate. A fine window of $\pm 200$ kHz is centred at each $\hat{f}_i$, covering the coarse-localisation error of FastRVM (about $\pm 75$ kHz) and ensuring that the true PJ frequency lies inside the window. 100 candidate frequencies are uniformly placed in each window with a spacing of approximately 4 kHz, and the three windows are merged to give 300 fine candidate frequencies. The fine global dictionary $\mathbf{H}$ is then assembled via (3)-(5), giving $M = 600 + 1 + 32 = 633$ (Fig. 3(b)).

Adjacent fine-candidate columns are highly correlated and a direct least-squares solution is numerically unstable. The same ARD prior as in (8) is imposed on $\mathbf{H}$. By the conjugacy of the Gaussian prior and the Gaussian observation model, the posterior distribution $p(\mathbf{w} \mid \mathbf{y})$ is Gaussian, with mean and covariance

$$\boldsymbol{\mu} = \sigma^{-2}\boldsymbol{\Sigma}\mathbf{H}^T\mathbf{y}, \quad \boldsymbol{\Sigma} = \left(\sigma^{-2}\mathbf{H}^T\mathbf{H} + \boldsymbol{\Lambda}\right)^{-1} \tag{12}$$

where $\boldsymbol{\Lambda} = \mathrm{diag}(\alpha_1, \ldots, \alpha_M)$. The posterior mean $\boldsymbol{\mu}$ serves as the coefficient estimate.

The hyperparameters $\{\alpha_i\}$ and the noise variance $\sigma^2$ are not specified manually; they are estimated jointly from the data by maximising the marginal likelihood $p(\mathbf{y} \mid \{\alpha_i\}, \sigma^2)$, with the update rules

$$\alpha_i^{\mathrm{new}} = \frac{1 - \alpha_i \Sigma_{ii}}{\mu_i^2}, \quad (\sigma^2)^{\mathrm{new}} = \frac{\|\mathbf{y} - \mathbf{H}\boldsymbol{\mu}\|^2}{N - \sum_i(1 - \alpha_i\Sigma_{ii})} \tag{13}$$

where $\Sigma_{ii}$ is the *i*th diagonal entry of the posterior covariance matrix. The updates of $\alpha_i$ and $\sigma^2$ are alternated until convergence.

After inference, the posterior mean $\boldsymbol{\mu}$ is taken directly as the coefficient estimate of each component: the coefficient pairs $(\hat{a}_i, \hat{b}_i)$ at the active frequencies provide the peak-to-peak PJ amplitude via (6); the DCD and ISI coefficients give the corresponding component amplitudes; and the RMS RJ is estimated from the residual via (7).

***

## 4 Experimental Results

To verify the effectiveness of the proposed method, simulation experiments are designed to evaluate the wide-band PJ estimation accuracy, the multi-component joint decomposition accuracy, and performance under multi-PJ scenarios, comparing LS-FFT <sup>[12]</sup>, LS-NUDFT and the proposed SBL method. LS-NUDFT constructs a non-uniform DFT spectrum from the actual transition instants, takes the dominant spectral peak frequency, and fits the component amplitudes by least squares; it represents a strong baseline among frequency-domain correction methods. The simulated data are TIE sequences generated under PRBS-7 patterns at a 2 Gbps data rate, with 50 000 samples collected, channel memory depth $L=5$, and DCD and ISI ground truths set to 1.0 ps and 0.16 ps, respectively. Since the PJ frequency has a significant influence on the estimation accuracy of frequency-domain methods, the experiments scan the PJ frequency over 100 kHz – 15 MHz to compare the decomposition performance of the three methods. Two parameter sets are used: Sample 1 with PJ = 10.0 ps and RJ = 5.0 ps; Sample 2 with PJ = 6.0 ps and RJ = 5.0 ps.

Six frequency points (0.1, 0.5, 1, 5, 10 and 15 MHz) are selected within 100 kHz – 15 MHz, and the peak-to-peak PJ estimation errors of the three methods for the two parameter sets are shown in Fig. 4.

![[fig4_full_nudft_comparison.png]]

Fig. 4  Comparison of wide-band PJ estimation errors of three methods for the two samples.

As shown in Fig. 4, the LS-FFT PJ error increases markedly with frequency, reaching 9.08 ps (Sample 1) and 5.52 ps (Sample 2) at 15 MHz. After the non-uniform DFT is constructed from the actual transition instants $t_n$, LS-NUDFT mitigates this bias substantially, keeping the error below 0.7 ps across the full band, with mean errors of 0.48 ps and 0.60 ps in the two samples, although some fluctuation remains across frequency points. SBL keeps the PJ error within 0.5 ps at all six frequency points in both samples, with mean errors of 0.30 ps and 0.28 ps, and exhibits smaller inter-frequency variation. This indicates that ARD can identify the active frequencies directly from the fine dictionary with less disturbance from spectral-peak selection.

Three frequency points (0.1, 1.0 and 10.0 MHz) are then chosen to compare the simultaneous decomposition accuracy of the four components — PJ, DCD, ISI and RJ — and the errors are reported in Table 1.

Table 1  Multi-component decomposition errors (ps). Ground truth — Sample 1: PJ = 10.00, DCD = 1.00, ISI = 0.16, RJ = 5.00; Sample 2: PJ = 6.00, DCD = 1.00, ISI = 0.16, RJ = 5.00.

<table>
  <thead>
    <tr>
      <th rowspan="2">Sample</th>
      <th rowspan="2"><i>f</i><sub>PJ</sub><br>(MHz)</th>
      <th colspan="4">LS-FFT Error (ps)</th>
      <th colspan="4">LS-NUDFT Error (ps)</th>
      <th colspan="4">SBL Error (ps)</th>
    </tr>
    <tr>
      <th>PJ</th><th>DCD</th><th>ISI</th><th>RJ</th>
      <th>PJ</th><th>DCD</th><th>ISI</th><th>RJ</th>
      <th>PJ</th><th>DCD</th><th>ISI</th><th>RJ</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3">1</td>
      <td>0.1</td>
      <td>0.25</td><td>0.04</td><td>0.41</td><td>0.01</td>
      <td>0.44</td><td>0.04</td><td>0.40</td><td>0.02</td>
      <td>0.02</td><td>0.03</td><td>0.30</td><td>0.01</td>
    </tr>
    <tr>
      <td>1.0</td>
      <td>1.29</td><td>0.04</td><td>0.48</td><td>0.06</td>
      <td>0.63</td><td>0.04</td><td>0.42</td><td>0.02</td>
      <td>0.46</td><td>0.03</td><td>0.30</td><td>0.01</td>
    </tr>
    <tr>
      <td>10.0</td>
      <td>1.28</td><td>0.04</td><td>0.44</td><td>0.55</td>
      <td>0.56</td><td>0.04</td><td>0.42</td><td>0.02</td>
      <td>0.50</td><td>0.03</td><td>0.30</td><td>0.02</td>
    </tr>
    <tr>
      <td rowspan="3">2</td>
      <td>0.1</td>
      <td>0.44</td><td>0.04</td><td>0.42</td><td>0.01</td>
      <td>0.56</td><td>0.04</td><td>0.41</td><td>0.00</td>
      <td>0.01</td><td>0.03</td><td>0.30</td><td>0.01</td>
    </tr>
    <tr>
      <td>1.0</td>
      <td>0.86</td><td>0.04</td><td>0.44</td><td>0.01</td>
      <td>0.68</td><td>0.04</td><td>0.42</td><td>0.02</td>
      <td>0.43</td><td>0.03</td><td>0.30</td><td>0.01</td>
    </tr>
    <tr>
      <td>10.0</td>
      <td>0.94</td><td>0.04</td><td>0.42</td><td>0.20</td>
      <td>0.61</td><td>0.04</td><td>0.42</td><td>0.02</td>
      <td>0.37</td><td>0.03</td><td>0.30</td><td>0.02</td>
    </tr>
  </tbody>
</table>

As shown in Table 1, the DCD errors of all three methods remain within 0.03–0.04 ps, indicating that this component is insensitive to PJ frequency-identification errors. For the PJ component, the SBL error remains within 0.50 ps throughout, whereas the LS-FFT error rises to 1.28 ps and 0.94 ps at 10.0 MHz in the two samples; LS-NUDFT reduces the error at this frequency to 0.56 ps and 0.61 ps, with mean PJ errors of 0.54 ps (Sample 1) and 0.62 ps (Sample 2), intermediate between LS-FFT and SBL. For the RJ component, the LS-FFT error rises to 0.55 ps and 0.20 ps at 10.0 MHz, whereas LS-NUDFT and SBL both keep it within 0.02 ps, indicating that more accurate frequency identification can reduce error propagation to the residual component. For the ISI component, the SBL error is approximately 0.30 ps, while LS-NUDFT and LS-FFT give approximately 0.40–0.48 ps, with no clear dependence on PJ frequency. This offset mainly arises from the finite-sample statistical fluctuation of RJ noise when conditional means are taken over the $2^L = 32$ pattern bins of the $\mathbf{C}$ matrix. Its magnitude is approximately $\sigma_{RJ}/\sqrt{N/2^L}$; when $N$ is increased from 50 000 to 100 000, the SBL ISI error drops from 0.33 ps to 0.25 ps, and LS-FFT exhibits the same trend, consistent with the theoretical expectation.

To investigate the identification and decomposition capability under multi-PJ scenarios, five multi-tone experiments are further designed (equal-amplitude components, total PJ peak-to-peak approximately 30 ps, RJ = 2 ps rms, DCD = 1 ps, $N = 50\,000$): near-frequency dual-tone 1.00/1.05 MHz, medium-separation dual-tone 1.10/1.30 MHz, wide-separation dual-tone 1.0/5.0 MHz, triple-tone 0.5/2/8 MHz, and triple-tone 1.1/3.7/11.3 MHz. In the Dual/Tri scenarios, the numbers following the labels denote the injected PJ frequencies in MHz. Frequency identification is assessed with a $\pm 100$ kHz matching tolerance: a scenario is considered to have achieved true PJ frequency identification if every true PJ frequency can be matched to a frequency in the estimated set. Across all five scenarios, both LS-NUDFT and SBL achieve true PJ frequency identification, whereas LS-FFT, which searches for only one dominant peak under a single-PJ assumption, cannot cover multi-frequency scenarios. The PJ and RJ decomposition errors are listed in Table 2.

Table 2  Decomposition errors under multi-PJ scenarios (ps).

<table>
  <thead>
    <tr>
      <th rowspan="2">Scenario</th>
      <th colspan="3">PJ Error (ps)</th>
      <th colspan="3">RJ Error (ps)</th>
    </tr>
    <tr>
      <th>LS-FFT</th><th>LS-NUDFT</th><th>SBL</th>
      <th>LS-FFT</th><th>LS-NUDFT</th><th>SBL</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Dual-tone 1.0/5.0 MHz</td><td>10.55</td><td>0.03</td><td>0.24</td><td>3.66</td><td>0.01</td><td>0.01</td></tr>
    <tr><td>Dual-tone 1.00/1.05 MHz</td><td>1.95</td><td>14.16</td><td>0.02</td><td>0.64</td><td>3.61</td><td>0.01</td></tr>
    <tr><td>Dual-tone 1.10/1.30 MHz</td><td>3.58</td><td>0.09</td><td>0.15</td><td>1.20</td><td>0.01</td><td>0.01</td></tr>
    <tr><td>Triple-tone 0.5/2/8 MHz</td><td>7.04</td><td>0.70</td><td>0.32</td><td>2.35</td><td>0.07</td><td>0.01</td></tr>
    <tr><td>Triple-tone 1.1/3.7/11.3 MHz</td><td>8.34</td><td>0.04</td><td>0.17</td><td>2.19</td><td>0.01</td><td>0.01</td></tr>
    <tr><td><b>Mean</b></td><td>6.29</td><td>3.00</td><td>0.18</td><td>2.01</td><td>0.74</td><td>0.01</td></tr>
  </tbody>
</table>

Although LS-NUDFT covers both true frequency components of the near-frequency dual-tone scenario (1.00/1.05 MHz) within the $\pm 100$ kHz tolerance, its PJ error still reaches 14.16 ps and its RJ error rises to 3.61 ps. Because the two frequencies differ by only 50 kHz, the corresponding dictionary columns are highly correlated, and the subsequent joint LS fitting becomes ill-conditioned so that the amplitude and energy allocation becomes unstable. By contrast, SBL keeps the PJ error within 0.35 ps across all five scenarios, with a mean of 0.18 ps and only 0.02 ps in the near-frequency dual-tone scenario; the average RJ error is only 0.01 ps. As long as the true PJ components are covered by the candidate frequency set, ARD inference can recover coefficients more stably from highly correlated dictionary columns.

***

## 5 Conclusion

This paper presents a sparse Bayesian learning approach to multi-component jitter decomposition. The method retains the TIE linear superposition model, replacing conventional frequency-domain peak-picking with a redundant frequency dictionary and the ARD mechanism, to achieve PJ identification and joint multi-component estimation without any frequency prior. Experimental results demonstrate that, in single-PJ scenarios across 100 kHz–15 MHz, the SBL PJ estimation error remains within 0.5 ps and the RJ error within 0.02 ps. In five multi-PJ scenarios, SBL successfully identifies all true PJ frequency components, with a mean PJ error of 0.18 ps and an error of only 0.02 ps in the most challenging near-frequency dual-tone (1.00/1.05 MHz) scenario. These results indicate that the method maintains stable decomposition performance in both high-frequency single-tone and near-frequency multi-tone regimes, effectively mitigating the frequency bias and near-frequency amplitude instability encountered in conventional frequency-domain peak-picking methods. Future work will validate the method on measured oscilloscope data.

***

## Acknowledgements

This work is supported by the National Key Research and Development Program of China (2022YFF0707104).

***

## References

[1] Balestrieri, E., Picariello, F., Rapuano, S., et al.: ‘Review on jitter terminology and definitions’, Measurement, 2019, 145, pp. 264–273

[2] Chen, J., Ye, P., Zhao, Y., et al.: ‘Methodology for jitter analysis in digital storage oscilloscope’. Proc. IEEE 16th Int. Conf. Electronic Measurement & Instruments (ICEMI), Harbin, China, August 2023, pp. 1–6

[3] Moussa, B., Chaccour, K., Bouyekhf, R., et al.: ‘Compensating trigger jitter and time interval error measurement for digital sampling oscilloscopes with hardware design on FPGA’, Meas. Sci. Technol., 2024, 35, (7), p. 076001

[4] Tripathi, J.N., Sharma, V.K., Shrimali, H.: ‘A review on power supply induced jitter’, IEEE Trans. Compon. Packag. Manuf. Technol., 2019, 9, (3), pp. 511–524

[5] Deng, Y., Shang, Z., Tang, Z., et al.: ‘Jitter analysis and decomposition based on tail-fit algorithm’. Proc. 2024 4th Int. Conf. Communication Technology and Information Technology (ICCTIT), Guangzhou, China, December 2024, pp. 611–615

[6] Fang, S., Pan, W., Pan, D., et al.: ‘Jitter analysis based on kernel density estimation and dual-Dirac’. Proc. IEEE Int. Conf. Signal, Information and Data Processing (ICSIDP), Zhuhai, China, November 2024, pp. 1–6

[7] Peng, J., Qi, Z., Li, Z., et al.: ‘Jitter decomposition based on dual-Dirac model: a two-stage limited-sampling algorithm’. Proc. IEEE 17th Int. Conf. Electronic Measurement & Instruments (ICEMI), Beijing, China, August 2025, pp. 169–174

[8] Dou, Q., Abraham, J.A.: ‘Jitter decomposition by time lag correlation’. Proc. 7th Int. Symp. Quality Electronic Design (ISQED), San Jose, CA, USA, March 2006, pp. 525–530

[9] Yamaguchi, T.J., Ishida, M., Hou, H.X., et al.: ‘An FFT-based jitter separation method for high-frequency jitter testing with a 10× reduction in test time’. Proc. IEEE Int. Test Conf. (ITC), Santa Clara, CA, USA, October 2007, pp. 1–8

[10] Ren, N., Fu, Z., Zhou, D., et al.: ‘Jitter decomposition by convolutional neural networks’, IEEE Trans. Electromagn. Compat., 2021, 63, (4), pp. 1550–1561

[11] Wu, R., Sha, Y., Xu, Z., et al.: ‘Fusing time and distribution domains: a feature-interaction network for jitter component analysis’, IEEE Trans. Electromagn. Compat., 2026, doi: 10.1109/TEMC.2026.3679020

[12] Duan, Y., Chen, D.: ‘Fast and accurate decomposition of deterministic jitter components in high-speed links’, IEEE Trans. Electromagn. Compat., 2019, 61, (1), pp. 217–225

[13] Tipping, M.E.: ‘Sparse Bayesian learning and the relevance vector machine’, J. Mach. Learn. Res., 2001, 1, pp. 211–244

[14] Guo, Q., Xin, Z., Zhou, T., et al.: ‘Off-grid space alternating sparse Bayesian learning’, IEEE Trans. Instrum. Meas., 2023, 72, Art. no. 1002310

[15] Faul, A.C., Tipping, M.E.: ‘Analysis of sparse Bayesian learning’, in Dietterich, T.G., Becker, S., Ghahramani, Z. (Eds.): ‘Advances in Neural Information Processing Systems 14’ (MIT Press, Cambridge, MA, 2002), pp. 383–389

