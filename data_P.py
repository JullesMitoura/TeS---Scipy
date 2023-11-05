import matplotlib.pyplot as plt
import pandas as pd

def plot_data(data: pd.DataFrame, P: float):
    # Filtrar os dados com base na coluna "Pressure (bar)"
    filtered_data = data[data["Pressure (bar)"] == P]
    
    # Remover as colunas "Temperature (K)" e "Pressure (bar)" para plotar as demais
    columns_to_plot = [col for col in filtered_data.columns if col not in ["Temperature (K)", "Pressure (bar)"]]
    
    # Primeiro gráfico: dados como são
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)  # Primeiro gráfico de um layout de 1x2
    for col in columns_to_plot:
        plt.plot(filtered_data["Temperature (K)"], filtered_data[col], label=col)
    plt.xlabel("Temperature (K)")
    plt.ylabel("Mols")
    plt.title(f"Mols formed -  Pressure (bar) = {P}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left", fontsize=8, frameon=False)
    plt.grid(True)
    
    # Segundo gráfico: dados normalizados pela soma dos valores na mesma linha (exceto coluna "C")
    plt.subplot(1, 2, 2)  # Segundo gráfico de um layout de 1x2
    sum_without_C = filtered_data[columns_to_plot].drop(columns="C").sum(axis=1)
    normalized_data = filtered_data[columns_to_plot].div(sum_without_C, axis=0)
    
    # Plotando todas as colunas, exceto "C"
    for col in [c for c in columns_to_plot if c != "C"]:
        plt.plot(filtered_data["Temperature (K)"], normalized_data[col], label=col)
    plt.xlabel("Temperature (K)")
    plt.ylabel("% mol")
    plt.title(f"Molar Fraction - Pressure (bar) = {P}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left", fontsize = 8, frameon=False)
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()