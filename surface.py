import matplotlib.pyplot as plt
import numpy as np


def plot_superficie(x, y, z, title):

    x_array = np.array(x)
    y_array = np.array(y)
    z_array = np.array(z)

    x_grid, y_grid = np.meshgrid(np.unique(x_array), np.unique(y_array))
    z_grid = z_array.reshape(len(np.unique(y_array)), len(np.unique(x_array)))

    fig = plt.figure(figsize=(10, 4)) # ajuste o tamanho conforme necessário


    ax1 = fig.add_subplot(121, projection='3d') # 121 significa 1 linha, 2 colunas, 1º gráfico
    surf = ax1.plot_surface(x_grid, y_grid, z_grid, cmap='coolwarm', edgecolor='none')
    ax1.set_xlabel('Temperature (K)', labelpad=10, fontsize=9, style='italic')
    ax1.set_ylabel('Pressure (bar)', labelpad=10, fontsize=9, style='italic')
    cbar1 = fig.colorbar(surf, ax=ax1, pad=0.1)
    cbar1.ax.set_title(label=f'{title} (mols)', pad=5, fontweight='bold')

    ax2 = fig.add_subplot(122) # 122 significa 1 linha, 2 colunas, 2º gráfico
    c = ax2.contourf(x_grid, y_grid, z_grid, cmap='coolwarm', levels=50)
    ax2.set_xlabel('Temperature (K)', labelpad=10, fontsize=9, style='italic')
    ax2.set_ylabel('Pressure (bar)', labelpad=10, fontsize=9, style='italic')
    cbar2 = fig.colorbar(c, ax=ax2, pad=0.1)
    cbar2.ax.set_title(label=f'{title} (mols)', pad=10, fontweight='bold')

    plt.tight_layout()
    plt.show()