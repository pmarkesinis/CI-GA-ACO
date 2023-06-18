import time
from Maze import Maze
from PathSpecification import PathSpecification
from Ant import Ant
import numpy as np

# Class representing the first assignment. Finds shortest path between two points in a maze according to a specific
# path specification.
class AntColonyOptimization:

    # Constructs a new optimization object using ants.
    # @param maze the maze .
    # @param antsPerGen the amount of ants per generation.
    # @param generations the amount of generations.
    # @param Q normalization factor for the amount of dropped pheromone
    # @param evaporation the evaporation factor.
    def __init__(self, maze, ants_per_gen, generations, q, evaporation):
        self.maze = maze
        self.ants_per_gen = ants_per_gen
        self.generations = generations
        self.q = q
        self.evaporation = evaporation
        self.gen_averages = []
        self.minimum = []

    # Loop that starts the shortest path process
    # @param spec Spefication of the route we wish to optimize
    # @return ACO optimized route
    def find_shortest_route(self, path_specification):
        # Initialize pheromone matrix to a small value
        # Initially, all links have the same (non-zero) probability to be explored
        self.maze.reset()
        result = None
        for i in range(1, self.generations + 1):
            # Create generation
            ants = []
            for a in range(1, self.ants_per_gen + 1):
                ant = Ant(self.maze, path_specification)
                ants.append(ant)

            # Make ants traverse the maze
            ant_count = 1
            ant_routes = []
            # print("Generation", i, "pheromone levels start as", sum(ant.maze.pheromones))
            for ant in ants:
                ant.reset_points()
                ant_route = ant.find_route()
                # If ant found a route
                if ant_route is not None and ant_route.size() > 0:
                    print("Generation", i, "ant", ant_count, "Ant route size", ant_route.size())
                    ant_count += 1
                    ant_routes.append(ant_route)
                    # If ant's route is the most optimal yet
                    if result is None or ant_route.shorter_than(result):
                        result = ant_route
                # If ant couldn't find a route
                else:
                    # print("Generation", i, "ant", ant_count, "The ant route is none or size 0")
                    ant_count += 1

            # Evaporate
            self.maze.evaporate(self.evaporation)
            self.maze.add_pheromone_routes(ant_routes, self.q)
            if len(ant_routes) != 0:
                minimum_distance = min([x.size() for x in ant_routes])
                avg_distance = np.average([x.size() for x in ant_routes])
                self.gen_averages.append(avg_distance)
                self.minimum.append(minimum_distance)
                print("Generation",i," minimum distance", minimum_distance,"|||",len(ant_routes),"found a route")
            else:
                print("Generation", i, "couldn't find a route")
            # print("Generation", i, "pheromone levels end as", sum(ant.maze.pheromones))
            print("-----------------------------------------------------")
        return result



    # # Update pheromone levels in the maze
    # for route in ant_routes:
    #     self.maze.add_pheromone_route(route, self.q)

    # self.maze.evaporate(self.evaporation)


