import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import cProfile
import pandas as pd
from itertools import chain
import copy

from services.calculate import nearest_neighbors_vrptw, local_search_clean, routes_length, check_feasibility, create_auxiliary_table, check_solution_feasibility
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

    data = Data("solomon/RC2/RC201_100")
    # data = Data("solomon/local_search_test")
    # data = Data("solomon/auxiliary_dict_test")

    vrptw = VRPTW(data, vehicle_capacity=1000)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    macs = MACS_VRPTW(vrptw, tau0=None, m=10, alpha=0.5, beta=1, q0=0.9, p=0.1)

    print(macs.vrptw.distances)

    nn_solution = macs.run()

    #TODO Sprawdzić czemu wyszło z local search.
    # nn_solution = {'length': 1420.53, 'vehicles': 4, 'routes': [[0, 5, 45, 83, 82, 36, 47, 64, 11, 62, 19, 88, 7, 18, 8, 90, 49, 46, 10, 20, 66, 35, 32, 70, 1, 0], [0, 63, 65, 33, 29, 12, 21, 73, 67, 40, 22, 87, 53, 41, 57, 43, 37, 97, 13, 89, 60, 48, 17, 91, 100, 93, 0], [0, 95, 42, 14, 92, 59, 98, 2, 72, 39, 23, 75, 15, 44, 61, 16, 38, 86, 99, 84, 85, 94, 6, 96, 26, 56, 74, 58, 0], [0, 28, 27, 52, 69, 31, 30, 71, 76, 79, 81, 51, 9, 78, 34, 3, 50, 68, 54, 4, 55, 25, 24, 77, 80, 0]]}
    # nn_solution = {'length': 1536.32, 'vehicles': 4, 'routes': [[0, 72, 39, 95, 2, 28, 29, 12, 21, 75, 23, 67, 73, 53, 40, 22, 41, 57, 43, 37, 97, 96, 13, 91, 17, 93, 100, 58, 89, 0], [0, 33, 65, 63, 64, 11, 19, 62, 88, 7, 18, 8, 90, 49, 46, 26, 54, 56, 74, 55, 25, 77, 80, 0], [0, 42, 14, 92, 59, 5, 83, 45, 47, 36, 82, 52, 69, 31, 30, 71, 76, 79, 81, 51, 9, 78, 34, 3, 50, 10, 66, 20, 32, 35, 68, 24, 4, 1, 70, 0], [0, 27, 98, 44, 15, 38, 16, 99, 61, 86, 85, 87, 94, 6, 84, 60, 48, 0]]}


    # Optimal R201_100
    # nn_solution = {'length': 1252.37, 'vehicles': 4, 'routes': [[0, 5, 83, 45, 82, 47, 36, 64, 11, 19, 62, 7, 88, 90, 18, 84, 8, 49, 46, 48, 60, 17, 91, 100, 93, 89, 0], [0, 2, 72, 39, 75, 23, 67, 21, 40, 73, 41, 22, 87, 57, 43, 37, 97, 96, 13, 58, 0],[0, 95, 59, 92, 42, 15 ,14, 98, 61, 16, 44, 38, 86, 85, 99, 6, 94, 53, 26, 54, 56, 74, 4, 55, 25, 24, 80, 0], [0, 33, 65, 63, 31, 69, 52, 27, 28, 12, 29, 76, 30, 71, 9, 51, 81, 79, 78, 34, 3, 50, 20, 10, 32, 66, 35, 68, 77, 1, 70, 0]]}





    # nn_solution = {'length': 1880.468130112817, 'vehicles': 15, 'routes': [[0, 93, 5, 75, 2, 1, 99, 100, 97, 95, 98, 7, 3, 4, 89, 91, 88, 86, 83, 82, 77, 87, 90, 0], [0, 20, 22, 24, 27, 29, 6, 32, 33, 34, 28, 26, 23, 25, 9, 11, 10, 8, 21, 96, 0], [0, 48, 0], [0, 67, 63, 62, 66, 69, 68, 65, 49, 55, 57, 40, 44, 46, 45, 42, 41, 78, 0], [0, 43, 81, 0], [0, 47, 80, 79, 0], [0, 74, 72, 61, 64, 54, 59, 51, 50, 52, 13, 0], [0, 30, 36, 18, 17, 73, 0], [0, 84, 85, 76, 71, 70, 0], [0, 31, 35, 37, 38, 39, 19, 15, 0], [0, 12, 0], [0, 14, 0], [0, 16, 0], [0, 94, 53, 56, 58, 60, 0], [0, 92, 0]]}
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))



    # nn_solution = local_search_clean(vrptw, nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)

    # TODO Feasibility
    # print(check_feasibility(vrptw, [[0, 93, 5, 24, 2, 1, 99, 100, 97, 95, 98, 7, 3, 4, 89, 91, 88, 86, 83, 82, 77, 87, 90, 0]]))

    # nn_solution = nearest_neighbors_vrptw(vrptw)
    # # #TODO Profiler
    # nn_solution = {'length': 1651.7, 'vehicles': 4, 'routes': [[0, 63, 65, 28, 2, 15, 21, 75, 98, 61, 44, 38, 16, 86, 99, 85, 22, 41, 57, 43, 37, 97, 96, 91, 13, 58, 0], [0, 72, 39, 23, 71, 30, 51, 79, 78, 81, 9, 90, 49, 46, 10, 20, 66, 32, 1, 68, 35, 70, 89, 93, 100, 0], [0, 42, 14, 92, 59, 95, 5, 45, 83, 82, 36, 47, 64, 11, 62, 19, 7, 88, 18, 6, 87, 94, 3, 34, 50, 26, 56, 55, 54, 74, 4, 25, 24, 80, 77, 0], [0, 33, 69, 31, 52, 27, 12, 29, 76, 67, 73, 40, 53, 8, 84, 60, 17, 48, 0]]}
    # cProfile.run('local_search_clean(vrptw, nn_solution)')
    #
    # nn_solution = {'length': 1651.7, 'vehicles': 4, 'routes': [[0, 63, 65, 28, 2, 15, 21, 75, 98, 61, 44, 38, 16, 86, 99, 85, 22, 41, 57, 43, 37, 97, 96, 91, 13, 58, 0], [0, 72, 39, 23, 71, 30, 51, 79, 78, 81, 9, 90, 49, 46, 10, 20, 66, 32, 1, 68, 35, 70, 89, 93, 100, 0], [0, 42, 14, 92, 59, 95, 5, 45, 83, 82, 36, 47, 64, 11, 62, 19, 7, 88, 18, 6, 87, 94, 3, 34, 50, 26, 56, 55, 54, 74, 4, 25, 24, 80, 77, 0], [0, 33, 69, 31, 52, 27, 12, 29, 76, 67, 73, 40, 53, 8, 84, 60, 17, 48, 0]]}
    # cProfile.run('local_search_clean(vrptw, nn_solution)')
    # macs.run()
    # nn_solution = nearest_neighbors_vrptw(vrptw)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # table = create_auxiliary_dict(vrptw, nn_solution["routes"])
    # print(table)
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
    # nn_solution = {'length': 1492.14, 'vehicles': 4, 'routes': [[0, 65, 52, 64, 83, 82, 11, 15, 16, 12, 73, 78, 79, 7, 6, 8, 46, 3, 4, 1, 55, 68, 0], [0, 14, 47, 59, 75, 23, 21, 19, 18, 76, 51, 57, 9, 53, 10, 97, 74, 13, 17, 60, 100, 70, 0], [0, 92, 95, 63, 33, 31, 29, 27, 28, 30, 62, 67, 71, 90, 99, 87, 86, 22, 49, 20, 56, 66, 96, 54, 37, 43, 35, 93, 91, 80, 0], [0, 42, 36, 39, 72, 45, 5, 2, 98, 69, 88, 61, 44, 40, 38, 41, 81, 94, 85, 84, 50, 26, 34, 32, 89, 24, 48, 25, 77, 58, 0]]}

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
    nn_solution = {'length': 1209.71, 'vehicles': 4, 'routes': [[0, 45, 5, 3, 1, 42, 36, 37, 39, 44, 38, 61, 90, 99, 52, 57, 86, 87, 9, 10, 97, 59, 74, 13, 17, 60, 100, 70, 0], [0, 69, 64, 48, 21, 23, 19, 18, 76, 51, 84, 22, 49, 20, 66, 56, 50, 34, 32, 89, 24, 25, 77, 75, 58, 83, 0], [0, 91, 92, 95, 85, 63, 33, 26, 27, 28, 29, 31, 30, 62, 67, 71, 96, 81, 72, 41, 40, 35, 43, 54, 93, 94, 80, 0], [0, 65, 82, 12, 14, 47, 11, 15, 16, 73, 88, 98, 53, 78, 79, 7, 8, 6, 46, 4, 2, 55, 68, 0]]}

    add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=100, font_color='r', font_size=8)

    plt.show()
