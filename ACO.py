import abc
import numpy as np
from services.calculate import nearest_neighbors_vrptw


class MACS_VRPTW(): #Multiple Ant Colony System for Vehicle Routing Problems With Time Windows

    def __init__(self, vrptw, m, alpha, beta, tau0): #jeśli tau0 , m - liczba mrówek

        self.vrptw = vrptw
        self.tau0 = tau0
        self.m = m
        self.alpha = alpha
        self.beta = beta
        self.pheromones = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j
        self.shortest_path = []

        self.nn_init_solution = nearest_neighbors_vrptw(self.vrptw)

        self.shortest_path = self.nn_init_solution["routes"]

        if self.tau0 is None:
            self.tau0 = 1/(vrptw.size * self.nn_init_solution["length"])

        print(self.tau0)


    def initialize_pheromones(self):

        # setup pheromones
        n = self.vrptw.data.size
        self.pheromones = np.full((n, n), self.tau0)

    def construct_ant_solution(self):
        pass

    def daemon_actions(self):

        pass

    def global_update_pheromones(self):
        pass

    def new_active_ant(self,k, local_search, IN):
        pass
