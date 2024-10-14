""""

TeS - Thermodynamic Equilibrium Simulation

Este programa de simulação foi desenvolvido por Julles Mitoura, doutorando em Engenharia Química pelo programa de pós-graduacao em
Engenharia Química da Universidade Estadual de Campinas.
O programa calcula as composicoes de equilibrio de um sistema reacional utilizando a metodologia da minimização da energia de Gibbs
do sistema. Para o calculo dos coeficientes de fugacidade, inicialmente podem ser utilizadas as seguintes equações de estado:
    - ideal (phi = 1)
    - peng_robinson
    - redlich_kwong
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
from custom_widgets import CheckableComboBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from gibbs import GIBBS
from surface import plot_superficie
from linear_graph import line_graf, line_graf_T
from correlation import plot_correlation_matrix
from data_P import plot_data_temperature, plot_data_pressure
import os
import sys
import subprocess
import platform


class LogoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gibbs_results = None
        self.selectedComponents = []
        self.initUI()
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)


    def initUI(self):
        # Configurar a janela principal
        self.setWindowTitle('TeS')
        self.setFixedSize(800, 760)  # Tamanho fixo da janela

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
        pixmap = pixmap.scaled(750, 70) 
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
        self.equation_combobox.addItems(["ideal", "peng_robinson", "redlich_kwong", "soave_redlich_kwong"])
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

        self.line_graf = QPushButton('Gráfico de linhas - P', self)
        self.line_graf.clicked.connect(self.plotLineGraph)
        layout.addWidget(self.line_graf, 14, 1)

        self.line_graf_T = QPushButton('Gráfico de linhas - T', self)
        self.line_graf_T.clicked.connect(self.plotLineGraph2)
        layout.addWidget(self.line_graf_T, 15, 1)

        self.matriz_coorel = QPushButton('Matriz de correlação', self)
        self.matriz_coorel.clicked.connect(self.plotCorrelationMatrix)
        layout.addWidget(self.matriz_coorel, 15, 0)

        self.components_label = QLabel('Componentes para % molar:', self)
        layout.addWidget(self.components_label, 13, 2, 1, 2) 

        self.components_combobox = CheckableComboBox(self)
        self.components_combobox.view().pressed.connect(self.updateSelectedComponents)
        layout.addWidget(self.components_combobox, 13, 4, 1, 1)

        self.pressure_label = QLabel('Pressão:', self)
        layout.addWidget(self.pressure_label, 14, 2, 1, 1)  # Adicionando na linha 14

        self.temp_label = QLabel('Temperatura:', self)
        layout.addWidget(self.temp_label, 15, 2, 1, 1)  # Adicionando na linha 14

        self.temp_combobox = QComboBox(self)
        self.temp_combobox.setEnabled(False)  # Começará desabilitado até que a simulação seja executada
        layout.addWidget(self.temp_combobox, 15, 3, 1, 1)

        self.pressure_combobox = QComboBox(self)
        self.pressure_combobox.setEnabled(False)  # Começará desabilitado até que a simulação seja executada
        layout.addWidget(self.pressure_combobox, 14, 3, 1, 1)

        # Adicionar o botão "Gráfico de linhas (Pressão fixa)" abaixo da combobox de pressão
        self.fixed_pressure_graph_btn = QPushButton('mols e % molar - P = cte', self)
        layout.addWidget(self.fixed_pressure_graph_btn, 14, 4, 1, 1)
        self.fixed_pressure_graph_btn.clicked.connect(self.plotEquilibriumData)

        # Adicionar o botão "Gráfico de linhas (Pressão fixa)" abaixo da combobox de pressão
        self.fixed_temperature_graph_btn = QPushButton('mols e % molar - T = cte', self)
        layout.addWidget(self.fixed_temperature_graph_btn, 15, 4, 1, 1)
        self.fixed_temperature_graph_btn.clicked.connect(self.plotEquilibriumData2)


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
        layout.addWidget(self.saveDataButton, 21,0, 1, 6)
        self.saveDataButton.clicked.connect(self.saveSimulatedData)

        self.component_selection_label.setEnabled(False)
        self.component_combobox.setEnabled(False)
        self.pressure_label.setEnabled(False)
        self.pressure_combobox.setEnabled(False)
        self.response_surface_btn.setEnabled(False)
        self.line_graf.setEnabled(False)
        self.line_graf_T.setEnabled(False)
        self.matriz_coorel.setEnabled(False)
        self.fixed_pressure_graph_btn.setEnabled(False)
        self.fixed_temperature_graph_btn.setEnabled(False)
        self.maxValuesTable.setEnabled(False)
        self.saveDataButton.setEnabled(False)
        self.components_label.setEnabled(False)
        self.components_combobox.setEnabled(False)
        self.temp_label.setEnabled(False)
        self.temp_combobox.setEnabled(False)

    def importData(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.filePath, _ = QFileDialog.getOpenFileName(self, "Selecione um arquivo CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if self.filePath:
            data = pd.read_csv(self.filePath, usecols=["Component", "initial"])
            components = data["Component"].unique()
            self.component_combobox.clear()
            self.component_combobox.addItems(components)
            self.component_combobox.setEnabled(True)
            for component in components:
                self.components_combobox.addItem(component)
            

            self.tableWidget.setRowCount(len(data))
            for row_idx, row_data in data.iterrows():
                item1 = QTableWidgetItem(row_data["Component"])
                item2 = QTableWidgetItem(str(row_data["initial"]))  # Converter para string
                self.tableWidget.setItem(row_idx, 0, item1)
                self.tableWidget.setItem(row_idx, 1, item2)

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
            if platform.system() == "Windows":
                os.startfile(filename)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", filename])
            else:  # Linux
                subprocess.call(["xdg-open", filename])
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


        if not Pmin_text or not Pmax_text or not Tmin_text or not Tmax_text or not ntemp_text or not npressure_text:
            QMessageBox.warning(self, "Atenção", "Revise as informações para seguir com a simulação!")
            return
    

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
        progress_dialog.setCancelButton(None) 
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

        unique_temp = self.gibbs_results['Temperature (K)'].unique()
        self.temp_combobox.clear()
        self.temp_combobox.addItems([str(temp) for temp in sorted(unique_temp)])
        self.temp_combobox.setEnabled(True)

        self.updateMaxValuesTable()

        self.component_selection_label.setEnabled(True)
        self.component_combobox.setEnabled(True)
        self.pressure_label.setEnabled(True)
        self.pressure_combobox.setEnabled(True)
        self.response_surface_btn.setEnabled(True)
        self.line_graf.setEnabled(True)
        self.line_graf_T.setEnabled(True)
        self.matriz_coorel.setEnabled(True)
        self.fixed_pressure_graph_btn.setEnabled(True)
        self.fixed_temperature_graph_btn.setEnabled(True)
        self.maxValuesTable.setEnabled(True)
        self.saveDataButton.setEnabled(True)
        self.components_label.setEnabled(True)
        self.components_combobox.setEnabled(True)
        self.temp_label.setEnabled(True)
        self.temp_combobox.setEnabled(True)

    def plotResponseSurface(self):
        """Chama a função plot_superficie com os resultados de Gibbs se o número de simulações for adequado."""
        if int(self.nsimp_input.text().strip()) < 5 or int(self.nsimt_input.text().strip()) < 5:

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
            components = [col for col in self.gibbs_results.columns if col not in ['Temperature (K)', 'Pressure (bar)']]
            self.maxValuesTable.setRowCount(len(components))
            for idx, component in enumerate(components):
                max_value = self.gibbs_results[component].max()
                temp_at_max = self.gibbs_results[self.gibbs_results[component] == max_value]['Temperature (K)'].values[0]
                pressure_at_max = self.gibbs_results[self.gibbs_results[component] == max_value]['Pressure (bar)'].values[0]
                
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
                if not filePath.endswith('.csv'):
                    filePath += '.csv'
                self.gibbs_results.to_csv(filePath, index=False)
                QMessageBox.information(self, "Sucesso", "Dados simulados salvos com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def plotCorrelationMatrix(self):

        if int(self.nsimp_input.text().strip()) < 5 or int(self.nsimt_input.text().strip()) < 5:
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

    def plotLineGraph2(self):
        if self.gibbs_results is not None:
            line_graf_T(self.gibbs_results,self.component_combobox.currentText())
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def plotEquilibriumData(self):
        if self.gibbs_results is not None:
            selected_pressure = float(self.pressure_combobox.currentText())  # Obtém o valor de pressão selecionado
            plot_data_temperature(self.gibbs_results, selected_pressure,self.selectedComponents)
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def plotEquilibriumData2(self):
        if self.gibbs_results is not None:
            selected_temp = float(self.temp_combobox.currentText())  # Obtém o valor de pressão selecionado
            plot_data_pressure(self.gibbs_results, selected_temp,self.selectedComponents)
        else:
            QMessageBox.warning(self, "Erro", "Por favor, execute a simulação primeiro!")

    def updateSelectedComponents(self, index):
        item = self.components_combobox.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            if item.text() not in self.selectedComponents:
                self.selectedComponents.append(item.text())
        else:
            if item.text() in self.selectedComponents:
                self.selectedComponents.remove(item.text())


def main():
    app = QApplication(sys.argv)

    font = QFont()
    font.setPointSize(10)
    app.setFont(font)

    ex = LogoApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()