import abc
import numpy as np

class Ant(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.L = 0  # Długość trasy wyznaczonej przez mrówkę.
        self.M = [] # Trasa wyznaczona przez daną mrówkę.

    @abc.abstractmethod
    def move(self):
        pass

