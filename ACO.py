import abc
import numpy as np


class ACOStrategy(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, vrptw):
        self.vrptw = vrptw

    @abc.abstractmethod
    def initialize_pheromones(self):
        pass

    @abc.abstractmethod
    def construct_ant_solution(self):
        pass

    @abc.abstractmethod
    def daemon_actions(self):  # optional
        pass

    @abc.abstractmethod
    def global_update_pheromones(self):
        pass


class MACS_VRPTW(ACOStrategy): #Multiple Ant Colony System for Vehicle Routing Problems With Time Windows

    def __init__(self, vrptw, tau0, m, alpha, beta): #tau0 - początkowa wartość feromonu, m - liczba mrówek
        super().__init__(vrptw)

        self.tau0 = tau0
        self.m = m
        self.alpha = alpha
        self.beta = beta
        self.pheromones = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j
        self.shortest_path = []

        #TODO NN Heuristic

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
