\begin{table*}[t]
\caption{Jitter decomposition results at three PJ frequencies (True values: PJ = 15.0 ps, DCD = 1.0 ps, ISI = 0.16 ps, RJ = 2.0 ps)}
\label{tab:decomp}
\centering
\begin{tabular}{llcccccccc}
\hline
& & \multicolumn{2}{c}{PJ (ps)} & \multicolumn{2}{c}{DCD (ps)} & \multicolumn{2}{c}{ISI (ps)} & \multicolumn{2}{c}{RJ (ps)} \\
\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}
$f_\mathrm{PJ}$ & Method & Est. & Error & Est. & Error & Est. & Error & Est. & Error \\
\hline
\multirow{2}{*}{0.1 MHz} & LS-FFT & 15.132 & 0.132 & 0.965 & 0.035 & 0.344 & 0.184 & 2.000 & 0.000 \\
                          & SBL    & 14.987 & 0.013 & 0.943 & 0.057 & 0.340 & 0.180 & 1.995 & 0.005 \\
\multirow{2}{*}{1.0 MHz} & LS-FFT & 16.693 & 1.693 & 0.965 & 0.035 & 0.476 & 0.316 & 2.406 & 0.406 \\
                          & SBL    & 15.166 & 0.166 & 0.942 & 0.058 & 0.340 & 0.180 & 1.994 & 0.006 \\
\multirow{2}{*}{10.0 MHz} & LS-FFT & 12.943 & 2.057 & 0.966 & 0.034 & 0.659 & 0.499 & 4.203 & 2.203 \\
                           & SBL    & 15.130 & 0.130 & 0.943 & 0.057 & 0.340 & 0.180 & 1.994 & 0.006 \\
\hline
\end{tabular}
\end{table*}