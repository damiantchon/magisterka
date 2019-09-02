import os
import sys
import time
import signal
import random
import datetime
import argparse
import numpy as np
import networkx as nx
import pandas as pd
import multiprocessing as mp
from queue import Empty

from services.calculate import nearest_neighbors_vrptw, routes_length
from data import ParsedData, VRPTW
from MACS_VRPTW import MACS_VRPTW


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


def describe_solution(solution, logging=False, filename=None):

    def get_length(route):
        lenght = 0
        for i in range(0, len(route)-1):
            lenght += vrptw.distances[i][i+1]

        return round(lenght, 2)

    def get_load(route):
        load = 0
        for customer in route:
            load += vrptw.demands[customer]

        return load

    for i, route in enumerate(solution["routes"]):
        load = get_load(route)
        length = get_length(route)
        if logging:
            log("Cykl: {}\t Długość: {}\t Ładunek: {}\t{}\n".format(i + 1, length, load, route), filename)
        else:
            print("Cykl: {}\t Długość: {}\t Ładunek: {}\t{}".format(i+1, length, load, route))


def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x

def restricted_float_10000(x):
    x = float(x)
    if x < 0.0 or x > 10000.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 10000.0]"%(x,))
    return x

def restricted_int_0_10000(x):
    x = float(x)
    if x < 0.0 or x > 100000:
        raise argparse.ArgumentTypeError("{} not in range [0, 100000]".format(x))
    return int(x)

def restricted_int_1_10000(x):
    x = float(x)
    if x < 0.0 or x > 100000:
        raise argparse.ArgumentTypeError("{} not in range [1, 100000]".format(x))
    return int(x)


def restricted_int_5_10000(x):
    x = float(x)
    if x < 5 or x > 10000:
        raise argparse.ArgumentTypeError("{} not in range [5, 10000]".format(x))
    return int(x)


def restricted_file(x):
    if not os.path.exists(x):
        raise argparse.ArgumentError("File {} not found".format(x))
    return str(x)


def log(string, filename):
    if os.path.exists(filename):
        file = open(filename, "a")
    else:
        file = open(filename, "w+")

    file.write(string)
    file.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''Algorytm MACS-VRPTW''',
        epilog='''Wykonał: Damian Tchoń'''
    )

    parser.add_argument('file', help="Plik zawierający model danych problem VRPTW", type=restricted_file)
    parser.add_argument('capacity', help="Ładowność pojazdów podanego problemu VRPTW", type=restricted_int_0_10000)
    parser.add_argument('time', help="Długość działania algorytmu w sekundach", type=int)
    parser.add_argument('m', help="Parametr m - liczba mrówek w kolonii [def=10]", default=10, type=restricted_int_1_10000)
    parser.add_argument('beta', help="Parametr beta - im większy, tym większa istotność atrakcyjności n [def=1]", default=1, type=restricted_float_10000)
    parser.add_argument('q0', help="Parametr q0 - prawdopodobieństwo pseudolosowego wyboru scieżki [def=0.1]", default=0.1, type=restricted_float)
    parser.add_argument('p', help="Parametr p - szybkość odparowywania feromonu [def=0.9]", default=0.9, type=restricted_float)

    args = parser.parse_args()

    file = args.file  # source file with model

    work_time = int(args.time)  # algorithtm working time

    f = ("solutions/SOLUTION_" + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

    # log("Started working on {} solution.\n".format(str(file)), f)

    data = ParsedData(str(file))

    vrptw = VRPTW(data, vehicle_capacity=200)

    pos = nx.get_node_attributes(vrptw.graph, 'coordinates')
    demands = nx.get_node_attributes(vrptw.graph, 'demands')
    time_windows = nx.get_node_attributes(vrptw.graph, 'time_windows')

    macs = MACS_VRPTW(vrptw, tau0=None, m=args.m, beta=args.beta, q0=args.q0, p=args.p)

    print('Rozpoczęto pracę nad "{}"'.format(args.file))
    print('Paramtery algorytmu: m={}, beta={}, q0={}, p={}'.format(args.m, args.beta, args.q0, args.p))

    best_solution = nearest_neighbors_vrptw(vrptw=vrptw, v=None)

    start_time = time.time()
    stop_time = start_time + work_time

    print('Przewidywany czas zakończenia:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stop_time)))
    print('...')

    p_vei = None
    p_time = None

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
                    queueue = queue.get(timeout=0.1)
                    new_best_solution = queueue[0]
                except Empty:
                    pass
                if new_best_solution:
                    got_new_solution = True

            if new_best_solution:
                # log("NEW_BEST_SOLUTION OF {} (Working time: {} at {})\n".format(file, str(time.time() - start_time),
                #                                                               str(time.asctime())), f)
                # log(str(new_best_solution) + "\n", f)
                if new_best_solution["vehicles"] < v:

                    os.kill(p_vei.pid, signal.SIGTERM)
                    # print(str(time.time() - start_time), "SIGTERM to VEI {} sent".format(p_vei.pid))
                    os.kill(p_time.pid, signal.SIGTERM)
                    # print(str(time.time() - start_time), "SIGTERM to TIME {} sent".format(p_time.pid))
                    p_vei.join()
                    p_time.join()
                    best_solution = new_best_solution
                    solution_with_less_vehicles_found = True

                else:
                    best_solution = new_best_solution

    os.kill(p_vei.pid, signal.SIGTERM)
    os.kill(p_time.pid, signal.SIGTERM)

    print('Zakończono pracę nad "{}"'.format(args.file))

    print("Użyte pojazdy:  {}".format(best_solution["vehicles"]))
    print("Łączna długość: {}".format(best_solution["length"]))
    print("Trasy:")
    describe_solution(best_solution, logging=False, filename=f)
    print('\nWyniki zapisano w pliku "{}"'.format(f))


    log('Paramtery algorytmu: m={}, beta={}, q0={}, p={}\n\n'.format(args.m, args.beta, args.q0, args.p), f)

    log("Problem: {}\n".format(args.file), f)
    log("Ładowność pojazdu: {}\n\n".format(args.capacity), f)

    log("Użyte pojazdy:  {}\n".format(best_solution["vehicles"]), f)
    log("Łączna długość: {}\n".format(best_solution["length"]), f)
    log("\nTrasy:\n", f)
    describe_solution(best_solution, logging=True, filename=f)

