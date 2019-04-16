import abc
import numpy as np
from services.calculate import nearest_neighbors_vrptw, local_search_clean


class MACS_VRPTW(): #Multiple Ant Colony System for Vehicle Routing Problems With Time Windows

    def __init__(self, vrptw, m, alpha, beta, tau0): #jeśli tau0 , m - liczba mrówek

        self.vrptw = vrptw
        self.tau0 = tau0
        self.m = m
        self.alpha = alpha
        self.beta = beta
        self.pheromones = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j
        self.shortest_path = []

        self.best_solution = {}

        #
        # if self.tau0 is None:
        #     self.tau0 = 1/(vrptw.size * self.nn_init_solution["length"])

        # print(self.tau0)

    def run(self):
        self.best_solution = nearest_neighbors_vrptw(self.vrptw)
        self.best_solution = local_search_clean(self.vrptw, self.best_solution)
        # main loop

        #todo WARUNKI WYJŚCIA
        while True:
            break



    def ACS_VEI(self, v):
        pass

    def ACS_TIME(self, v):
        pass

