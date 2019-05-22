import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import cProfile
import pandas as pd
from itertools import chain
import copy

from services.calculate import nearest_neighbors_vrptw, local_search_clean, routes_length, check_feasibility, create_auxiliary_table, check_solution_feasibility, run_2opt
from VRPTW import Data, VRPTW, VRPTW_MACS_DS
from ACO import MACS_VRPTW


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)


def update_solution(solution_to_update):

    updated_solution = {"length": 0,
                        "vehicles": 0,
                        "routes": list(filter(([0, 0]).__ne__, solution_to_update["routes"]))}

    updated_solution["length"] = routes_length(vrptw, solution_to_update["routes"])
    updated_solution["vehicles"] = len(updated_solution["routes"])
    return updated_solution

def add_solution_to_graph(graph, solution):

    for route in solution["routes"]:
        for i in range(0, len(route)-1):
            graph.add_edge(route[i], route[i + 1])

    return graph


if __name__ == '__main__':

    data = Data("solomon/C1/C104_100")

    vrptw = VRPTW(data, vehicle_capacity=200)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    macs = MACS_VRPTW(vrptw, tau0=None, m=10, alpha=0.5, beta=1, q0=0.9, p=0.1)

    # print(macs.vrptw.distances)

    # nn_solution = macs.run()

    #TODO Sprawdzić czemu wyszło z local search.
    # nn_solution = {'length': 1420.53, 'vehicles': 4, 'routes': [[0, 5, 45, 83, 82, 36, 47, 64, 11, 62, 19, 88, 7, 18, 8, 90, 49, 46, 10, 20, 66, 35, 32, 70, 1, 0], [0, 63, 65, 33, 29, 12, 21, 73, 67, 40, 22, 87, 53, 41, 57, 43, 37, 97, 13, 89, 60, 48, 17, 91, 100, 93, 0], [0, 95, 42, 14, 92, 59, 98, 2, 72, 39, 23, 75, 15, 44, 61, 16, 38, 86, 99, 84, 85, 94, 6, 96, 26, 56, 74, 58, 0], [0, 28, 27, 52, 69, 31, 30, 71, 76, 79, 81, 51, 9, 78, 34, 3, 50, 68, 54, 4, 55, 25, 24, 77, 80, 0]]}
    # nn_solution = {'length': 1536.32, 'vehicles': 4, 'routes': [[0, 72, 39, 95, 2, 28, 29, 12, 21, 75, 23, 67, 73, 53, 40, 22, 41, 57, 43, 37, 97, 96, 13, 91, 17, 93, 100, 58, 89, 0], [0, 33, 65, 63, 64, 11, 19, 62, 88, 7, 18, 8, 90, 49, 46, 26, 54, 56, 74, 55, 25, 77, 80, 0], [0, 42, 14, 92, 59, 5, 83, 45, 47, 36, 82, 52, 69, 31, 30, 71, 76, 79, 81, 51, 9, 78, 34, 3, 50, 10, 66, 20, 32, 35, 68, 24, 4, 1, 70, 0], [0, 27, 98, 44, 15, 38, 16, 99, 61, 86, 85, 87, 94, 6, 84, 60, 48, 0]]}


    # Optimal R201_100
    # nn_solution = {'length': 1252.37, 'vehicles': 4, 'routes': [[0, 5, 83, 45, 82, 47, 36, 64, 11, 19, 62, 7, 88, 90, 18, 84, 8, 49, 46, 48, 60, 17, 91, 100, 93, 89, 0], [0, 2, 72, 39, 75, 23, 67, 21, 40, 73, 41, 22, 87, 57, 43, 37, 97, 96, 13, 58, 0],[0, 95, 59, 92, 42, 15 ,14, 98, 61, 16, 44, 38, 86, 85, 99, 6, 94, 53, 26, 54, 56, 74, 4, 55, 25, 24, 80, 0], [0, 33, 65, 63, 31, 69, 52, 27, 28, 12, 29, 76, 30, 71, 9, 51, 81, 79, 78, 34, 3, 50, 20, 10, 32, 66, 35, 68, 77, 1, 70, 0]]}





    # nn_solution = {'length': 1880.468130112817, 'vehicles': 15, 'routes': [[0, 93, 5, 75, 2, 1, 99, 100, 97, 95, 98, 7, 3, 4, 89, 91, 88, 86, 83, 82, 77, 87, 90, 0], [0, 20, 22, 24, 27, 29, 6, 32, 33, 34, 28, 26, 23, 25, 9, 11, 10, 8, 21, 96, 0], [0, 48, 0], [0, 67, 63, 62, 66, 69, 68, 65, 49, 55, 57, 40, 44, 46, 45, 42, 41, 78, 0], [0, 43, 81, 0], [0, 47, 80, 79, 0], [0, 74, 72, 61, 64, 54, 59, 51, 50, 52, 13, 0], [0, 30, 36, 18, 17, 73, 0], [0, 84, 85, 76, 71, 70, 0], [0, 31, 35, 37, 38, 39, 19, 15, 0], [0, 12, 0], [0, 14, 0], [0, 16, 0], [0, 94, 53, 56, 58, 60, 0], [0, 92, 0]]}



    # nn_solution = local_search_clean(vrptw, nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # nn_solution = local_search_clean(vrptw, nn_solution)

    # TODO Feasibility


    nn_solution = nearest_neighbors_vrptw(vrptw)
    # # #TODO Profiler
    # nn_solution = {'length': 1651.7, 'vehicles': 4, 'routes': [[0, 63, 65, 28, 2, 15, 21, 75, 98, 61, 44, 38, 16, 86, 99, 85, 22, 41, 57, 43, 37, 97, 96, 91, 13, 58, 0], [0, 72, 39, 23, 71, 30, 51, 79, 78, 81, 9, 90, 49, 46, 10, 20, 66, 32, 1, 68, 35, 70, 89, 93, 100, 0], [0, 42, 14, 92, 59, 95, 5, 45, 83, 82, 36, 47, 64, 11, 62, 19, 7, 88, 18, 6, 87, 94, 3, 34, 50, 26, 56, 55, 54, 74, 4, 25, 24, 80, 77, 0], [0, 33, 69, 31, 52, 27, 12, 29, 76, 67, 73, 40, 53, 8, 84, 60, 17, 48, 0]]}



    def test():
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)
        local_search_clean(vrptw, nn_solution)


    cProfile.run('test()')
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
    #
    #
    # # print(check_feasibility(vrptw, nn_solution["routes"]))
    # # print(nn_solution)
    #
    # nn_solution = local_search_clean(vrptw, nn_solution)
    # # print(check_feasibility(vrptw, nn_solution["routes"]))
    # print(nn_solution)




    # nn_solution = update_solution(nn_solution)
    # print(nn_solution)
    #
    # print("Feasible:", check_feasibility(vrptw, nn_solution["routes"]))
    # for ajdi, route in enumerate(nn_solution["routes"]):
    #     route = run_2opt(vrptw, route)
    #     nn_solution["routes"][ajdi] = route
    # nn_solution = update_solution(nn_solution)
    # print(nn_solution)
    # print("Feasible:", check_solution_feasibility(vrptw, nn_solution["routes"]))
    #
    # print(routes_length(vrptw, [[0, 98, 94, 95, 96, 92, 93, 0]]))
    # print(routes_length(vrptw, [[0, 98, 96, 95, 94, 92, 93, 0]]))





    # nn_solution = local_search_clean(vrptw, nn_solution)
    # print(nn_solution)

    # while [0, 57, 55, 54, 53, 56, 58, 60, 59, 68, 69, 0] not in nn_solution["routes"]:
    #     nn_solution = local_search_clean(vrptw, nn_solution)


    add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=100, font_color='r', font_size=8)

    plt.show()
