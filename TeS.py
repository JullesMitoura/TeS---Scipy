""""

TeS - Thermodynamic Equilibrium Simulation

Este programa de simulação foi desenvolvido por Julles Mitoura, doutorando em Engenharia Química pelo programa de pós-graduacao em
Engenharia Química da Universidade Estadual de Campinas.
O programa calcula as composicoes de equilibrio de um sistema reacional utilizando a metodologia da minimização da energia de Gibbs
do sistema. Para o calculo dos coeficientes de fugacidade, inicialmente podem ser utilizadas as seguintes equações de estado:
    - ideal (phi = 1)
    - peng_robinson
    - redlich_kwong
    - van_der_waals
    - soave_redlich_kwong
    
A versao 1.0 do projeto TeS considera a formacao de componentes em fase de vapor e carbono solido (somente). O componente solido 
considerado é escrito como ideal.

Como padrão, o polinômio utilizado para o cálculo das capacidades caloríficas em ambas as fases é o seguinte:

Cp/R = a + B.T + c.T^2 + d.T^-2

Os coeficientes podem ser verificados no livro "Introdução à Termodinâmica da Engenharia Química", ecrito por Abbott, Van Ness e 
Smith.

"""
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout, QFrame, QTextEdit, QDialog, QTableWidget, QTableWidgetItem, QFileDialog, QVBoxLayout, QComboBox, QHeaderView
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from gibbs import GIBBS
from surface import plot_superficie
from linear_graph import line_graf
from correlation import plot_correlation_matrix
from data_P import plot_data
import os
import sys
import subprocess

class LogoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gibbs_results = None
        self.initUI()
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)


    def initUI(self):
        # Configurar a janela principal
        self.setWindowTitle('TeS')
        self.setFixedSize(800, 750)  # Tamanho fixo da janela

        # Definir o fundo como branco
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)

        # Criar um widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout vertical para organizar elementos
        main_layout = QVBoxLayout(central_widget)

        # Layout de grade para organizar elementos em uma matriz 6x20
        layout = QGridLayout()
        main_layout.addLayout(layout)

        # Adicionar o logotipo nas células das linhas 1 e 2 e ocupar 6 colunas
        logo_label = QLabel(self)
        pixmap = QPixmap('imgs/logo_TeS.jpg')  # Substitua pelo caminho da sua imagem de logotipo
        pixmap = pixmap.scaled(1000, 85,Qt.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label, 0, 0, 2, 6)  # Alinhar ao topo e ocupar 6 colunas nas linhas 1 e 2

        # Adicionar uma linha preta (QFrame) marcando a segunda linha
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: grey;")
        layout.addWidget(line, 2, 0, 1, 6)  # Adicionar a linha na segunda linha da matriz

        # Adicionar botões nas células da linha 3 e 4, ocupando a coluna 1
        button1 = QPushButton('Importar dados', self)
        button1.clicked.connect(self.importData)
        layout.addWidget(button1, 3, 0)
        
        button2 = QPushButton('Informações', self)
        button2.clicked.connect(self.showReadmeDialog)
        layout.addWidget(button2, 4, 0)

        # Adicionar rótulos para as comboboxes na coluna 4
        equation_label = QLabel('Equação de estado:')
        layout.addWidget(equation_label, 9, 3)

        inhibit_label = QLabel('Inibir componente:')
        layout.addWidget(inhibit_label, 10, 3)

        # Criar comboboxes para "Equação de estado" (um valor) e "Inibir componente" (múltiplos valores) na coluna 4
        self.equation_combobox = QComboBox(self)
        self.equation_combobox.setEnabled(False)  # Desabilitado até a importação da tabela
        self.equation_combobox.addItems(["ideal", "peng_robinson", "redlich_kwong",
                                         "van_der_waals", "soave_redlich_kwong"])
        layout.addWidget(self.equation_combobox, 9, 4)

        self.inhibit_combobox = QComboBox(self)
        self.inhibit_combobox.setEnabled(False)  # Desabilitado até a importação da tabela
        layout.addWidget(self.inhibit_combobox, 10, 4)

        # Criar uma tabela para mostrar os dados do CSV (colunas 2 e 3)
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(2)  # Duas colunas: "Component" e "Initial"
        self.tableWidget.setHorizontalHeaderLabels(["Component", "Initial (mols)"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Tamanho fixo para as colunas
        layout.addWidget(self.tableWidget, 3, 1, 3, 3)  # Exibir a tabela nas colunas 2 e 3

        image_label = QLabel(self)
        pixmap = QtGui.QPixmap('imgs/minG.png')  # Carrega a imagem
        scaled_pixmap = pixmap.scaled(200, 124, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Ajusta o tamanho da imagem
        image_label.setPixmap(scaled_pixmap)  # Define a imagem ajustada no QLabel
        layout.addWidget(image_label, 3, 4, 3, 1)


        sim = QPushButton('Simular', self) # Define a cor de fundo, o tamanho da fonte e o padding
        sim.clicked.connect(self.runSimulation)
        layout.addWidget(sim, 5, 0, 1, 1)  # Adiciona o botão ao layout para que ele ocupe duas linhas


        # Adicionar uma linha preta (QFrame) marcando a segunda linha
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: grey;")
        layout.addWidget(line, 6, 0, 1, 6)

        # Adicionar rótulo e campo de entrada para "Temperatura Mínima (K):" na linha 7
        temp_min_label = QLabel('Temperatura Mínima (K):', self)
        layout.addWidget(temp_min_label, 7, 0)
        self.temp_min_input = QLineEdit(self)
        layout.addWidget(self.temp_min_input, 7, 1)

        # Adicionar rótulo e campo de entrada para "Temperatura Máxima (K):" na linha 6
        temp_max_label = QLabel('Temperatura Máxima (K):', self)
        layout.addWidget(temp_max_label, 8, 0)
        self.temp_max_input = QLineEdit(self)
        layout.addWidget(self.temp_max_input, 8, 1)

         # Adicionar rótulo e campo de entrada para "Temperatura Máxima (K):" na linha 6
        p_minlabel = QLabel('Pressão Mínima (bar):', self)
        layout.addWidget(p_minlabel, 9, 0)
        self.pmin_input = QLineEdit(self)
        layout.addWidget(self.pmin_input, 9, 1)       


        # Adicionar rótulo e campo de entrada para "Temperatura Máxima (K):" na linha 6
        p_max_label = QLabel('Pressão Máxima (bar):', self)
        layout.addWidget(p_max_label, 10, 0)
        self.pmax_input = QLineEdit(self)
        layout.addWidget(self.pmax_input, 10, 1)
        
        # Adicionar rótulo e campo de entrada para "Temperatura Máxima (K):" na linha 6
        nsim_t = QLabel('Nº Simulações (T):', self)
        layout.addWidget(nsim_t, 7, 3)
        self.nsimt_input = QLineEdit(self)
        layout.addWidget(self.nsimt_input, 7, 4)

        # Adicionar rótulo e campo de entrada para "Temperatura Máxima (K):" na linha 6
        nsim_p = QLabel('Nº Simulações (P):', self)
        layout.addWidget(nsim_p, 8, 3)
        self.nsimp_input = QLineEdit(self)
        layout.addWidget(self.nsimp_input, 8, 4)

        # Adicionar uma linha preta (QFrame) marcando a segunda linha
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: grey;")
        layout.addWidget(line, 11, 0, 1, 6)

        simulation_results_label = QLabel('Resultados das simulações:', self)
        layout.addWidget(simulation_results_label, 12, 0, 1, 6)

        self.component_selection_label = QLabel('Selecione um componente:', self)
        layout.addWidget(self.component_selection_label, 13, 0, 1, 3)  # Adicionando na linha 12

        self.component_combobox = QComboBox(self)
        self.component_combobox.setEnabled(False)  # Começará desabilitado até que o arquivo seja carregado
        layout.addWidget(self.component_combobox, 13, 1, 1, 1)

        self.response_surface_btn = QPushButton('Superfície de resposta', self)
        layout.addWidget(self.response_surface_btn, 14, 0)
        self.response_surface_btn.clicked.connect(self.plotResponseSurface)

        self.line_graf = QPushButton('Gráfico de linhas', self)
        self.line_graf.clicked.connect(self.plotLineGraph)
        layout.addWidget(self.line_graf, 14, 1)

        self.matriz_coorel = QPushButton('Matriz de correlação', self)
        self.matriz_coorel.clicked.connect(self.plotCorrelationMatrix)
        layout.addWidget(self.matriz_coorel, 15, 0)

        self.pressure_label = QLabel('Selecione um valor de pressão:', self)
        layout.addWidget(self.pressure_label, 13, 2, 1, 2)  # Adicionando na linha 14

        self.pressure_combobox = QComboBox(self)
        self.pressure_combobox.setEnabled(False)  # Começará desabilitado até que a simulação seja executada
        layout.addWidget(self.pressure_combobox, 13, 4, 1, 1)

        # Adicionar o botão "Gráfico de linhas (Pressão fixa)" abaixo da combobox de pressão
        self.fixed_pressure_graph_btn = QPushButton('Composições no equilibrio (mols, % molar)', self)
        layout.addWidget(self.fixed_pressure_graph_btn, 14, 3, 1, 3)
        self.fixed_pressure_graph_btn.clicked.connect(self.plotEquilibriumData)


        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: grey;")
        layout.addWidget(line, 17, 0, 1, 6)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: grey;")
        layout.addWidget(line, 17, 0, 1, 6)

        # Adicionar um rótulo para a tabela de resultados máximos
        max_values_label = QLabel('Valores máximos por componente e respectivas condições:', self)
        layout.addWidget(max_values_label, 18, 0, 1, 6)

        # Criar a tabela para mostrar os valores máximos
        self.maxValuesTable = QTableWidget()
        self.maxValuesTable.setColumnCount(4)  # Quatro colunas: "Componente", "Valor máximo", "Temperatura (K)", "Pressão (bar)"
        self.maxValuesTable.setHorizontalHeaderLabels(["Componente", "Valor máximo", "Temperatura (K)", "Pressão (bar)"])
        self.maxValuesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Ajustar o tamanho das colunas
        layout.addWidget(self.maxValuesTable, 20, 0, 1, 6)

        # Adicionando o botão para salvar os dados simulados
        self.saveDataButton = QPushButton('Salvar dados simulados', self)
        layout.addWidget(self.saveDataButton, 21,0, 1, 6)  # Adicionando o botão na linha 18, ocupando 6 colunas
        self.saveDataButton.clicked.connect(self.saveSimulatedData)

        self.component_selection_label.setEnabled(False)
        self.component_combobox.setEnabled(False)
        self.pressure_label.setEnabled(False)
        self.pressure_combobox.setEnabled(False)
        self.response_surface_btn.setEnabled(False)
        self.line_graf.setEnabled(False)
        self.matriz_coorel.setEnabled(False)
        self.fixed_pressure_graph_btn.setEnabled(False)
        self.maxValuesTable.setEnabled(False)
        self.saveDataButton.setEnabled(False)

    def importData(self):
        # Abrir o diálogo de seleção de arquivo e permitir que o usuário escolha um arquivo CSV
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.filePath, _ = QFileDialog.getOpenFileName(self, "Selecione um arquivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if self.filePath:
            # Utilizar o Pandas para ler o arquivo CSV selecionado e selecionar as colunas "Component" e "Initial"
            data = pd.read_csv(self.filePath, usecols=["Component", "initial"])
            components = data["Component"].unique()
            self.component_combobox.clear()
            self.component_combobox.addItems(components)
            self.component_combobox.setEnabled(True)
            
            # Preencher a tabela com os dados
            self.tableWidget.setRowCount(len(data))
            for row_idx, row_data in data.iterrows():
                item1 = QTableWidgetItem(row_data["Component"])
                item2 = QTableWidgetItem(str(row_data["initial"]))  # Converter para string
                self.tableWidget.setItem(row_idx, 0, item1)
                self.tableWidget.setItem(row_idx, 1, item2)

            # Preencher a combobox do botão "Inibir componente" com os valores da coluna "Component"
            components = data["Component"].unique()
            self.inhibit_combobox.clear()
            self.inhibit_combobox.addItem("Não inibir")
            self.inhibit_combobox.addItems(components)

            # Habilitar as comboboxes
            self.equation_combobox.setEnabled(True)
            self.inhibit_combobox.setEnabled(True)

    def showReadmeDialog(self):
        filename = "TeS.pdf"
        if os.path.isfile(filename):
            os.startfile(filename)
        else:
            print(f"O arquivo {filename} não foi encontrado.")

    def runSimulation(self):
        """Executa a simulação usando a função GIBBS."""

        Pmin_text = self.pmin_input.text().strip()
        Pmax_text = self.pmax_input.text().strip()
        Tmin_text = self.temp_min_input.text().strip()
        Tmax_text = self.temp_max_input.text().strip()
        ntemp_text = self.nsimt_input.text().strip()
        npressure_text = self.nsimp_input.text().strip()

        # Verificar se todos os campos necessários estão preenchidos
        if not Pmin_text or not Pmax_text or not Tmin_text or not Tmax_text or not ntemp_text or not npressure_text:
            QMessageBox.warning(self, "Atenção", "Revise as informações para seguir com a simulação!")
            return
    
        # Obter os valores dos widgets
        Pmin = float(self.pmin_input.text())
        Pmax = float(self.pmax_input.text())
        Tmin = float(self.temp_min_input.text())
        Tmax = float(self.temp_max_input.text())
        eq = self.equation_combobox.currentText()
        ntemp = int(self.nsimt_input.text())  # Número de pontos de temperatura
        npressure = int(self.nsimp_input.text())  # Número de pontos de pressão

        inhibited_component = self.inhibit_combobox.currentText()
        if inhibited_component == "Não inibir":
            inhibited_component = None
  

        progress_dialog = QProgressDialog("Simulando...", None, 0, 0, self)
        progress_dialog.setAutoClose(True)
        progress_dialog.setCancelButton(None)  # Sem botão de cancelar
        progress_dialog.show()

        QApplication.processEvents()

        # Executar a função GIBBS
        # Suponho que a variável `filePath` seja uma variável de instância
        # Se não for, você precisará ajustar para obter o caminho do arquivo corretamente
        self.gibbs_results = GIBBS(self.filePath, Pmin, Pmax, Tmin, Tmax, eq, npressure, ntemp, inhibited_component)

        progress_dialog.close()

        unique_pressures = self.gibbs_results['Pressure (bar)'].unique()
        self.pressure_combobox.clear()
        self.pressure_combobox.addItems([str(pressure) for pressure in sorted(unique_pressures)])
        self.pressure_combobox.setEnabled(True)
        self.updateMaxValuesTable()

        self.component_selection_label.setEnabled(True)
        self.component_combobox.setEnabled(True)
        self.pressure_label.setEnabled(True)
        self.pressure_combobox.setEnabled(True)
        self.response_surface_btn.setEnabled(True)
        self.line_graf.setEnabled(True)
        self.matriz_coorel.setEnabled(True)
        self.fixed_pressure_graph_btn.setEnabled(True)
        self.maxValuesTable.setEnabled(True)
        self.saveDataButton.setEnabled(True)

    def plotResponseSurface(self):
        """Chama a função plot_superficie com os resultados de Gibbs se o número de simulações for adequado."""
        # Assuming self.nsim_t and self.nsim_p are the numeric values for the number of simulations
        if int(self.nsimp_input.text().strip()) < 5 or int(self.nsimt_input.text().strip()) < 5:
            # Mostrar a mensagem de erro para o usuário
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setText("Com a quantidade de pontos que você selecionou não é possível plotar uma superfície de resposta!")
            error_msg.setWindowTitle("Erro")
            error_msg.exec_()
        elif self.gibbs_results is not None:
            x = self.gibbs_results['Temperature (K)']
            y = self.gibbs_results['Pressure (bar)']
            selected_component = self.component_combobox.currentText()
            z = self.gibbs_results[selected_component]
            plot_superficie(x, y, z, selected_component)
        else:
            # Mostrar uma mensagem de erro caso a simulação ainda não tenha sido executada
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setText("Por favor, execute a simulação primeiro!")
            error_msg.setWindowTitle("Erro")
            error_msg.exec_()

    def plotFixedPressureGraph(self):
            """Função para plotar o gráfico de linhas com uma pressão fixa."""
            pass
    
    def updateMaxValuesTable(self):
        if self.gibbs_results is not None:
            # Remover as colunas 'Temperature (K)' e 'Pressure (bar)' dos componentes a serem considerados
            components = [col for col in self.gibbs_results.columns if col not in ['Temperature (K)', 'Pressure (bar)']]
            self.maxValuesTable.setRowCount(len(components))
            for idx, component in enumerate(components):
                max_value = self.gibbs_results[component].max()
                temp_at_max = self.gibbs_results[self.gibbs_results[component] == max_value]['Temperature (K)'].values[0]
                pressure_at_max = self.gibbs_results[self.gibbs_results[component] == max_value]['Pressure (bar)'].values[0]
                
                # Arredondar os valores para duas casas decimais
                max_value_str = "{:.2f}".format(max_value)
                temp_at_max_str = "{:.2f}".format(temp_at_max)
                pressure_at_max_str = "{:.2f}".format(pressure_at_max)

                self.maxValuesTable.setItem(idx, 0, QTableWidgetItem(component))
                self.maxValuesTable.setItem(idx, 1, QTableWidgetItem(max_value_str))
                self.maxValuesTable.setItem(idx, 2, QTableWidgetItem(temp_at_max_str))
                self.maxValuesTable.setItem(idx, 3, QTableWidgetItem(pressure_at_max_str))
                self.saveDataButton.setText(f'Salvar dados simulados')

    def saveSimulatedData(self):
        if self.gibbs_results is not None:
            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getSaveFileName(self, "Salvar dados simulados", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if filePath:
                # Se o usuário não fornecer a extensão .csv, vamos adicioná-la
                if not filePath.endswith('.csv'):
                    filePath += '.csv'
                self.gibbs_results.to_csv(filePath, index=False)
                QMessageBox.information(self, "Sucesso", "Dados simulados salvos com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def plotCorrelationMatrix(self):

        if int(self.nsimp_input.text().strip()) < 5 or int(self.nsimt_input.text().strip()) < 5:
            # Mostrar a mensagem de erro para o usuário
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setText("Simule mais pontos para verificar as correlações!")
            error_msg.setWindowTitle("Erro")
            error_msg.exec_()

        elif self.gibbs_results is not None:
            plot_correlation_matrix(self.gibbs_results)
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def plotLineGraph(self):
        if self.gibbs_results is not None:
            line_graf(self.gibbs_results,self.component_combobox.currentText())
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def plotEquilibriumData(self):
        if self.gibbs_results is not None:
            selected_pressure = float(self.pressure_combobox.currentText())  # Obtém o valor de pressão selecionado
            plot_data(self.gibbs_results, selected_pressure)
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")


def main():
    app = QApplication(sys.argv)

    # Define a fonte global para toda a aplicação
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)

    ex = LogoApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()