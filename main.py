import os
import sys
import time
import signal
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import multiprocessing as mp
from queue import Empty


from services.calculate import nearest_neighbors_vrptw, routes_length
from VRPTW import Data, VRPTW
from ACO import MACS_VRPTW


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)


def get_spaced_colors(n):
    max_value = 16581375  # 255**3
    interval = int(max_value / n)
    colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]

    return [(int(i[:2], 16)/255, int(i[2:4], 16)/255, int(i[4:], 16)/255) for i in colors]

def log(string):
    file = open("log.txt", "a")
    file.write(string)
    file.close()

def update_solution(solution_to_update):

    updated_solution = {"length": 0,
                        "vehicles": 0,
                        "routes": list(filter(([0, 0]).__ne__, solution_to_update["routes"]))}

    updated_solution["length"] = routes_length(vrptw, solution_to_update["routes"])
    updated_solution["vehicles"] = len(updated_solution["routes"])
    return updated_solution

def add_solution_to_graph(graph, solution):

    colors = get_spaced_colors(len(solution["routes"]))

    for c, route in enumerate(solution["routes"]):
        edgelist = []
        for i in range(0, len(route) - 1):
            edgelist.append((route[i], route[i + 1]))
        print(colors[c])
        graph.add_edges_from(edgelist, color=colors[c])

    return graph

def draw_solution_to_graph(graph, pos, solution):

    colors = get_spaced_colors(len(solution["routes"]))

    for route in enumerate(solution["routes"]):
        edgelist = []
        for i in range(0, len(route) - 1):
            edgelist.append((route[i], route[i+1]))

        r = lambda: random.randint(0, 255)
        color = '#%02X%02X%02X' % (r(),r(),r())

        nx.draw_networkx_edges(G=graph, pos=pos, edgelist=edgelist, edge_color=color)


    return graph
if __name__ == '__main__':

    print(sys.argv)

    file = str(sys.argv[1]) # source file with model

    work_time = int(sys.argv[2]) # algorithtm working time

    log("Started working on {} solution.\n".format(str(file)))

    data = Data(str(file))

    vrptw = VRPTW(data, vehicle_capacity=200)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    macs = MACS_VRPTW(vrptw, tau0=None, m=10, alpha=0.5, beta=1, q0=0.9, p=0.1)

    print(macs.vrptw.distances)

    best_solution = nearest_neighbors_vrptw(vrptw)

    start_time = time.time()
    stop_time = start_time + work_time

    while stop_time >= time.time():

        v = best_solution["vehicles"]

        queue = mp.Queue()
        vei_time_queue = mp.Queue()

        p_vei = mp.Process(target=macs.ACS_VEI, args=(v, best_solution, stop_time, queue, vei_time_queue))
        p_time = mp.Process(target=macs.ACS_TIME,
                            args=(v + 1, best_solution, start_time, stop_time, queue, vei_time_queue))

        p_vei.start()
        p_time.start()

        solution_with_less_vehicles_found = False

        while not solution_with_less_vehicles_found and stop_time >= time.time():

            new_best_solution = None
            got_new_solution = False

            while not got_new_solution and stop_time >= time.time():
                try:
                    new_best_solution = queue.get(timeout=2)
                except Empty:
                    pass
                if new_best_solution:
                    got_new_solution = True

            if new_best_solution:
                log("NEW_BEST_SOLUTION OF {} (Working time: {} at {})".format(file, str(time.time() - start_time),
                                                                              str(time.asctime())))
                log(str(new_best_solution) + "\n")
                if new_best_solution["vehicles"] < v:

                    os.kill(p_vei.pid, signal.SIGTERM)
                    os.kill(p_time.pid, signal.SIGTERM)
                    p_vei.join()
                    p_time.join()
                    best_solution = new_best_solution
                    solution_with_less_vehicles_found = True

                else:
                    best_solution = new_best_solution




    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=100, font_color='white', font_size=8)

    add_solution_to_graph(vrptw.graph, best_solution)

    edges = vrptw.graph.edges()
    colors = [vrptw.graph[u][v]['color'] for u, v in edges]

    nx.draw_networkx_edges(vrptw.graph, pos=pos, edges=edges, edge_color=colors)

    plt.show()

    # plt.savefig("result.png", bbox_inches='tight')
