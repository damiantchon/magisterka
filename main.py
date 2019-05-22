import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import cProfile
import pandas as pd
import os
import sys
import time
import signal
import multiprocessing as mp
from queue import Full, Empty
from itertools import chain
import copy

from services.calculate import nearest_neighbors_vrptw, local_search_clean, routes_length, check_feasibility, create_auxiliary_table, check_solution_feasibility, run_2opt
from VRPTW import Data, VRPTW, VRPTW_MACS_DS
from ACO import MACS_VRPTW


desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)

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

    for route in solution["routes"]:
        for i in range(0, len(route)-1):
            graph.add_edge(route[i], route[i + 1])

    return graph


if __name__ == '__main__':

    print(sys.argv)

    log("Started working on {} solution.\n".format(str(sys.argv[1])))

    data = Data(str(sys.argv[1]))

    vrptw = VRPTW(data, vehicle_capacity=1000)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    macs = MACS_VRPTW(vrptw, tau0=None, m=10, alpha=0.5, beta=1, q0=0.9, p=0.1)

    print(macs.vrptw.distances)

    best_solution = nearest_neighbors_vrptw(vrptw)

    work_time = int(sys.argv[2])  # algorithtm working time
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


    add_solution_to_graph(vrptw.graph, best_solution)

    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_depo_ids(), with_labels=True, node_color='r',
                     node_size=300, font_color='k', font_size=8, labels=time_windows)
    nx.draw_networkx(vrptw.graph, pos=pos, nodelist=vrptw.get_clients_ids(), with_labels=True, node_color='k',
                     node_size=100, font_color='r', font_size=8)

    plt.show()
