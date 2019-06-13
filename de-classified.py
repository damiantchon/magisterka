import networkx as nx
import cProfile
import multiprocessing as mp
from queue import Full, Empty
import os
import signal
from os import listdir
from os.path import isfile, join

import time

from services.calculate import nearest_neighbors_vrptw
from VRPTW import Data, VRPTW
from ACO import MACS_VRPTW


def log(string):
    file = open("log.txt", "a")
    file.write(string)
    file.close()

if __name__ == '__main__':

    file_sets = []

    file_sets.append((sorted(["solomon/R1/" + f for f in listdir("solomon/R1") if isfile(join("solomon/R1", f))]), 200))
    file_sets.append((sorted(["solomon/R2/" + f for f in listdir("solomon/R2") if isfile(join("solomon/R2", f))]), 1000))
    file_sets.append((sorted(["solomon/C1/" + f for f in listdir("solomon/C1") if isfile(join("solomon/C1", f))]), 200))
    file_sets.append((sorted(["solomon/C2/" + f for f in listdir("solomon/C2") if isfile(join("solomon/C2", f))]), 700))
    file_sets.append((sorted(["solomon/RC1/" + f for f in listdir("solomon/RC1") if isfile(join("solomon/RC1", f))]), 200))
    file_sets.append((sorted(["solomon/RC2/" + f for f in listdir("solomon/RC2") if isfile(join("solomon/RC2", f))]), 1000))

    # files = ["solomon/C1/" + f for f in listdir("solomon/C1") if isfile(join("solomon/C1", f))]


    print(file_sets)

    for set in file_sets:


        for file in set[0]:

            log("Started working on {} solution.\n".format(file))

            data = Data(file)

            vrptw = VRPTW(data, vehicle_capacity=set[1])

            pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
            demands = nx.get_node_attributes(vrptw.graph, 'demands')
            time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

            macs = MACS_VRPTW(vrptw, tau0=None, m=10, beta=1, q0=0.9, p=0.1)

            print(macs.vrptw.distances)

            best_solution = nearest_neighbors_vrptw(vrptw)

            work_time = 30 # algorithtm working time
            start_time = time.time()
            stop_time = start_time + work_time

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
                            new_best_solution = queue.get(timeout=0.1)
                        except Empty:
                            pass
                        if new_best_solution:
                            got_new_solution = True

                    if new_best_solution:

                        log("{} (Working time: {} at {})\n".format(file, str(int(time.time() - start_time)),
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





            log("{} || ***FINAL SOLUTION***\n".format(file))
            log(str(best_solution) + "\n")



