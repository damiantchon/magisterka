import numpy as np
from scipy.spatial import distance

def manhattan_distance(x, y):
    return sum(abs(a-b) for a,b in zip(x,y))

def euclidean_distance(x, y):
    return round(distance.euclidean(x, y), 2)

def nearest_neighbors_vrptw(vrptw): # greedy greedy - tylko sprawdzane czy dojdę

    to_visit = []
    visited = []


    # prepeare "to_visit"
    for i in range(1, vrptw.size):
        to_visit.append(vrptw.ids[i])

    routes = []
    total_lenght = 0

    depo = 0

    vehicles_count = 0

    # main loop
    while to_visit:

        vehicles_count = vehicles_count + 1

        current_capacity = vrptw.vehicle_capacity

        route_length = 0

        time = 0

        current_city = 0

        current_route = [0]

        done = False

        while not done:

            fesible = []
            closest_fesible = {}

            for city in to_visit:
                distance = vrptw.distances[current_city][city]
                if time + distance <= vrptw.time_windows[city][1] \
                        and time + distance + vrptw.service_times[city] + vrptw.distances[city][depo] <= vrptw.time_windows[depo][1]\
                        and current_capacity - vrptw.demands[city] >= 0:
                    # dojadę przed końcem okna czasowego i po obsłudze zdążę wrócić do depo

                    fesible.append((city, distance))

            if fesible:
                closest_fesible["city"], closest_fesible["length"] = min(fesible, key=lambda f: f[1])
            else:
                closest_fesible["city"], closest_fesible["length"] = (0, vrptw.distances[current_city][depo])
                done = True

            # Dodajemy closest i zdejmujemy z listy to_visit
            current_route.append(closest_fesible["city"])
            if closest_fesible["city"] != depo:
                to_visit.remove(closest_fesible["city"])
            route_length += closest_fesible["length"]

            # Przesuwamy pojazd do następnego miasta i ustalamy czas po obsłudze
            current_city = closest_fesible["city"]
            current_capacity -= vrptw.demands[closest_fesible["city"]]

            if time + closest_fesible["length"] < vrptw.time_windows[current_city][0]:
                # Sytuacja z czekaniem na obsługę (przyjechaliśmy za wcześnie
                time = vrptw.time_windows[current_city][0] + vrptw.service_times[current_city]
            else:
                # Sytuacja normalna - dojeżdzamy w oknie czasowym
                time = time + closest_fesible["length"] + vrptw.service_times[current_city]

            print("Current City:", current_city)
            print("To visit:", to_visit)
            print("Route length:", route_length)
            print("Fesible", fesible)
            print("")

        total_lenght += route_length

        routes.append(current_route)

    solution = {"length": total_lenght, "vehicles": vehicles_count, "routes": routes}

    print(solution)

    return solution



