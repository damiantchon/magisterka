from services.calculate import nearest_neighbors_vrptw, nearest_neighbors_vrptw_vei, local_search_clean
import threading
from threading import Thread
from threading import Event
from VRPTW import VRPTW_MACS_DS
import numpy as np
import random
from services.calculate import routes_length, check_solution_feasibility
import copy


class MACS_VRPTW(): #Multiple Ant Colony System for Vehicle Routing Problems With Time Windows

    def __init__(self, vrptw, m, alpha, beta, tau0, q0, p): #jeśli tau0 , m - liczba mrówek, q0 - exploitation vs exploration

        self.vrptw = vrptw
        self.m = m
        self.alpha = alpha
        self.beta = beta
        self.tau0 = tau0
        self.q0 = q0
        self.p = p

        self.pheromones_TIME = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j
        self.pheromones_VEI = [] # 2 wymiarowa tablica zawierająca informacje o feromonie z i na j
        self.shortest_path = []

        self.best_solution = None
        self.best_solution_updated = False

        self.lock = threading.Lock()
        self.event = Event()

        self.vei_running = True
        self.time_running = True

    def run(self):
        self.best_solution = nearest_neighbors_vrptw(self.vrptw)
        self.best_solution = local_search_clean(self.vrptw, self.best_solution)

        print("Best solution v:", self.best_solution["vehicles"])
        print("Tau:", self.tau0)


        v = self.best_solution["vehicles"]

        # self.ACS_TIME(v+1)
        # self.ACS_VEI(v)
        counter = 0
        # todo WARUNKI WYJŚCIA
        while True:

            v = self.best_solution["vehicles"]

            vei_thread = Thread(target=self.ACS_VEI, args=(v,)) #TODO Poprawić "v-ki"
            time_thread = Thread(target=self.ACS_TIME, args=(v+1,))

            vei_thread.start()
            time_thread.start()

            self.event.wait()
            self.event.clear()
            self.vei_running = False
            self.time_running = False

            vei_thread.join()
            time_thread.join()

            self.vei_running = True
            self.time_running = True



    def new_active_ant(self, k, local_search, IN, macs_ds, pheromones):

        def get_fesible_cities(with_depos):

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

        def get_next_location(pheromones):

            pher_x_atract_B = []

            for ct in feasible_cities:
                pher_x_atract_B.append((ct, pheromones[current_location][ct] * pow(attractiveness[current_location][ct], self.beta)))

            pher_x_atract_B_sum = sum(n for _, n in pher_x_atract_B)

            if random.random() < self.q0: # exploitation
                return max(pher_x_atract_B ,key=lambda x:x[1])[0]

            else:
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

            def calculate_demands(decoded_tour):

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
                    if time + macs_ds.distances[route[i]][route[i+1]] <= macs_ds.time_windows[route[i+1]][1]:

                        time = max(time + macs_ds.distances[route[i]][route[i+1]], macs_ds.time_windows[route[i+1]][0])
                        time = time + macs_ds.service_times[route[i+1]]

                        if time + macs_ds.distances[route[i+1]][0] > macs_ds.time_windows[0][1]:
                            return False
                    else:
                        return False

                return True

            def route_length(route):
                length = 0

                for i in range(0, len(route) - 1):
                    length += macs_ds.distances[route[i]][route[i + 1]]

                return round(length, 2)


            # divide tour into list of single vehicle rides
            decoded_tour = decode_tour(tour)
            # print(decoded_tour)
            tours_with_demands = calculate_demands(decoded_tour)

            # create list of non_visited sorted by delivery quantities (tuple (id, quantity))
            non_visited = set(non_visited) - set(macs_ds.depo_ids) #  remove all depos from not visited (just to be sure :D)

            nv_w_demands = []

            for ct in non_visited:
                nv_w_demands.append((ct, macs_ds.demands[ct]))

            nv_w_demands = sorted(nv_w_demands, key=lambda x: x[1], reverse=True)


            # print(tours_with_demands)

            for city_w_demand in nv_w_demands:
                # print("CITY WITH DEMAND", city_w_demand)
                posible_inserts = [] #  list of tuples (tour_id, insertion_point, distance)

                for tour_id, t in enumerate(tours_with_demands):
                    # TODO ROZKMINIĆ BUG "826" - coś nie tak pilnowaniem Load
                    if t[1] + city_w_demand[1] <= macs_ds.vehicle_capacity: # check if demand did not exceed vehicle_capacity
                        route = t[0].copy()
                        # print("ROUTE", route)
                        for n, city in enumerate(t[0][1:], 1):
                            route.insert(n, city_w_demand[0])
                            # print("THEORETICAL ROUTE", route, is_fesible(route))
                            if is_fesible(route):
                                posible_inserts.append((tour_id, n, route_length(route)))
                            route.remove(city_w_demand[0])
                # print("POSSIBLE_INSERTS", posible_inserts)
                if posible_inserts:
                    best = min(posible_inserts, key=lambda x: x[2])
                    # print("BEST", best)
                    tours_with_demands[best[0]][0].insert(best[1], city_w_demand[0])
                    cities_to_visit.remove(city_w_demand[0])

            solution = {}
            solution["length"] = 0
            solution["vehicles"] = 0
            solution["routes"] = [x[0] for x in tours_with_demands]
            solution["length"] = routes_length(macs_ds, solution["routes"])
            solution["vehicles"] = len(solution["routes"])

            # print(solution)
            return solution

        current_location = macs_ds.get_random_depo()
        current_time = 0
        load = 0
        tour = [current_location]

        # initialization
        cities_to_visit = macs_ds.ids.copy()
        cities_to_visit.remove(current_location)

        feasible_cities = get_fesible_cities(with_depos=False)

        while feasible_cities:
            attractiveness = np.zeros((macs_ds.size, macs_ds.size))

            for city in feasible_cities:
                delivery_time = max(current_time + macs_ds.distances[current_location][city], macs_ds.time_windows[city][0])
                delta_time = delivery_time - current_time
                distance = delta_time*(macs_ds.time_windows[city][1] - current_time)
                if IN != 0:
                    distance = max(1, distance - IN[city])
                else:
                    distance = max(1, distance)

                # print("DISTANCE of city",city,":", distance, "(", delta_time ,"*", (macs_ds.time_windows[city][1] - current_time),")")

                attractiveness[current_location][city] = 1.0/distance

            next_location = get_next_location(pheromones=pheromones)# TODO - wybra następną lokację na podstawie (Equation 1)
            tour.append(next_location)
            current_time = max(current_time + macs_ds.distances[current_location][next_location], macs_ds.time_windows[next_location][0])\
                           + macs_ds.service_times[next_location]
            load = load + macs_ds.demands[next_location]

            cities_to_visit.remove(next_location)
            # print("Next location:", next_location)
            if next_location in macs_ds.depo_ids:
                current_time = 0
                load = 0

            # local pheromone updating
            pheromones[current_location][next_location] = \
                ((1-self.p) * pheromones[current_location][next_location]) + (self.p*self.tau0)

            current_location = next_location

            if current_location in macs_ds.depo_ids:
                feasible_cities = get_fesible_cities(with_depos=False)
            else:
                feasible_cities = get_fesible_cities(with_depos=True)

        #TODO insertion procedure
        # print(tour)
        solution = insertion_procedure(tour=tour, non_visited=cities_to_visit)

        if list(set(cities_to_visit) - set(macs_ds.depo_ids)):
            feasible = False
        else:
            feasible = True

        if local_search and feasible:
            # print("BEFORE", solution)
            last_solution_length = solution["length"]

            # solution = local_search_clean(macs_ds, solution)
            #
            # while (last_solution_length > solution["length"]):
            #     last_solution_length = solution["length"]
            #     solution = local_search_clean(macs_ds, solution)
            print(solution)
        return solution

    def ACS_VEI(self, v):

        print("ACS_VEI v =", v)

        macs_ds = VRPTW_MACS_DS(self.vrptw, v)
        self.pheromones_VEI = self.initialize_pheromones(macs_ds.size)

        best_VEI_solution = nearest_neighbors_vrptw_vei(vrptw=macs_ds, v=v)

        IN = [0] * macs_ds.size

        while self.vei_running:

            kth_solutions = []
            for k in range(0, self.m):
                solution = self.new_active_ant(k, local_search=False, IN=IN, macs_ds=macs_ds, pheromones=self.pheromones_VEI)

                for customer in list(set(self.vrptw.ids) - set(self.get_customers(solution) + [0])):
                    IN[customer] = IN[customer] + 1
                kth_solutions.append(solution)

            best_colony_solution = self.get_best_solution_VEI(kth_solutions)
            if self.count_customers(best_colony_solution) > self.count_customers(best_VEI_solution):
                best_VEI_solution = best_colony_solution
                IN = [0] * macs_ds.size

                print("CHECKING FISIBILITY OF", best_VEI_solution)
                if check_solution_feasibility(self.vrptw, best_VEI_solution["routes"]):
                    print("FEASIBLE")
                    self.lock.acquire()
                    self.best_solution = best_VEI_solution
                    self.vei_running = False
                    self.time_running = False
                    if not self.event.isSet():
                        self.event.set()
                    self.lock.release()


            self.pheromones_VEI = self.update_pheromones(best_VEI_solution, self.pheromones_VEI)
            self.lock.acquire()
            self.pheromones_VEI = self.update_pheromones(self.best_solution, self.pheromones_VEI)
            self.lock.release()
        print("DEAD :(")



    def ACS_TIME(self, v):

        print("ACS_TIME v =", v)

        macs_ds = VRPTW_MACS_DS(self.vrptw, v)

        self.pheromones_TIME = self.initialize_pheromones(macs_ds.size)

        while self.time_running:
            print("BEST SOLUTION:", self.best_solution)
            print(macs_ds.depo_ids)
            kth_solutions = []

            for k in range(0, self.m):
                kth_solutions.append(self.new_active_ant(k=1, local_search=True, IN=0, macs_ds=macs_ds, pheromones=self.pheromones_TIME))
                if self.time_running is False:
                    break

            best_TIME_solution = self.get_best_solution_TIME(macs_ds=macs_ds, solutions=kth_solutions)

            if best_TIME_solution:
                self.lock.acquire()
                if (best_TIME_solution["vehicles"] < self.best_solution["vehicles"] or best_TIME_solution["length"] < self.best_solution["length"]) and self.time_running:

                    self.best_solution = best_TIME_solution
                    self.time_running = False
                    self.vei_running = False
                    if not self.event.isSet():
                        self.event.set()
                    self.lock.release()
                else:
                    self.lock.release()

            self.pheromones_TIME = self.update_pheromones(self.best_solution, self.pheromones_TIME)



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

    def get_best_solution_TIME(self, macs_ds, solutions):

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


    def initialize_pheromones(self, size):
        if self.tau0 is None:
            self.tau0 = 1/(self.vrptw.size * self.best_solution["length"])

        pheromones = np.zeros((size, size))

        for i in range(0, size):
            for j in range(0, size):
                pheromones[i][j] = self.tau0

        return pheromones

    def update_pheromones(self, solution, pheromones):
        for route in solution["routes"]:
            for i in range(0, len(route)-1):
                pheromones[route[i]][route[i+1]] = (1-self.p)*pheromones[route[i]][route[i+1]] + self.p/self.best_solution["length"]

        return pheromones