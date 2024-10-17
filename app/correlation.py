import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_correlation_matrix(df):
    # Calculate correlation matrices
    spearman_corr = df.corr(method='spearman')
    pearson_corr = df.corr(method='pearson')

    # Set up the matplotlib figure
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

    # Draw the heatmaps
    sns.heatmap(spearman_corr, ax=axes[0], cmap='coolwarm', annot=True, fmt=".2f", vmin=-1, vmax=1)
    sns.heatmap(pearson_corr, ax=axes[1], cmap='coolwarm', annot=True, fmt=".2f", vmin=-1, vmax=1)

    # Set titles
    axes[0].set_title('Spearman Correlation')
    axes[1].set_title('Pearson Correlation')

    plt.tight_layout()
    plt.show()