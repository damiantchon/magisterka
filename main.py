import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from VRPTW import Data, VRPTW

from services.file_operations import clean_input_file, get_data_model

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout

from PyQt5 import QtGui

desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)


# class Window(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.title = "PyQt5 Window"
#
#         self.top = 100
#         self.left = 100
#         self.width = 800
#         self.height = 600
#
#         self.data = []
#         # DATA
#
#
#
#         self.InitWindow()
#
#     def InitWindow(self):
#         self.setWindowIcon(QtGui.QIcon("resources/icon.png"))
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#
#         self.create_form_group_layout()
#
#         self.main_layout = QHBoxLayout()
#         self.main_layout.addWidget(self.group_box)
#         self.create_layout()
#
#         self.show()
#
#     def UiComponents(self):
#         data_button = QPushButton("Ładuj dane", self)
#         data_button.setToolTip("Ładowanie danych modelu VRPTW")
#         data_button.clicked.connect(self.data_button_clicked)
#
#     def create_form_group_layout(self):
#         self.group_box = QGroupBox("Dane")
#         form_layout = QFormLayout()
#         form_layout.addWidget()
#
#     def data_button_clicked(self):
#         # TODO Convert and Load data
#         pass


if __name__ == '__main__':

    data = Data("coordinates.txt")

    print(data.get_node_data(26))

    vrptw = VRPTW(data)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')

    print(demands)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.ged_depo_ids(), with_labels=True, node_color='r', node_size=300, font_color='k', font_size=8, labels=demands)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k', node_size=200, font_color='w', font_size=8, labels=demands)

    plt.show()
