from services.calculate import nearest_neighbors_vrptw, CROSS_exchange_LS
from queue import Full, Empty
import time
import os
from profilehooks import profile
from data import VRPTW_MACS_DS, ParsedData, VRPTW
import numpy as np
import random
from services.calculate import routes_length, check_solution_feasibility, run_2opt


class MACS_VRPTW(): #Multiple Ant Colony System for Vehicle Routing Problems With Time Windows

    def __init__(self, vrptw, m, beta, tau0, q0, p, verbose=False): #jeśli tau0 , m - liczba mrówek, q0 - exploitation vs exploration

        self.vrptw = vrptw
        self.m = m
        self.beta = beta
        self.tau0 = tau0
        self.q0 = q0
        self.p = p

        self.verbose = verbose

        self.hashes = {}

        self.starting_time = 0
        self.search_duration = 0


        self.pheromones_TIME = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j
        self.pheromones_VEI = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j

    def get_solution_hash(self, solution):

        hashes = []

        for route in solution["routes"]:
            hashes.append(hash(tuple(route)))

        hashes.sort()

        final_hash = hash(tuple(hashes))

        return final_hash

    def new_active_ant(self, local_search, IN, macs_ds, pheromones):

        def get_feasible_cities(with_depos):

            # set all to not fesible if there is "no depo to go back to"
            if not list(set(cities_to_visit).intersection(macs_ds.depo_ids)):
                return []

            fesible = []
            temp_cities_to_visit = cities_to_visit.copy()
            if with_depos == False:
                temp_cities_to_visit = list(set(temp_cities_to_visit) - set(macs_ds.depo_ids))

            for city in temp_cities_to_visit:
                if current_time + macs_ds.distances[current_location][city] <= macs_ds.time_windows[city][1] \
                    and max(current_time + macs_ds.distances[current_location][city], macs_ds.time_windows[city][0]) + \
                    macs_ds.service_times[city] + macs_ds.distances[city][0] <= macs_ds.time_windows[0][1] \
                    and load + macs_ds.demands[city] <= macs_ds.vehicle_capacity:

                    fesible.append(city)
            return fesible

        def get_next_location(pheromones, attractiveness):
            pher_x_atract_B = []

            for ct in feasible_cities:
                pher_x_atract_B.append((ct, pheromones[current_location][ct] * pow(attractiveness[current_location][ct], self.beta)))

            pher_x_atract_B_sum = sum(n for _, n in pher_x_atract_B)

            if random.random() < self.q0: # exploitation
                return max(pher_x_atract_B ,key=lambda x:x[1])[0]

            else:   # exploration
                cities_and_probabilities = []
                for elem in pher_x_atract_B:
                    cities_and_probabilities.append((elem[0], elem[1]/pher_x_atract_B_sum))

                cities = [i[0] for i in cities_and_probabilities]
                probabilities = [i[1] for i in cities_and_probabilities]

                return np.random.choice(a=cities, p=probabilities)

        def insertion_procedure(tour, non_visited):

            def decode_tour(tour):

                temp_tour = tour.copy()

                depos = []
                for n, i in enumerate(temp_tour):
                    if i in macs_ds.depo_ids:
                        depos.append(tour[n])
                        temp_tour[n] = 0

                temp_tour.pop(0) # get rid of first depo
                decoded_tours = []

                single_ride = [0]
                for n, i in enumerate(temp_tour):
                    if i is not 0:
                        single_ride.append(i)
                    else:
                        single_ride.append(0)
                        decoded_tours.append(single_ride)

                        single_ride = [0]

                return decoded_tours

            def append_demands(decoded_tour):

                demands = []
                for ride in decoded_tour:
                    demand = 0
                    for city in ride:
                        demand = demand + macs_ds.demands[city]
                    demands.append(demand)

                tours_demands_dict = []
                tours_demands_dict = list(zip(decoded_tour, demands))
                return tours_demands_dict

            def is_fesible(route):
                time = 0

                for i in range(0, len(route) - 1):

                    time_after = time + macs_ds.distances[route[i]][route[i + 1]]

                    if time_after <= macs_ds.time_windows[route[i+1]][1]:

                        time = max(time_after, macs_ds.time_windows[route[i+1]][0]) + macs_ds.service_times[route[i+1]]
                    else:
                        return False

                if time + macs_ds.distances[route[len(route)-1]][0] > macs_ds.time_windows[0][1]:
                    return False
                else:
                    return True

            def feasible_after_insertion(route, time):

                if time + macs_ds.distances[route[len(route)-3]][route[len(route)-2]] > macs_ds.time_windows[route[len(route)-2]][1]:
                    return False
                else:
                    time = max(time + macs_ds.distances[route[len(route)-3]][route[len(route)-2]], macs_ds.time_windows[route[len(route)-2]][0])
                    time = time + macs_ds.service_times[route[len(route)-2]]
                    if time + macs_ds.distances[route[len(route)-1]][0] > macs_ds.time_windows[0][1]:
                        return False
                return True

            def get_last_customer_time(route):
                time = 0

                for i in range(0, len(route) - 1):
                    time = max(time + macs_ds.distances[route[i]][route[i + 1]],
                               macs_ds.time_windows[route[i + 1]][0])
                    time = time + macs_ds.service_times[route[i + 1]]

                return time

            def update_last_customer_time(route, time):
                time = max(time + macs_ds.distances[route[len(route) - 3]][route[len(route) - 2]],
                           macs_ds.time_windows[route[len(route) - 2]][0])
                time = time + macs_ds.service_times[route[len(route) - 2]]
                return time

            def route_length(route):
                length = 0

                for i in range(0, len(route) - 1):
                    length += macs_ds.distances[route[i]][route[i + 1]]

                return round(length, 2)


            # divide tour into list of single vehicle rides
            decoded_tour = decode_tour(tour)

            tours_with_demands = append_demands(decoded_tour)

            # create list of non_visited sorted by delivery quantities (tuple (id, quantity))
            non_visited = set(non_visited) - set(macs_ds.depo_ids) #  remove all depos from not visited (just to be sure)

            nv_w_demands = []

            for ct in non_visited:
                nv_w_demands.append((ct, macs_ds.demands[ct]))

            nv_w_demands = sorted(nv_w_demands, key=lambda x: x[1], reverse=True)


            for city_w_demand in nv_w_demands:

                posible_inserts = [] #  list of tuples (tour_id, insertion_point, distance)

                for tour_id, t in enumerate(tours_with_demands):

                    if t[1] + city_w_demand[1] <= macs_ds.vehicle_capacity: # check if demand did not exceed vehicle_capacity
                        route = t[0].copy()

                        for n, city in enumerate(t[0][1:], 1):

                            route.insert(n, city_w_demand[0])

                            if is_fesible(route):
                                posible_inserts.append((tour_id, n, route_length(route)))
                                route.remove(city_w_demand[0])
                            else:
                                route.remove(city_w_demand[0])

                if posible_inserts:
                    best = min(posible_inserts, key=lambda x: x[2])
                    tours_with_demands[best[0]][0].insert(best[1], city_w_demand[0])
                    cities_to_visit.remove(city_w_demand[0])

            solution = {}
            solution["length"] = 0
            solution["vehicles"] = 0
            solution["routes"] = [x[0] for x in tours_with_demands]
            solution["length"] = routes_length(macs_ds, solution["routes"])
            solution["vehicles"] = len(solution["routes"])

            return solution

        current_location = macs_ds.get_random_depo()
        current_time = 0
        load = 0
        tour = [current_location]

        # initialization
        cities_to_visit = macs_ds.ids.copy()
        cities_to_visit.remove(current_location)

        feasible_cities = get_feasible_cities(with_depos=False)

        while feasible_cities:

            attractiveness = self.create_attractiveness_array(IN, current_location, current_time, feasible_cities, macs_ds)

            next_location = get_next_location(pheromones=pheromones, attractiveness=attractiveness)# TODO - wybra następną lokację na podstawie (Equation 1)
            tour.append(next_location)
            current_time = max(current_time + macs_ds.distances[current_location][next_location], macs_ds.time_windows[next_location][0])\
                           + macs_ds.service_times[next_location]
            load = load + macs_ds.demands[next_location]

            cities_to_visit.remove(next_location)

            if next_location in macs_ds.depo_ids:
                current_time = 0
                load = 0

            #Local pheromone update
            pheromones[current_location][next_location] = \
                ((1-self.p) * pheromones[current_location][next_location]) + (self.p*self.tau0)

            current_location = next_location

            if current_location in macs_ds.depo_ids:
                feasible_cities = get_feasible_cities(with_depos=False)
            else:
                feasible_cities = get_feasible_cities(with_depos=True)

        solution = insertion_procedure(tour=tour, non_visited=cities_to_visit)

        if list(set(cities_to_visit) - set(macs_ds.depo_ids)):
            feasible = False
        else:
            feasible = True

        if local_search and feasible:

            solution = self.cross_exchange(macs_ds, solution)

        return solution

    def cross_exchange(self, macs_ds, solution):
        last_solution_length = solution["length"]
        solution = CROSS_exchange_LS(macs_ds, solution)
        while (last_solution_length > solution["length"]):
            last_solution_length = solution["length"]
            solution = CROSS_exchange_LS(macs_ds, solution)
        if self.verbose:
            print(os.getpid(), solution)
        return solution

    def create_attractiveness_array(self, IN, current_location, current_time, feasible_cities, macs_ds):
        attractiveness = np.zeros((macs_ds.size, macs_ds.size))
        for city in feasible_cities:
            delivery_time = max(current_time + macs_ds.distances[current_location][city], macs_ds.time_windows[city][0])
            delta_time = delivery_time - current_time
            distance = delta_time * (macs_ds.time_windows[city][1] - current_time)
            if IN != 0:
                distance = max(1, distance - IN[city])
            else:
                distance = max(1, distance)

            attractiveness[current_location][city] = 1.0 / distance
        return attractiveness

    def ACS_VEI(self, v, best_solution, stop_time, queue, vei_time_queue):
        if self.verbose:
            print("ACS_VEI v =", v)

        macs_ds = VRPTW_MACS_DS(self.vrptw, v)
        self.pheromones_VEI = self.initialize_pheromones(macs_ds.size, best_solution)

        best_VEI_solution = nearest_neighbors_vrptw(vrptw=self.vrptw, v=v)

        IN = [0] * macs_ds.size

        while stop_time > time.time():

            kth_solutions = []
            for k in range(0, self.m):

                solution = self.new_active_ant(local_search=False, IN=IN, macs_ds=macs_ds, pheromones=self.pheromones_VEI)

                for customer in list(set(self.vrptw.ids) - set(self.get_customers(solution) + [0])):
                    IN[customer] = IN[customer] + 1

                kth_solutions.append(solution)

            best_colony_solution = self.get_best_solution_VEI(kth_solutions)

            if self.count_customers(best_colony_solution) > self.count_customers(best_VEI_solution):
                best_VEI_solution = best_colony_solution
                IN = [0] * macs_ds.size
                if self.verbose:
                    print("CHECKING FEASIBILITY OF (len{})".format(self.count_customers(best_VEI_solution)), best_VEI_solution)
                if check_solution_feasibility(self.vrptw, best_VEI_solution["routes"]):
                    queue.put([best_VEI_solution, "ACS-VEI"])
                    if self.verbose:
                        print("FEASIBLE!")
            self.pheromones_VEI = self.update_pheromones(macs_ds, best_VEI_solution, self.pheromones_VEI, best_VEI_solution, IN=IN)

            try:
                best_solution = vei_time_queue.get_nowait()
                if self.verbose:
                    print("VEI's NEW BEST SOLUTION is", best_solution)
            except Empty:
                pass
            self.pheromones_VEI = self.update_pheromones(macs_ds, best_solution, self.pheromones_VEI, best_solution, IN=IN)

    def ACS_TIME(self, v, best_solution, start_time, stop_time, queue, vei_time_queue):

        if self.verbose:
            print("ACS_TIME v =", v)

        macs_ds = VRPTW_MACS_DS(self.vrptw, v)

        self.pheromones_TIME = self.initialize_pheromones(macs_ds.size, best_solution)

        while stop_time > time.time():
            if self.verbose:
                print("BEST SOLUTION V: {}, LEN: {}181".format(best_solution["vehicles"], best_solution["length"]))

            kth_solutions = []

            for k in range(0, self.m):
                if not stop_time > time.time():
                    break
                else:
                     kth_solutions.append(self.new_active_ant(local_search=True, IN=0, macs_ds=macs_ds, pheromones=self.pheromones_TIME))


            best_TIME_solution = self.get_best_solution_TIME(solutions=kth_solutions)

            if best_TIME_solution:

                if (best_TIME_solution["vehicles"] < best_solution["vehicles"] or best_TIME_solution["length"] < best_solution["length"]):

                    # send to process
                    best_solution = best_TIME_solution

                    if self.verbose:
                        print("NEW_BEST_SOLUTION (TIME) (Working time: {} at {})".format(str(time.time() - start_time),
                                                                              str(time.asctime())))

                    queue.put([best_TIME_solution, "ACS-TIME"])
                    vei_time_queue.put(best_TIME_solution)


            self.pheromones_TIME = self.update_pheromones(macs_ds, best_solution, self.pheromones_TIME, best_solution, IN=None)

    def count_customers(self, solution):
        customer_count = 0
        for route in solution["routes"]:
            customer_count = customer_count + len(route)-2

        return customer_count

    def get_customers(self, solution):
        customers = []

        for route in solution["routes"]:
            for i in range(1, len(route)-1):
                customers.append(route[i])

        return customers

    def not_visited_customers(self, vrptw, solution):
        return(list(set(vrptw.ids[1:]) - set(self.get_customers(solution))))

    def get_best_solution_VEI(self, solutions):
        most_customers = self.count_customers(max(solutions, key=lambda t: self.count_customers(t)))
        best_solutions = []
        for solution in solutions:
            if self.count_customers(solution) == most_customers:
                best_solutions.append(solution)

        best = min(best_solutions, key=lambda t: t["length"])

        return best

    def get_best_solution_TIME(self, solutions):

        feasible_kth_solutions = []

        for solution in solutions:
            if check_solution_feasibility(vrptw=self.vrptw, routes=solution["routes"]):
                feasible_kth_solutions.append(solution)

        if feasible_kth_solutions:
            min_veh_num = min(feasible_kth_solutions, key=lambda t: t["vehicles"])["vehicles"]

            solution_min_veh = []

            for solution in feasible_kth_solutions:
                if solution["vehicles"] == min_veh_num:
                    solution_min_veh.append(solution)

            best_sol = min(solution_min_veh, key=lambda t: t["length"])

            return best_sol

        else:
            return None

    def initialize_pheromones(self, size, best_solution):
        if self.tau0 is None:
            self.tau0 = 1/(self.vrptw.size * best_solution["length"])

        pheromones = np.zeros((size, size))

        for i in range(0, size):
            for j in range(0, size):
                pheromones[i][j] = self.tau0

        return pheromones

    def update_pheromones(self, macs_ds, solution, pheromones, best_solution, IN):

        def create_attractiveness_array(IN, current_location, current_time, feasible_cities, macs_ds):
            attractiveness = np.zeros((macs_ds.size, macs_ds.size))
            for city in feasible_cities:
                delivery_time = max(current_time + macs_ds.distances[current_location][city],
                                    macs_ds.time_windows[city][0])
                delta_time = delivery_time - current_time
                distance = delta_time * (macs_ds.time_windows[city][1] - current_time)
                if IN:
                    distance = max(1, distance - IN[city])
                else:
                    distance = max(1, distance)

                attractiveness[current_location][city] = 1.0 / distance
            return attractiveness

        def get_next_location(pheromones, location, target_locations):

            attractiveness = create_attractiveness_array(IN, location, macs_ds.time_windows[location][0],target_locations, macs_ds)

            pher_x_atract_B = []

            for target in target_locations:
                pher_x_atract_B.append((target, pheromones[location][target] * pow(attractiveness[location][target], self.beta)))

            pher_x_atract_B_sum = sum(n for _, n in pher_x_atract_B)

            if random.random() < self.q0: # exploitation
                return max(pher_x_atract_B ,key=lambda x:x[1])[0]

            else:   # exploration
                cities_and_probabilities = []
                for elem in pher_x_atract_B:
                    cities_and_probabilities.append((elem[0], elem[1]/pher_x_atract_B_sum))

                cities = [i[0] for i in cities_and_probabilities]
                probabilities = [i[1] for i in cities_and_probabilities]
                return np.random.choice(a=cities, p=probabilities)

        def get_list_of_first_customers(routes):
            customers = []

            for route in routes:
                customers.append(route[1])

            return customers

        def get_route_containing_customer(routes, customer):
            target_route = None

            for route in routes:
                if customer in route:
                    target_route = route.copy()
                    break

            return target_route


        depos = macs_ds.depo_ids.copy()

        temp_routes = solution["routes"].copy()
        final_routes = []

        while len(depos) > len(temp_routes):
            depos.pop()

        current_depo = depos.pop(0)
        first_depo = current_depo

        while temp_routes:

            new_route = [current_depo] #add new starting depo

            customers = get_list_of_first_customers(routes=temp_routes)
            next_location = get_next_location(pheromones=pheromones, location=current_depo, target_locations=customers)
            route_to_append = get_route_containing_customer(routes=temp_routes, customer=next_location)
            temp_routes.remove(route_to_append)
            route_to_append.pop(0) #remove old starting depo
            route_to_append.pop() #remove old finishing depo

            new_route += route_to_append

            last_customer = new_route[-1]
            if depos:
                finishing_depo = get_next_location(pheromones=pheromones, location=last_customer, target_locations=depos)
                depos.remove(finishing_depo)
                new_route += [finishing_depo]  # add new finishing depo
                current_depo = finishing_depo

            else:
                new_route += [first_depo]

            final_routes.append(new_route)


        for route in final_routes:

            for i in range(0, len(route)-1):
                pheromones[route[i]][route[i+1]] = (1-self.p)*pheromones[route[i]][route[i+1]] + self.p/best_solution["length"]
        # depos = macs_ds.depo_ids.copy()
        # depo = depos.pop(0)
        #
        # for route in solution["routes"]:
        #
        #
        #     pheromones[depo][route[1]] = (1-self.p)* pheromones[depo][route[1]] + self.p/best_solution["length"]
        #
        #     for i in range(1, len(route)-2):
        #         pheromones[route[i]][route[i+1]] = (1-self.p)*pheromones[route[i]][route[i+1]] + self.p/best_solution["length"]
        #
        #     if(depos):
        #         depo = depos.pop(0)
        #         pheromones[route[len(route)-1]][depo] = (1-self.p)*pheromones[route[len(route)-1]][depo] + self.p/best_solution["length"]
        #     else:
        #         pheromones[route[len(route)-1]][0] = (1-self.p)*pheromones[route[len(route)-1]][0] + self.p/best_solution["length"]

        return pheromones