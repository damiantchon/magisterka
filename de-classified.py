import networkx as nx
import cProfile
import multiprocessing as mp
from queue import Full, Empty
import os
import signal

import time

from services.calculate import nearest_neighbors_vrptw
from VRPTW import Data, VRPTW
from ACO import MACS_VRPTW

if __name__ == '__main__':

    data = Data("solomon/R2/R201_100")

    vrptw = VRPTW(data, vehicle_capacity=1000)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    macs = MACS_VRPTW(vrptw, tau0=None, m=10, alpha=0.5, beta=1, q0=0.9, p=0.1)

    print(macs.vrptw.distances)

    best_solution = nearest_neighbors_vrptw(vrptw)

    # args = sys.argv()

    work_time = 1800 # algorithtm working time
    start_time = time.time()
    stop_time = start_time + work_time

    # v = best_solution["vehicles"]
    #
    # queue = mp.Queue()
    # vei_time_queue = mp.Queue()
    #
    # cProfile.run("macs.ACS_TIME(v+1, best_solution, start_time, stop_time, queue, vei_time_queue)")

    while stop_time >= time.time():

        v = best_solution["vehicles"]

        queue = mp.Queue()
        vei_time_queue = mp.Queue()

        p_vei = mp.Process(target=macs.ACS_VEI, args=(v, best_solution, stop_time, queue, vei_time_queue))
        p_time = mp.Process(target=macs.ACS_TIME, args=(v+1, best_solution, start_time, stop_time, queue, vei_time_queue))

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
                print("GOT NEW BEST SOLUTION!")

                if new_best_solution["vehicles"] < v:

                    os.kill(p_vei.pid, signal.SIGTERM)
                    os.kill(p_time.pid, signal.SIGTERM)
                    p_vei.join()
                    p_time.join()
                    best_solution = new_best_solution
                    solution_with_less_vehicles_found = True

                else:
                    best_solution = new_best_solution

            print("NEW_BEST_SOLUTION (VEI) (Working time: {} at {})".format(str(time.time() - start_time),
                                                                            str(time.asctime())))
            print(best_solution)




    print("***FINAL SOLUTION***")
    print(best_solution)


