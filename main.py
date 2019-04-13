import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


from services.calculate import nearest_neighbors_vrptw
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


def check_fisibility(vrptw, routes):

    for route in routes:

        time = 0
        load = 0

        for i in range(0, len(route)-1):
            if time + vrptw.distances[route[i]][route[i+1]] > vrptw.time_windows[route[i+1]][1]:
                return False
            elif time + vrptw.distances[route[i]][route[i+1]] > vrptw.time_windows[route[i+1]][0]:
                time = time + vrptw.distances[route[i]][route[i+1]] + vrptw.service_times[i+1]
                load = load + vrptw.demands[route[i+1]]
            else:
                time = vrptw.time_windows[route[i+1]][0] + vrptw.service_times[route[i+1]]
                load = load + vrptw.demands[route[i+1]]

        if load > vrptw.vehicle_capacity:
            return False

    return True

def local_search(vrptw, first_route, second_route):

    i = 0

    def swap_edges(route1, route2, X1pi, X2pi, Y1pi, Y2pi):

        temp_r1 = []
        temp_r2 = []

        temp_r1 += route1[:X1pi]
        temp_r1 += route2[X2pi:Y2pi]
        temp_r1 += route1[Y1pi:]

        temp_r2 += route2[:X2pi]
        temp_r2 += route1[X1pi:Y1pi]
        temp_r2 += route2[Y2pi:]

        return temp_r1, temp_r2

    test = []
    test_set = []

    for X1_index, X1 in enumerate(first_route[:-1]):
        for X2_index, X2 in enumerate(second_route[:-1]):
            for Y1_index, Y1 in enumerate(first_route[X1_index:-1], X1_index):
                for Y2_index, Y2 in enumerate(second_route[X2_index:-1], X2_index):

                    i += 1

                    #  swaperooni:
                    if X1 == Y1 and X2 == Y2:

                        temp = first_route[:X1_index+1] + second_route[Y2_index+1:]
                        temp_second = second_route[:X2_index+1] + first_route[Y1_index+1:]
                        temp_first = temp

                        test.append(len(temp_first) + len(temp_second))
                        test_set.append(len(set(temp_first)) + len(set(temp_second)))

                    else:

                        temp_first, temp_second = swap_edges(first_route, second_route, X1_index+1, X2_index+1, Y1_index+1, Y2_index+1)

                        test.append(len(temp_first) + len(temp_second))
                        test_set.append(len(set(temp_first)) + len(set(temp_second)))

                    best_len = routes_length(vrptw, [first_route, second_route])
                    swaperooni_len = routes_length(vrptw, [temp_first, temp_second])

                    if swaperooni_len < best_len:
                        if check_fisibility(vrptw, [temp_first, temp_second]):
                            print(swaperooni_len, "<", best_len)
                            print(first_route)
                            print(temp_first)
                            print(second_route)
                            print(temp_second)



    # print("Test:", test)
    # print("Test set:", test_set)

def routes_length(vrptw, routes):
    length = 0
    for route in routes:
        for i in range(0, len(route)-1):
            length += vrptw.distances[route[i]][route[i+1]]

    return length


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

    print(nn_solution)

    print("Doin local search:")

    length = len(nn_solution["routes"])

    for i in range(0, length-1):
        for j in range(i+1, length):
            local_search(vrptw, first_route=nn_solution["routes"][i], second_route=nn_solution["routes"][j])


    nn_graph = add_solution_to_graph(vrptw.graph, nn_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=200, font_color='r', font_size=8)

    plt.show()

    # macs = MACS_VRPTW(vrptw, 1, 1, 1, None)




