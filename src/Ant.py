import random
from Route import Route
from Coordinate import Coordinate
import numpy as np
from Direction import Direction

#Class that represents the ants functionality.
class Ant:

    # Constructor for ant taking a Maze and PathSpecification.
    # @param maze Maze the ant will be running in.
    # @param spec The path specification consisting of a start coordinate and an end coordinate.
    def __init__(self, maze, path_specification):
        self.maze = maze
        self.start = path_specification.get_start()
        self.start_x = self.start.get_x()
        self.start_y = self.start.get_y()
        self.current_position = path_specification.get_start()
        self.end = path_specification.get_end()
        self.rand = random

    def reset_points(self):
        self.start = Coordinate(self.start_x, self.start_y)
        self.current_position = Coordinate(self.start_x, self.start_y)

    def check_deadend(self, visited, current_position, pheromone_probs):
        north, south, east, west = False, False, False, False
        if current_position.add_direction(Direction(0)) in visited or pheromone_probs[1] == 0:
            east = True
        if current_position.add_direction(Direction(1)) in visited or pheromone_probs[0] == 0:
            north = True
        if current_position.add_direction(Direction(2)) in visited or pheromone_probs[3] == 0:
            west = True
        if current_position.add_direction(Direction(3)) in visited or pheromone_probs[2] == 0:
            south = True
        return north and south and east and west

    def get_available_options(self, visited, current_position, pheromone_probs):
        indices = [1, 0, 3, 2]
        count = 0
        for i in range(len(pheromone_probs)):
            prob = pheromone_probs[i]
            if prob > 0:
                direction = Direction(indices[i])
                if current_position.add_direction(direction) not in visited:
                    count += 1
        return count

    def update_choices(self, indices, pheromone_probs, choice):
        pheromone_probs[indices.index(choice)] = 0.0
        total = np.sum(pheromone_probs)
        result = []
        for prob in pheromone_probs:
            result.append(prob / total)

        return result

    # Given [0, 3.95, 0.395, 0](the pheromone in each direction)
    # Returns [0, 0.5, 0.5, 0](the probability of going that direction based on pheromone amount)
    def calculate_direction_probs(self, surrounding_pheromones):
        total = surrounding_pheromones.get_total_surrounding_pheromone()
        pheromone_probs = [surrounding_pheromones.north, surrounding_pheromones.east, surrounding_pheromones.south, surrounding_pheromones.west]
        pheromone_probs = [(x / total) for x in pheromone_probs]
        return pheromone_probs

    # Method that performs a single run through the maze by the ant.
    # @return The route the ant found through the maze.
    def find_route(self):
        visited = []
        self.reset_points()
        # print("The amount of pheromone in the maze is",sum(sum(self.maze.pheromones)))
        steps = []
        route = Route(self.current_position)
        stack = []
        max_steps = 500
        # max_steps = 1350
        counter = 0
        # stack.append((Coordinate(self.start_x, self.start_y), 0))
        while self.current_position != self.end and route.size() <= max_steps:
            # print(self.current_position)
            counter += 1
            visited.append(self.current_position)
            surrounding_pheromones = self.maze.get_surrounding_pheromone(self.current_position)
            pheromone_probs = self.calculate_direction_probs(surrounding_pheromones)
            indices = [1, 0, 3, 2]

            for i in range(4):
                if (self.current_position.add_direction(Direction(indices[i])) in visited):
                    pheromone_probs[i] = 0

            # IF IT'S A DEAD-END
            if len(steps) != 0 and (self.check_deadend(visited, self.current_position, pheromone_probs)):
                if len(stack) == 0:
                    return None
                self.current_position, old_route = stack.pop()
                visited.remove(self.current_position)
                while old_route < route.size():
                    route.remove_last()
                    steps.pop()
                continue

            # ELSE
            # CHECK WHETHER POSITION SHOULD BE ADDED TO THE STACK (2 OR MORE CHOICES)
            if self.get_available_options(visited, self.current_position, pheromone_probs) >= 2:
                # print(self.current_position)
                stack.append((self.current_position, route.size()))

            # DECIDE THE DIRECTION TO MOVE (PROPORTIONAL-RANDOMLY)
            choice = random.choices(indices, weights=pheromone_probs)[0]


            # IF ITS NOT THE FIRST STEP
            if len(steps) != 0:
                next_place = self.current_position.add_direction(Direction(choice))
                while abs(steps[-1] - choice) == 2 or next_place in visited:
                    pheromone_probs = self.update_choices(indices, pheromone_probs, choice)
                    choice = random.choices(indices, weights=pheromone_probs)[0]
                    next_place = self.current_position.add_direction(Direction(choice))

            # MOVE IN THE CHOSEN DIRECTION AND UPDATE THE ROUTE AND STEPS
            self.current_position = self.current_position.add_direction(Direction(choice))
            route.add(Direction(choice))
            steps.append(choice)
        if len(steps) >= max_steps:
            # print("BAD")
            return None
        # print("GOOD")
        return route
