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


def check_fisibility(vrptw, routes):

    for route in routes:

        time = 0
        load = 0

        for i in range(0, len(route)-1):
            if time + vrptw.distances[route[i]][route[i+1]] > vrptw.time_windows[route[i+1]][1]:
                return False
            elif time + vrptw.distances[route[i]][route[i+1]] > vrptw.time_windows[route[i+1]][0]:
                time = time + vrptw.distances[route[i]][route[i+1]] + vrptw.service_times[i+1]
                load = load + vrptw.demands[route[i+1]]
            else:
                time = vrptw.time_windows[route[i+1]][0] + vrptw.service_times[route[i+1]]
                load = load + vrptw.demands[route[i+1]]

        if load > vrptw.vehicle_capacity:
            return False

    return True


def routes_length(vrptw, routes):
    length = 0
    for route in routes:
        for i in range(0, len(route)-1):
            length += vrptw.distances[route[i]][route[i+1]]

    return round(length, 2)


def local_search(vrptw, first_route, second_route, total, better):
    i = 0

    def swap_edges(route1, route2, X1pi, X2pi, Y1pi, Y2pi):

        temp_r1 = []
        temp_r2 = []

        temp_r1 += route1[:X1pi]
        temp_r1 += route2[X2pi:Y2pi]
        temp_r1 += route1[Y1pi:]

        temp_r2 += route2[:X2pi]
        temp_r2 += route1[X1pi:Y1pi]
        temp_r2 += route2[Y2pi:]

        return temp_r1, temp_r2

    test = []
    test_set = []

    temp_first = []
    temp_second = []

    first_best = first_route
    second_best = second_route

    oryg_len = routes_length(vrptw, [first_route, second_route])
    global best_len
    best_len = routes_length(vrptw, [first_route, second_route])


    for X1_index, X1 in enumerate(first_route[:-1]):
        dlugosci_X2 = []
        for X2_index, X2 in enumerate(second_route[:-1]):
            best_X2 = 99999999
            for Y1_index, Y1 in enumerate(first_route[X1_index:-1], X1_index):
                dlugosci_Y2 = []
                for Y2_index, Y2 in enumerate(second_route[X2_index:-1], X2_index):

                    i += 1

                    #  swaperooni:
                    if X1_index == Y1_index and X2_index == Y2_index:

                        temp = first_route[:X1_index+1] + second_route[Y2_index+1:]
                        temp_second = second_route[:X2_index+1] + first_route[Y1_index+1:]
                        temp_first = temp

                        test.append(len(temp_first) + len(temp_second))
                        test_set.append(len(set(temp_first)) + len(set(temp_second)))

                    else:

                        temp_first, temp_second = swap_edges(first_route, second_route, X1_index+1, X2_index+1, Y1_index+1, Y2_index+1)

                        test.append(len(temp_first) + len(temp_second))
                        test_set.append(len(set(temp_first)) + len(set(temp_second)))

                    swaperooni_len = routes_length(vrptw, [temp_first, temp_second])

                    if swaperooni_len < best_X2:
                        best_X2 = swaperooni_len


                    dlugosci_Y2.append(routes_length(vrptw, [temp_first, temp_second]))

                    if len(dlugosci_Y2) == 3:
                        if dlugosci_Y2[2] > dlugosci_Y2[1] > dlugosci_Y2[0]:

                            dlugosci_Y2.clear()
                            break
                        else:
                            dlugosci_Y2.pop(0)


                    if check_fisibility(vrptw, [temp_first]) is False:
                        break



                    total += 1
                    if swaperooni_len < best_len:
                        if check_fisibility(vrptw, [temp_first, temp_second]):
                            better += 1
                            # print("Indexes: X1:", X1_index, "Y1:", Y1_index, "X2:", X2_index, "Y2:", Y2_index)
                            # print(swaperooni_len, "<", best_len)
                            # print(first_route)
                            # print(temp_first)
                            # print(second_route)
                            # print(temp_second)

                            best_len = swaperooni_len

                            first_best = temp_first
                            second_best = temp_second

            dlugosci_X2.append(best_X2)

            if len(dlugosci_X2) == 3:
                if dlugosci_X2[2] > dlugosci_X2[1] > dlugosci_X2[0]:
                    # print(dlugosci_X2)
                    dlugosci_X2.clear()
                    break
                else:
                    dlugosci_X2.pop(0)

    first_route = first_best
    second_route = second_best

    # print("Test:", test)
    # print("Test set:", test_set)



    return total, better, first_best, second_best


def local_search_clean(vrptw, solution):

    def swap_edges(route1, route2, X1pi, X2pi, Y1pi, Y2pi):

        temp_r1 = []
        temp_r2 = []

        temp_r1 += route1[:X1pi]
        temp_r1 += route2[X2pi:Y2pi]
        temp_r1 += route1[Y1pi:]

        temp_r2 += route2[:X2pi]
        temp_r2 += route1[X1pi:Y1pi]
        temp_r2 += route2[Y2pi:]

        return temp_r1, temp_r2

    def local_search_single(first_route, second_route):

        first_best = first_route
        second_best = second_route

        global best_len
        best_len = routes_length(vrptw, [first_route, second_route])

        for X1_index, X1 in enumerate(first_route[:-1]):
            dlugosci_X2 = []
            for X2_index, X2 in enumerate(second_route[:-1]):
                best_X2 = 999999999999
                for Y1_index, Y1 in enumerate(first_route[X1_index:-1], X1_index):
                    dlugosci_Y2 = []
                    for Y2_index, Y2 in enumerate(second_route[X2_index:-1], X2_index):

                        #  swaperooni:
                        if X1_index == Y1_index and X2_index == Y2_index:

                            temp = first_route[:X1_index + 1] + second_route[Y2_index + 1:]
                            temp_second = second_route[:X2_index + 1] + first_route[Y1_index + 1:]
                            temp_first = temp

                        else:

                            temp_first, temp_second = swap_edges(first_route, second_route, X1_index + 1, X2_index + 1,
                                                                 Y1_index + 1, Y2_index + 1)


                        swaperooni_len = routes_length(vrptw, [temp_first, temp_second])

                        if swaperooni_len < best_X2:
                            best_X2 = swaperooni_len

                        dlugosci_Y2.append(routes_length(vrptw, [temp_first, temp_second]))

                        if len(dlugosci_Y2) == 3:
                            if dlugosci_Y2[2] > dlugosci_Y2[1] > dlugosci_Y2[0]:

                                dlugosci_Y2.clear()
                                break
                            else:
                                dlugosci_Y2.pop(0)

                        if check_fisibility(vrptw, [temp_first]) is False:
                            break

                        if swaperooni_len < best_len:
                            if check_fisibility(vrptw, [temp_first, temp_second]):

                                best_len = swaperooni_len

                                first_best = temp_first

                                second_best = temp_second

                dlugosci_X2.append(best_X2)

                if len(dlugosci_X2) == 3:
                    if dlugosci_X2[2] > dlugosci_X2[1] > dlugosci_X2[0]:

                        dlugosci_X2.clear()
                        break
                    else:
                        dlugosci_X2.pop(0)

        return first_best, second_best

    def update_solution(solution_to_update):

        updated_solution = {"length": 0,
                            "vehicles": 0,
                            "routes": list(filter(([0, 0]).__ne__, solution_to_update["routes"]))}

        updated_solution["length"] = routes_length(vrptw, solution_to_update["routes"])
        updated_solution["vehicles"] = len(updated_solution["routes"])

        return updated_solution

    # main loop
    for i in range(0, len(solution["routes"])-1):
        for j in range(i+1, len(solution["routes"])):
            # sprawdzenie czy któraś z optymalizowanych dróg nie jest już pusta
            if solution["routes"][i] is not [0, 0] and solution["routes"][j] is not [0, 0]:
                solution["routes"][i], solution["routes"][j] = \
                    local_search_single(solution["routes"][i], solution["routes"][j])

    # aktualizacja rozwiązania

    return update_solution(solution)




