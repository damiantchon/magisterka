import re
import networkx as nx
import numpy as np
from services.calculate import manhattan_distance, euclidean_distance


class VRPTW:

    def __init__(self, data):
        self.data = data

        self.distances = self.create_distance_matrix()

        self.graph = nx.Graph()

        for i in range(0, data.size):
            self.graph.add_node(data.ids[i],
                                coordinates=data.coordinates[i],
                                demands=data.demands[i],
                                time_windows=data.time_windows[i],
                                service_times=data.service_times[i])

    def create_distance_matrix(self):

        zeros = np.zeros((self.data.size, self.data.size))

        for i in range(0, self.data.size):
            for j in range(i+1, self.data.size):

                zeros[i][j] = euclidean_distance(self.data.coordinates[i], self.data.coordinates[j])
                zeros[j][i] = zeros[i][j]

        return zeros

    def get_clients_ids(self):
        return self.data.ids[1:]

    def get_depo_ids(self):
        return [self.data.ids[0]]

    def duplicate_depo(self):  # Zakładając, że depo jest pierwszym rekordem w danych wejściowych.

        self.data.size = self.data.size + 1

        max_client_id = max(self.data.ids) + 1

        self.data.ids.append(max_client_id)
        self.data.coordinates.append(self.data.coordinates[0])
        self.data.demands.append(self.data.demands[0])
        self.data.time_windows.append(self.data.time_windows[0])
        self.data.service_times.append(self.data.service_times[0])


class Data:

    def __init__(self, input_file_name):

        self.size = None
        self.ids = []
        self.ids_data = []
        self.coordinates = []
        self.demands = []
        self.time_windows = []
        self.service_times = []

        self.setup_data_model(input_file_name, "temp.txt")

    def __str__(self):

        return_me = ""

        return_me += "Size: " + str(self.size) + "\n"
        return_me += "IDs: " + str(self.ids) + "\n"
        return_me += "Coordinates: " + str(self.coordinates) + "\n"
        return_me += "Demands: " + str(self.demands) + "\n"
        return_me += "Time Windows: " + str(self.time_windows) + "\n"
        return_me += "Service Times " + str(self.service_times) + "\n"

        return return_me

    def setup_data_model(self, raw_input_file, output_file_path):

        def get_raw_data():

            with open(raw_input_file, "r") as fin, open(output_file_path, "w+") as fout:
                fin.readline()

                for line in fin:
                    fout.write(re.sub(r'\s+', ' ', line).strip() + "\n")

            return_me = []

            with open(output_file_path, "r") as fin:
                for line in fin:
                    splited = list(map(float, line.split()))
                    return_me.append(splited)

                return return_me

        raw_data = get_raw_data()

        for i in range(0, len(raw_data)):

            self.size = len(raw_data)

            self.ids_data.append(int(raw_data[i][0]))

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




