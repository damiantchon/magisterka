import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import cProfile
import pandas as pd
from itertools import chain
import copy

from services.calculate import nearest_neighbors_vrptw, local_search_clean, routes_length
from VRPTW import Data, VRPTW, VRPTW_MACS_DS
from ACO import MACS_VRPTW


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)



def add_solution_to_graph(graph, solution):

    for route in solution["routes"]:
        for i in range(0, len(route)-1):
            graph.add_edge(route[i], route[i + 1])

    return graph


if __name__ == '__main__':

    # data = Data("solomon/local_search_test")
    data = Data("solomon/C101_100")

    vrptw = VRPTW(data, vehicle_capacity=200)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    # print(time_windows)

    macs = MACS_VRPTW(vrptw, tau0=None, m=20, alpha=0.5, beta=1, q0=0.7, p=0.1)

    print(macs.vrptw.distances)


    # cProfile.run('macs.run()')
    # macs.run()

    # nn_solution = nearest_neighbors_vrptw(vrptw)
    # nn_solution["routes"] = [[0, 1, 6, 3, 4, 0], [0, 5, 2, 7, 8, 0]]
    # nn_solution["length"] = routes_length(vrptw, nn_solution["routes"])
    #
    # print("Doin local search:")
    # first_solution = copy.deepcopy(nn_solution)



    nn_solution = macs.run()

    add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=200, font_color='r', font_size=8)

    plt.show()
