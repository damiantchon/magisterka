import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import cProfile
import pandas as pd
from itertools import chain
import copy

from services.calculate import nearest_neighbors_vrptw, local_search_clean, routes_length, check_feasibility
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
    data = Data("solomon/C201_100")

    vrptw = VRPTW(data, vehicle_capacity=700)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    # print(time_windows)

    macs = MACS_VRPTW(vrptw, tau0=None, m=10, alpha=0.5, beta=1, q0=0.9, p=0.1)

    print(macs.vrptw.distances)

    # nn_solution = macs.run()
    nn_solution = {'length': 591.56, 'vehicles': 3, 'routes': [[0, 93, 5, 75, 2, 1, 99, 100, 97, 92, 94, 95, 98, 7, 3, 4, 89, 91, 88, 84, 86, 83, 82, 85, 76, 71, 70, 73, 80, 79, 81, 78, 77, 96, 87, 90, 0], [0, 67, 63, 62, 74, 72, 61, 64, 66, 69, 68, 65, 49, 55, 54, 53, 56, 58, 60, 59, 57, 40, 44, 46, 45, 51, 50, 52, 47, 43, 42, 41, 48, 0], [0, 20, 22, 24, 27, 30, 29, 6, 32, 33, 31, 35, 37, 38, 39, 36, 34, 28, 26, 23, 18, 19, 16, 14, 12, 15, 17, 13, 25, 9, 11, 10, 8, 21, 0]]}

    # cProfile.run('macs.run()')
    # macs.run()

    # nn_solution = nearest_neighbors_vrptw(vrptw)
    # nn_solution["routes"] = [[0, 1, 6, 3, 4, 0], [0, 5, 2, 7, 8, 0]]
    # nn_solution["length"] = routes_length(vrptw, nn_solution["routes"])
    #
    # print("Doin local search:")
    # first_solution = copy.deepcopy(nn_solution)


    # nn_solution = {'length': 902.43, 'vehicles': 11, 'routes': [[0, 98, 96, 95, 94, 92, 93, 0], [0, 67, 65, 63, 62, 74, 72, 61, 64, 68, 66, 69, 0], [0, 57, 55, 54, 53, 56, 58, 60, 59, 0], [0, 43, 42, 41, 40, 44, 46, 45, 48, 51, 50, 52, 49, 47, 0], [0, 32, 33, 31, 35, 37, 38, 39, 36, 34, 0], [0, 20, 24, 25, 27, 29, 30, 28, 26, 23, 22, 21, 0], [0, 97, 100, 99, 2, 1, 75, 0], [0, 81, 78, 76, 71, 70, 73, 77, 79, 80, 0], [0, 90, 87, 86, 83, 82, 84, 85, 88, 89, 91, 0], [0, 5, 3, 7, 8, 10, 11, 9, 6, 4, 0], [0, 13, 17, 18, 19, 15, 16, 14, 12, 0]]}
    # print(nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print(nn_solution)

    # while [0, 57, 55, 54, 53, 56, 58, 60, 59, 68, 69, 0] not in nn_solution["routes"]:
    #     nn_solution = local_search_clean(vrptw, nn_solution)

    # nn_solution = {'length': 2137.82, 'vehicles': 5, 'routes': [[0, 92, 59, 5, 45, 83, 42, 14, 95, 98, 28, 69, 61, 38, 16, 99, 85, 18, 8, 84, 6, 94, 57, 43, 97, 37, 96, 13, 74, 4, 89, 60, 17, 91, 100, 93, 58, 77, 80, 0], [0, 72, 39, 33, 63, 36, 47, 82, 27, 52, 62, 11, 19, 88, 7, 86, 53, 41, 3, 50, 46, 66, 32, 35, 1, 70, 48, 0], [0, 65, 2, 15, 31, 30, 29, 12, 76, 73, 40, 0], [0, 23, 21, 75, 44, 67, 87, 22, 49, 10, 20, 26, 56, 55, 24, 68, 0], [0, 64, 71, 51, 79, 78, 81, 90, 9, 34, 54, 25, 0]]}
    # print(check_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = {'length': 1648.19, 'vehicles': 20, 'routes': [[0, 33, 81, 50, 68, 0], [0, 92, 42, 15, 87, 57, 97, 13, 0], [0, 65, 71, 9, 66, 1, 0], [0, 45, 82, 18, 84, 60, 89, 0], [0, 62, 11, 90, 10, 0], [0, 72, 75, 22, 74, 58, 0], [0, 53, 26, 0], [0, 28, 29, 78, 34, 35, 77, 0], [0, 31, 88, 7, 0], [0, 12, 76, 79, 3, 54, 24, 80, 0], [0, 2, 21, 73, 41, 56, 4, 0], [0, 27, 69, 30, 51, 20, 32, 70, 0], [0, 39, 23, 67, 55, 25, 0], [0, 52, 99, 6, 0], [0, 14, 44, 38, 43, 91, 100, 0], [0, 40, 94, 96, 0], [0, 59, 5, 83, 61, 85, 37, 93, 0], [0, 63, 64, 49, 48, 0], [0, 36, 47, 19, 8, 46, 0], [0, 95, 98, 16, 86, 17, 0]]}
    # opt = 0
    # notopt = 0
    # while nn_solution["length"] > 828:
    #     nn_solution = macs.run()
    #     if nn_solution["length"] <  829.5:
    #         opt += 1
    #     else:
    #         notopt += 1
    #     print("Optimal:", opt)
    #     print("Not optimal:", notopt)

    add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=200, font_color='r', font_size=8)

    plt.show()
