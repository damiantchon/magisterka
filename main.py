import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from itertools import chain
import copy

from services.calculate import nearest_neighbors_vrptw, local_search, local_search_clean, routes_length
from VRPTW import Data, VRPTW
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

    data = Data("solomon/R101_100")

    vrptw = VRPTW(data, vehicle_capacity=200)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    # print(time_windows)

    macs = MACS_VRPTW(vrptw, tau0=None, m=20, alpha=0.5, beta=0.5)

    nn_solution = nearest_neighbors_vrptw(vrptw)

    # nn_solution["routes"] = [[0, 1, 6, 3, 4, 0], [0, 5, 2, 7, 8, 0]]
    # nn_solution["length"] = routes_length(vrptw, nn_solution["routes"])

    print("Doin local search:")

    length = len(nn_solution["routes"])

    total = 0
    better = 0

    first_solution = copy.deepcopy(nn_solution)
    #
    # for i in range(0, length-1):
    #     for j in range(i + 1, length):
    #         if nn_solution["routes"][i] is not [0, 0] and nn_solution["routes"][j] is not [0, 0]:
    #             total, better, first_best, second_best = local_search(vrptw, first_route=nn_solution["routes"][i], second_route=nn_solution["routes"][j], total=total, better=better)
    #             nn_solution["routes"][i] = first_best
    #             nn_solution["routes"][j] = second_best
    #
    #
    # nn_solution["routes"] = list(filter(([0, 0]).__ne__, nn_solution["routes"]))
    #
    # nn_solution["vehicles"] = len(nn_solution["routes"])
    # nn_solution["length"] = routes_length(vrptw, nn_solution["routes"])

    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)
    nn_solution = local_search_clean(vrptw, nn_solution)
    print(nn_solution)

    print(first_solution)
    print(nn_solution)

    print("Total:", total)
    print("Better", better)

    add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=200, font_color='r', font_size=8)

    plt.show()

    # macs = MACS_VRPTW(vrptw, 1, 1, 1, None)




