from services.calculate import manhattan_distance
import re
import numpy as np

def clean_input_file(input_file_path, output_file_path):
    fin = open(input_file_path, "r")
    fout = open(output_file_path, "w+")

    fin.readline()

    for line in fin:

        fout.write(re.sub(r'\s+', ' ', line).strip() + "\n")


def get_data_model(data_file_path):

    def get_raw_data():

        return_me = []

        fin = open(data_file_path)

        for line in fin:
            splited = list(map(float, line.split()))
            return_me.append(splited)

        fin.close()
        return return_me

    data = {}

    raw_data = get_raw_data()

    ids = []
    coordinates = []
    distances = np.zeros((len(raw_data), len(raw_data)))
    demands = []
    time_windows = []
    service_times = []

    for i in range(0, len(raw_data)):

        ids.append(int(raw_data[i][0]))

        coordinates.append((raw_data[i][1], raw_data[i][2]))

        for j in range(i+1, len(raw_data)):
            distances[i, j] = manhattan_distance(raw_data[i][1:3], raw_data[j][1:3])
            distances[j, i] = distances[i, j]

        demands.append(int(raw_data[i][3]))

        time_windows.append((raw_data[i][4], raw_data[i][5]))

        service_times.append(raw_data[i][6])


    data["ids"] = ids
    data["coordinates"] = coordinates
    data["distances"] = distances
    data["demands"] = demands
    data["time_windows"] = time_windows
    data["service_times"] = service_times
    return data