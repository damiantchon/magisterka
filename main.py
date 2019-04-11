import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


from services.calculate import nearest_neighbors_vrptw
from VRPTW import Data, VRPTW
from ACO import ACOStrategy, MACS_VRPTW


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)


def add_solution_to_graph(graph, solution):

    for route in solution["routes"]:
        for i in range(0, len(route)-1):
            graph.add_edge(route[i], route[i + 1])

    return graph


if __name__ == '__main__':

    data = Data("solomon/C201_100")

    vrptw = VRPTW(data)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    # print(time_windows)

    aco = MACS_VRPTW(vrptw, tau0=0, m=20, alpha=0.5, beta=0.5)

    nn_solution = nearest_neighbors_vrptw(vrptw)

    nn_graph = add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=200, font_color='r', font_size=8, labels=time_windows)

    plt.show()




