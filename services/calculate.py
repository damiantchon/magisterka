from scipy.spatial import distance


def manhattan_distance(x, y):
    return sum(abs(a-b) for a,b in zip(x,y))


def euclidean_distance(x, y):
    return distance.euclidean(x, y)  #round(distance.euclidean(x, y), 2)


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

        load = 0

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
                        and max(time + distance, vrptw.time_windows[city][0]) + vrptw.service_times[city] + vrptw.distances[city][depo] <= vrptw.time_windows[depo][1]\
                        and load + vrptw.demands[city] <= vrptw.vehicle_capacity:
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
            load = load + vrptw.demands[closest_fesible["city"]]

            time = max(vrptw.time_windows[current_city][0] + vrptw.service_times[current_city],
                       time + closest_fesible["length"] + vrptw.service_times[current_city])

        total_lenght += route_length

        routes.append(current_route)

    solution = {"length": total_lenght, "vehicles": vehicles_count, "routes": routes}

    print(solution)

    return solution


def nearest_neighbors_vrptw_vei(vrptw, v): # greedy greedy - tylko sprawdzane czy dojdę

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
    while to_visit and vehicles_count < v:

        vehicles_count = vehicles_count + 1

        load = 0

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
                        and max(time + distance, vrptw.time_windows[city][0]) + vrptw.service_times[city] + vrptw.distances[city][depo] <= vrptw.time_windows[depo][1]\
                        and load + vrptw.demands[city] <= vrptw.vehicle_capacity:
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
            load = load + vrptw.demands[closest_fesible["city"]]

            time = max(vrptw.time_windows[current_city][0] + vrptw.service_times[current_city],
                       time + closest_fesible["length"] + vrptw.service_times[current_city])

        total_lenght += route_length

        routes.append(current_route)

    solution = {"length": total_lenght, "vehicles": vehicles_count, "routes": routes}

    print(solution)

    return solution


def check_feasibility(vrptw, routes): #TODO zoptymalizować

    for route in routes:

        time = 0
        load = 0

        for i in range(0, len(route)-1):
            if time + vrptw.distances[route[i]][route[i+1]] > vrptw.time_windows[route[i+1]][1]:
                return False
            else:
                time = max(time + vrptw.distances[route[i]][route[i+1]] + vrptw.service_times[i+1],
                           vrptw.time_windows[route[i+1]][0] + vrptw.service_times[route[i+1]])
                load = load + vrptw.demands[route[i+1]]

        if load > vrptw.vehicle_capacity:
            return False

    return True


def check_solution_feasibility(vrptw, routes): #TODO zoptymalizować

    visited = []
    for route in routes:
        for city in route:
            visited.append(city)

    if list(set(vrptw.ids) - set(visited)):
        return False


    for route in routes:

        time = 0
        load = 0

        for i in range(0, len(route)-1):
            if time + vrptw.distances[route[i]][route[i+1]] > vrptw.time_windows[route[i+1]][1]:
                return False
            else:
                time = max(time + vrptw.distances[route[i]][route[i+1]] + vrptw.service_times[i+1],
                           vrptw.time_windows[route[i+1]][0] + vrptw.service_times[route[i+1]])
                load = load + vrptw.demands[route[i+1]]

        if load > vrptw.vehicle_capacity:
            return False

    return True


def check_feasibility_prime(vrptw, route, Xi_Xpi, d_table): # Zoptymalizowana versja "check_feasibility

    if (Xi_Xpi[0] >= 0):
        time = d_table.get(str(route[Xi_Xpi[0]]) + "_" + str(route[Xi_Xpi[1]]))["time"]
        load = d_table.get(str(route[Xi_Xpi[0]]) + "_" + str(route[Xi_Xpi[1]]))["load"]
    else:
        time = 0
        load = 0

    for i in range(Xi_Xpi[1], len(route)-1):
        if time + vrptw.distances[route[i]][route[i + 1]] > vrptw.time_windows[route[i + 1]][1]:
            return False
        else:
            time = max(time + vrptw.distances[route[i]][route[i + 1]] + vrptw.service_times[route[i + 1]],
                       vrptw.time_windows[route[i + 1]][0] + vrptw.service_times[route[i + 1]])
            load = load + vrptw.demands[route[i + 1]]
    # print("LOAD:", load," (ROUTE", route, ")")
    if load > vrptw.vehicle_capacity:
        return False

    return True


def check_feasibility_bis(vrptw, route, last_y2, d_table):
    is_feasible = False
    if last_y2 is None:
        last_y2 = {"index": 0, "time": 0, "load": 0}

        # for i in range()

    return is_feasible, last_y2


def create_auxiliary_dict(vrptw, routes):
    table = {}

    for route in routes:
        time = 0
        load = 0

        for i in range(0, len(route)-1):
            start = route[i]
            stop = route[i+1]

            # time and load
            time = max(time + vrptw.distances[start][stop], vrptw.time_windows[stop][0]) + vrptw.service_times[stop]
            load = load + vrptw.demands[stop]
            table[str(start) + "_" + str(stop)] = {"time": time , "load": load}

            # maximum lateness
            route_latenesses = []

            windows = vrptw.time_windows
            services = vrptw.service_times
            distances = vrptw.distances

            r = route

            l_time = 0
            basic_lateness = 0

            l_time = windows[r[i + 1]][1]  # 15
            basic_lateness = windows[r[i + 1]][1] - windows[r[i + 1]][0]

            route_latenesses.append(basic_lateness)  # (1, 5)
            print("Basic lateness:", basic_lateness)


            for j in range(i + 1, len(route)-1):

                l_time += services[r[j]] + distances[r[j]][r[j+1]]
                print("J:", j)
                print("B_lateness:", basic_lateness)
                print("Windows[1]", windows[r[j+1]][1])
                print("L_time:", l_time)
                print(basic_lateness + (windows[r[j+1]][1] - l_time))
                route_latenesses.append(basic_lateness + (windows[r[j+1]][1] - l_time))

            # l_time += services[r[len(r)-2]] + distances[r[len(r)-2]][r[len(r)-1]]
            # route_latenesses.append(basic_lateness + (windows[len(r)-1][1] - l_time))

            table[str(start) + "_" + str(stop)]["lateness"] = min(route_latenesses)



        # fill load_to_go
        table[str(route[len(route)-2]) + "_" + str(route[len(route)-1])]["load_to_go"] = 0
        load_to_go = 0

        for i in reversed(range(0, len(route) - 2)):

            start = route[i]
            stop = route[i + 1]

            # "load to go" (how much more load do we need to finish this road from given city)
            load_to_go = load_to_go + vrptw.demands[route[i+2]]

            table[str(start) + "_" + str(stop)]["load_to_go"] = load_to_go

    return table


def update_departure_table(vrptw, routes, t):

    for route in routes:
        time = 0
        load = 0
        for i in range(0, len(route)-1):
            start = route[i]
            stop = route[i+1]

            time = max(time + vrptw.distances[start][stop], vrptw.time_windows[stop][0]) + vrptw.service_times[stop]
            load = load + vrptw.demands[stop]
            t[start][stop] = (time, load)

    return t


def routes_length(vrptw, routes):
    length = 0
    for route in routes:
        for i in range(0, len(route)-1):
            length += vrptw.distances[route[i]][route[i+1]]

    return round(length, 2) # int(length*(10**2))/(10.**2)


def local_search_clean(vrptw, solution):

    def calculate_delta(X1i, X2i, Y1i, Y2i, r1, r2):
        delta = 0

        dist = vrptw.distances

        if X1i == Y1i and X2i == Y2i:
            delta = dist[r1[X1i]][r2[X2i + 1]] + dist[r2[X2i]][r1[X1i + 1]] - \
                    (dist[r1[X1i]][r1[X1i + 1]] + dist[r2[X2i]][r2[X2i + 1]])

        elif X1i != Y1i and X2i != Y2i:
            delta = dist[r1[X1i]][r2[X2i + 1]] + dist[r2[Y2i]][r1[Y1i + 1]] + dist[r2[X2i]][r1[X1i + 1]] + dist[r1[Y1i]][r2[Y2i + 1]] - \
                    (dist[r1[X1i]][r1[X1i + 1]] + dist[r1[Y1i]][r1[Y1i + 1]] + dist[r2[X2i]][r2[X2i + 1]] + dist[r2[Y2i]][r2[Y2i + 1]])

        elif X1i == Y1i and X2i != Y2i:
            delta = dist[r2[X2i]][r2[Y2i + 1]] + dist[r1[X1i]][r2[X2i + 1]] + dist[r2[Y2i]][r1[Y1i + 1]] - \
                    (dist[r2[X2i]][r2[X2i + 1]] + dist[r2[Y2i]][r2[Y2i + 1]] + dist[r1[X1i]][r1[X1i + 1]])

        elif X1i != Y1i and X2i == Y2i:
            delta = dist[r1[X1i]][r1[Y1i + 1]] + dist[r2[X2i]][r1[X1i + 1]] + dist[r1[Y1i]][r2[Y2i + 1]] - \
                    (dist[r1[X1i]][r1[X1i + 1]] + dist[r1[Y1i]][r1[Y1i + 1]] + dist[r2[X2i]][r2[X2i + 1]])

        return delta

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

    def local_search_single(first_route, second_route, d_table):


        first_best = first_route
        second_best = second_route

        global best_len
        best_len = 0 #routes_length(vrptw, [first_route, second_route])

        last_y2 = {}
        last_y2["index"] = None
        last_y2["departure"] = None
        last_y2["load"] = None

        for X1_index, X1 in enumerate(first_route[:-1]):
            dlugosci_X2 = []
            for X2_index, X2 in enumerate(second_route[:-1]):
                best_X2 = 999999999999
                for Y1_index, Y1 in enumerate(first_route[X1_index:-1], X1_index):
                    dlugosci_Y2 = []
                    for Y2_index, Y2 in enumerate(second_route[X2_index:-1], X2_index):

                        # swaperooni
                        if X1_index == Y1_index and X2_index == Y2_index:

                            temp = first_route[:X1_index + 1] + second_route[Y2_index + 1:]
                            temp_second = second_route[:X2_index + 1] + first_route[Y1_index + 1:]
                            temp_first = temp

                        else:

                            temp_first, temp_second = swap_edges(first_route, second_route, X1_index + 1, X2_index + 1,
                                                                 Y1_index + 1, Y2_index + 1)


                        #TODO Zoptymalizować liczenie (constant time - do starego Y2prime dodać nowy Y2prime i dalej
                        #TODO propagować, zamiast liczenia trasy od zera

                        # if X2_index == Y2_index:
                        #     if check_feasibility_prime(vrptw, temp_first, (X1_index - 1, X1_index), d_table) is False:
                        #         break
                        if X2_index != Y2_index:
                            if last_y2["index"] is None:
                                is_feasible, last_y2 = check_feasibility_bis(vrptw=vrptw, route=temp_first, last_y2=None, d_table=d_table)

                            else:
                                is_feasible, last_y2 = check_feasibility_bis(vrptw=vrptw, route=temp_first, last_y2=last_y2, d_table=d_table)


                        #TODO Koniec optymalizacji zamiast
                        if check_feasibility_prime(vrptw, temp_first, (X1_index - 1, X1_index), d_table) is False:
                            break
                        #TODO Koniec zamiast :)

                        swaperooni_len = calculate_delta(X1_index,X2_index,Y1_index,Y2_index,r1=first_route,r2=second_route) #routes_length(vrptw, [temp_first, temp_second])

                        if swaperooni_len < best_X2:
                            best_X2 = swaperooni_len

                        dlugosci_Y2.append(swaperooni_len)

                        if len(dlugosci_Y2) == 3:
                            if dlugosci_Y2[2] > dlugosci_Y2[1] > dlugosci_Y2[0]: # or (dlugosci_Y2[2] > best_len and dlugosci_Y2[1] > best_len and dlugosci_Y2[0] > best_len):

                                dlugosci_Y2.clear()
                                break
                            else:
                                dlugosci_Y2.pop(0)

                        if swaperooni_len < best_len:
                            # if check_fisibility(vrptw, [temp_second]):
                            if check_feasibility_prime(vrptw, temp_second, (X2_index - 1, X2_index), d_table):

                                best_len = swaperooni_len

                                first_best = temp_first

                                second_best = temp_second

                                # d_table = update_departure_table(vrptw, [first_best, second_best], d_table)

                dlugosci_X2.append(best_X2)

                if len(dlugosci_X2) == 3:
                    if dlugosci_X2[2] > dlugosci_X2[1] > dlugosci_X2[0]: # or (dlugosci_X2[2] > best_len and dlugosci_X2[1] > best_len and dlugosci_X2[0] > best_len):

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
            departure_table = create_auxiliary_dict(vrptw, solution["routes"])
            # sprawdzenie czy któraś z optymalizowanych dróg nie jest już pusta
            if solution["routes"][i] is not [0, 0] and solution["routes"][j] is not [0, 0]:
                solution["routes"][i], solution["routes"][j] = \
                    local_search_single(solution["routes"][i], solution["routes"][j], departure_table)

    # aktualizacja rozwiązania
    print(update_solution(solution))
    return update_solution(solution)




