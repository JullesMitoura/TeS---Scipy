import matplotlib.pyplot as plt
import pandas as pd

def plot_data(data: pd.DataFrame, P: float, selected_components: list):
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
    plt.title(f"Mols formed - Pressure (bar) = {P}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.grid(True)
    
    # Segundo gráfico: dados normalizados pela soma dos valores selecionados na mesma linha
    plt.subplot(1, 2, 2)  # Segundo gráfico de um layout de 1x2
    sum_selected = filtered_data[selected_components].sum(axis=1)
    normalized_data = filtered_data[selected_components].div(sum_selected, axis=0)
    
    for col in selected_components:
        plt.plot(filtered_data["Temperature (K)"], normalized_data[col], label=col)
    plt.xlabel("Temperature (K)")
    plt.ylabel("% mol")
    plt.title(f"Molar Fraction - Pressure (bar) = {P}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()


def plot_data_temperature(data: pd.DataFrame, P: float, selected_components: list):
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
    plt.title(f"Mols formed - Pressure (bar) = {P}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.grid(True)
    
    # Segundo gráfico: dados normalizados pela soma dos valores selecionados na mesma linha
    plt.subplot(1, 2, 2)  # Segundo gráfico de um layout de 1x2
    sum_selected = filtered_data[selected_components].sum(axis=1)
    normalized_data = filtered_data[selected_components].div(sum_selected, axis=0)
    
    for col in selected_components:
        plt.plot(filtered_data["Temperature (K)"], normalized_data[col], label=col)
    plt.xlabel("Temperature (K)")
    plt.ylabel("% mol")
    plt.title(f"Molar Fraction - Pressure (bar) = {P}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def plot_data_pressure(data: pd.DataFrame, T: float, selected_components: list):
    # Filtrar os dados com base na coluna "Temperature (K)"
    filtered_data = data[data["Temperature (K)"] == T]
    
    # Remover as colunas "Temperature (K)" e "Pressure (bar)" para plotar as demais
    columns_to_plot = [col for col in filtered_data.columns if col not in ["Temperature (K)", "Pressure (bar)"]]

    # Primeiro gráfico: dados como são
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)  # Primeiro gráfico de um layout de 1x2
    for col in columns_to_plot:
        plt.plot(filtered_data["Pressure (bar)"], filtered_data[col], label=col)
    plt.xlabel("Pressure (bar)")
    plt.ylabel("Mols")
    plt.title(f"Mols formed - Temperature (K) = {T}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.grid(True)
    
    # Segundo gráfico: dados normalizados pela soma dos valores selecionados na mesma linha
    plt.subplot(1, 2, 2)  # Segundo gráfico de um layout de 1x2
    sum_selected = filtered_data[selected_components].sum(axis=1)
    normalized_data = filtered_data[selected_components].div(sum_selected, axis=0)
    
    for col in selected_components:
        plt.plot(filtered_data["Pressure (bar)"], normalized_data[col], label=col)
    plt.xlabel("Pressure (bar)")
    plt.ylabel("% mol")
    plt.title(f"Molar Fraction - Temperature (K) = {T}")
    plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
