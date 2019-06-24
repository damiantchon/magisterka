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

best_len_to_date = {
    "solomon/R1/R101": 1650.80,
    "solomon/R1/R102": 1486.12,
    "solomon/R1/R103": 1292.68,
    "solomon/R1/R104": 1007.31,
    "solomon/R1/R105": 1377.11,
    "solomon/R1/R106": 1252.03,
    "solomon/R1/R107": 1104.66,
    "solomon/R1/R108": 960.88,
    "solomon/R1/R109": 1194.73,
    "solomon/R1/R110": 1118.84,
    "solomon/R1/R111": 1096.72,
    "solomon/R1/R112": 982.14,

    "solomon/C1/C101": 828.94,
    "solomon/C1/C102": 828.94,
    "solomon/C1/C103": 828.06,
    "solomon/C1/C104": 824.78,
    "solomon/C1/C105": 828.94,
    "solomon/C1/C106": 828.94,
    "solomon/C1/C107": 828.94,
    "solomon/C1/C108": 828.94,
    "solomon/C1/C109": 828.94,

    "solomon/R2/R201": 1252.37,
    "solomon/R2/R202": 1191.70,
    "solomon/R2/R203": 939.50,
    "solomon/R2/R204": 825.52,
    "solomon/R2/R205": 994.43,
    "solomon/R2/R206": 906.14,
    "solomon/R2/R207": 890.61,
    "solomon/R2/R208": 726.82,
    "solomon/R2/R209": 909.16,
    "solomon/R2/R210": 939.37,
    "solomon/R2/R211": 885.71,

    "solomon/C2/C201": 591.56,
    "solomon/C2/C202": 591.56,
    "solomon/C2/C203": 591.17,
    "solomon/C2/C204": 590.60,
    "solomon/C2/C205": 588.88,
    "solomon/C2/C206": 588.49,
    "solomon/C2/C207": 588.29,
    "solomon/C2/C208": 588.32,

    "solomon/RC1/RC101": 1696.95,
    "solomon/RC1/RC102": 1554.75,
    "solomon/RC1/RC103": 1261.67,
    "solomon/RC1/RC104": 1135.48,
    "solomon/RC1/RC105": 1629.44,
    "solomon/RC1/RC106": 1424.73,
    "solomon/RC1/RC107": 1230.48,
    "solomon/RC1/RC108": 1139.82,

    "solomon/RC2/RC201": 1406.94,
    "solomon/RC2/RC202": 1365.65,
    "solomon/RC2/RC203": 1049.62,
    "solomon/RC2/RC204": 798.46,
    "solomon/RC2/RC205": 1297.65,
    "solomon/RC2/RC206": 1146.32,
    "solomon/RC2/RC207": 1061.14,
    "solomon/RC2/RC208": 828.14

}

def log(string):
    file = open("log.txt", "a")
    file.write(string)
    file.close()

if __name__ == '__main__':

    file_sets = []

    # file_sets.append((sorted(["solomon/R1/" + f for f in listdir("solomon/R1") if isfile(join("solomon/R1", f))]), 200))
    # file_sets.append((sorted(["solomon/R2/" + f for f in listdir("solomon/R2") if isfile(join("solomon/R2", f))]), 1000))
    # file_sets.append((sorted(["solomon/C1/" + f for f in listdir("solomon/C1") if isfile(join("solomon/C1", f))]), 200))
    # file_sets.append((sorted(["solomon/C2/" + f for f in listdir("solomon/C2") if isfile(join("solomon/C2", f))]), 700))
    # file_sets.append((sorted(["solomon/RC1/" + f for f in listdir("solomon/RC1") if isfile(join("solomon/RC1", f))]), 200))
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

            work_time = 1800 # algorithtm working time
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

                solution_with_fewer_vehicles_found = False

                while stop_time >= time.time() and not solution_with_fewer_vehicles_found:

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

                        log("V:{}, L:{}\n".format(str(new_best_solution["vehicles"]), str(new_best_solution["length"])))

                        if new_best_solution["vehicles"] < v:

                            os.kill(p_vei.pid, signal.SIGTERM)
                            os.kill(p_time.pid, signal.SIGTERM)
                            p_vei.join()
                            p_time.join()
                            best_solution = new_best_solution
                            solution_with_fewer_vehicles_found = True

                        else:
                            best_solution = new_best_solution

                        if new_best_solution["length"] == best_len_to_date[file]:
                            if (p_vei.is_alive()):
                                os.kill(p_vei.pid, signal.SIGTERM)
                            if (p_time.is_alive()):
                                os.kill(p_time.pid, signal.SIGTERM)
                            p_vei.join()
                            p_time.join()
                            print("Im here!")
                            stop_time = 0





            log("{} || ***FINAL SOLUTION***\n".format(file))
            log(str(best_solution) + "\n")



