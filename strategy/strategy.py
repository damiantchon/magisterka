import abc


class AntOptimizationStrategyAbstract(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_parameters(self):
        pass

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
    def update_pheromones(self):
        pass