import re
import networkx as nx
import numpy as np

from random import choice
from services.calculate import euclidean_distance


class ParsedData:
    """Klasa zweierające 'surowe' dane na temat problemu VRPTW"""

    def __init__(self, input_file_name):

        self.size = None
        self.ids = []
        self.ids_data = []
        self.coordinates = []
        self.demands = []
        self.time_windows = []
        self.service_times = []

        self.parse_raw_data_model(input_file_name)

    def __str__(self):

        return_me = ""

        return_me += "Size: " + str(self.size) + "\n"
        return_me += "IDs: " + str(self.ids) + "\n"
        return_me += "Coordinates: " + str(self.coordinates) + "\n"
        return_me += "Demands: " + str(self.demands) + "\n"
        return_me += "Time Windows: " + str(self.time_windows) + "\n"
        return_me += "Service Times " + str(self.service_times) + "\n"

        return return_me

    def parse_raw_data_model(self, raw_input_file):

        def get_raw_data():
            return_me = []
            with open(raw_input_file, "r") as fin:

                fin.readline()

                for line in fin:
                    if not line.strip().startswith("#"):
                        line = re.sub(r'\s+', ' ', line).strip() + "\n"

                        splited = list(map(float, line.split()))
                        return_me.append(splited)

            return return_me

        raw_data = get_raw_data()
        for i in range(0, len(raw_data)):
            self.size = len(raw_data)

            self.ids_data.append(raw_data[i][0])

            self.ids.append(i)

            self.coordinates.append((raw_data[i][1], raw_data[i][2]))

            self.demands.append(int(raw_data[i][3]))

            self.time_windows.append((raw_data[i][4], raw_data[i][5]))

            self.service_times.append(raw_data[i][6])

    def get_node_data(self, num):

        if self.ids[num] is not None:

            data = {}
            data["id"] = self.ids[num]
            data["coordinates"] = self.coordinates[num]
            data["demand"] = self.demands[num]
            data["time_window"] = self.time_windows[num]
            data["service_times"] = self.service_times[num]

            return data

        else:
            return None

class VRPTW:
    """Klasa zawierająca podstawowy model VRPTW"""
    def __init__(self, data, vehicle_capacity):

        # From data
        self.ids_data = data.ids_data
        self.size = data.size
        self.ids = data.ids
        self.coordinates = data.coordinates
        self.demands = data.demands
        self.time_windows = data.time_windows
        self.service_times = data.service_times

        # Capacity
        self.vehicle_capacity = vehicle_capacity

        # Calculated
        self.distances = self.create_distance_matrix()

        self.graph = nx.Graph()

        for i in range(0, data.size):
            self.graph.add_node(data.ids[i],
                                coordinates=data.coordinates[i],
                                demands=data.demands[i],
                                time_windows=data.time_windows[i],
                                service_times=data.service_times[i])

    def create_distance_matrix(self):

        zeros = np.zeros((self.size, self.size))

        for i in range(0, self.size):
            for j in range(i+1, self.size):

                zeros[i][j] = euclidean_distance(self.coordinates[i], self.coordinates[j])
                zeros[j][i] = zeros[i][j]

        return zeros

    def get_clients_ids(self):
        return self.ids[1:]

    def get_depo_ids(self):
        return [self.ids[0]]

class VRPTW_MACS_DS:
    """Klasa zawierająca model problemu VRPTW dla algorytmu MACS-VRPTW"""
    def __init__(self, vrptw, v):

        self.v = v

        self.ids_data_legacy = vrptw.ids_data.copy()
        self.size = vrptw.size + (v-1)
        self.vehicle_capacity = vrptw.vehicle_capacity

        self.ids = []

        # Creating ids
        for i in range(0, self.size):
            self.ids.append(i)

        self.depo_ids = [0]

        for i in range(vrptw.size, self.size):
            self.depo_ids.append(i)

        self.coordinates = vrptw.coordinates.copy()
        self.demands = vrptw.demands.copy()
        self.time_windows = vrptw.time_windows.copy()
        self.service_times = vrptw.service_times.copy()

        for i in range(vrptw.size, self.size):
            self.coordinates.append(self.coordinates[0])
            self.demands.append(self.demands[0])
            self.time_windows.append(self.time_windows[0])
            self.service_times.append(self.service_times[0])

        self.distances = vrptw.distances.copy()


        # Adding distances
        if v > 1:

            new_array_1 = []

            for i in range(0, vrptw.size):
                array = np.full(v-1, self.distances[i][0])
                new_array_1 = np.append(arr=new_array_1, values=array)

            new_array_1 = new_array_1.reshape((vrptw.size, v-1))
            self.distances = np.hstack((self.distances, new_array_1))

            new_array_2 = []

            for i in range(0, v-1):
                array = vrptw.distances[0]
                array2 = np.zeros(v-1)

                new_array_2 = np.concatenate((new_array_2, array, array2))

            new_array_2 = new_array_2.reshape((v-1, self.size))

            self.distances = np.vstack((self.distances, new_array_2))

        self.graph = nx.Graph()

        for i in range(0, self.size):
            self.graph.add_node(self.ids[i],
                                coordinates=self.coordinates[i],
                                demands=self.demands[i],
                                time_windows=self.time_windows[i],
                                service_times=self.service_times[i])

    def get_random_depo(self):
        return choice(self.depo_ids)
