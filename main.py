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


    # lolwut?
    # {'length': 826.75, 'vehicles': 10,
    #  'routes': [[0, 20, 24, 25, 27, 29, 30, 28, 26, 23, 22, 21, 0], [0, 90, 87, 86, 83, 82, 84, 85, 88, 89, 91, 0],
    #             [0, 13, 17, 18, 19, 15, 16, 14, 12, 0], [0, 98, 96, 95, 94, 92, 93, 97, 100, 99, 0],
    #             [0, 43, 42, 41, 40, 44, 46, 45, 48, 51, 50, 52, 49, 47, 0], [0, 32, 33, 31, 35, 37, 38, 39, 36, 34, 0],
    #             [0, 5, 3, 7, 8, 10, 11, 9, 6, 4, 2, 1, 75, 0], [0, 81, 78, 76, 71, 70, 73, 77, 79, 80, 0],
    #             [0, 67, 65, 63, 62, 74, 72, 61, 64, 66, 0], [0, 57, 55, 54, 53, 56, 58, 60, 59, 68, 69, 0]]}

    # nn_solution = {'length': 902.43, 'vehicles': 11, 'routes': [[0, 98, 96, 95, 94, 92, 93, 0], [0, 67, 65, 63, 62, 74, 72, 61, 64, 68, 66, 69, 0], [0, 57, 55, 54, 53, 56, 58, 60, 59, 0], [0, 43, 42, 41, 40, 44, 46, 45, 48, 51, 50, 52, 49, 47, 0], [0, 32, 33, 31, 35, 37, 38, 39, 36, 34, 0], [0, 20, 24, 25, 27, 29, 30, 28, 26, 23, 22, 21, 0], [0, 97, 100, 99, 2, 1, 75, 0], [0, 81, 78, 76, 71, 70, 73, 77, 79, 80, 0], [0, 90, 87, 86, 83, 82, 84, 85, 88, 89, 91, 0], [0, 5, 3, 7, 8, 10, 11, 9, 6, 4, 0], [0, 13, 17, 18, 19, 15, 16, 14, 12, 0]]}
    # print(nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print(nn_solution)

    # while [0, 57, 55, 54, 53, 56, 58, 60, 59, 68, 69, 0] not in nn_solution["routes"]:
    #     nn_solution = local_search_clean(vrptw, nn_solution)



    nn_solution = macs.run()
    opt = 0
    notopt = 0
    while nn_solution["length"] > 828:
        nn_solution = macs.run()
        if nn_solution["length"] <  829.5:
            opt += 1
        else:
            notopt += 1
        print("Optimal:", opt)
        print("Not optimal:", notopt)

    add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=200, font_color='r', font_size=8)

    plt.show()
