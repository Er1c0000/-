import matplotlib.pyplot as plt
import seaborn as sns

def setup_plot_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = ["Arial", "Times New Roman"]
    plt.rcParams["axes.unicode_minus"] = False
