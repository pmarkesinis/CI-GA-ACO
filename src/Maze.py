import traceback
import sys
import numpy as np

from SurroundingPheromone import SurroundingPheromone
from Coordinate import Coordinate


# Class that holds all the maze data. This means the pheromones, the open and blocked tiles in the system as
# well as the starting and end coordinates.
class Maze:

    # Constructor of a maze
    # @param walls int array of tiles accessible (1) and non-accessible (0)
    # @param width width of Maze (horizontal)
    # @param length length of Maze (vertical)
    def __init__(self, walls, width, length):
        self.walls = walls
        self.length = length
        self.width = width
        self.start = None
        self.end = None
        self.pheromones = self.initialize_pheromones()

    # Initialize pheromones to a start value.
    def initialize_pheromones(self):
        # Initialize a matrix of pheromones with the same dimensions as the maze
        pheromones = np.ones((self.width, self.length)) 

        # Set pheromones to 0 for any inaccessible tiles (walls)
        for x in range(self.width):
            for y in range(self.length):
                if self.walls[x][y] == 0:
                    pheromones[x][y] = 0
        return pheromones

    # Reset the maze for a new shortest path problem.
    def reset(self):
        try:
            self.initialize_pheromones()
        except Exception as e:
            print("An error occurred while resetting the maze:")
            traceback.print_exc()

    # Update the pheromones along a certain route according to a certain Q
    # @param r The route of the ants
    # @param Q Normalization factor for amount of dropped pheromone
    def add_pheromone_route(self, route, q):
        # Calculate the amount of pheromones to be dropped on each tile of the route
        # For hard
        # delta_pheromone = 20 / np.power(1.01, route.size() - 850)
        delta_pheromone = q / route.size()
        # delta_pheromone = q / route.size()

        # print("THIS IS THE ROUTE START ", route.start)
        route_coordinates = [route.start]
        curr_pos = route.start

        for direction in route.route:
            if direction.value == 0:
                curr_pos.x += 1
                new_coord = Coordinate(curr_pos.x, curr_pos.y)
                route_coordinates.append(new_coord)
            elif direction.value == 1:
                curr_pos.y -= 1
                new_coord = Coordinate(curr_pos.x, curr_pos.y)
                route_coordinates.append(new_coord)
            elif direction.value == 2:
                curr_pos.x -= 1
                new_coord = Coordinate(curr_pos.x, curr_pos.y)
                route_coordinates.append(new_coord)
            elif direction.value == 3:
                curr_pos.y += 1
                new_coord = Coordinate(curr_pos.x, curr_pos.y)
                route_coordinates.append(new_coord)
            else:
                continue

        # Add the pheromones to the tiles of the route
        for coordinate in route_coordinates:
            self.pheromones[coordinate.x][coordinate.y] += delta_pheromone
        return

    # Update pheromones for a list of routes
    # @param routes A list of routes
    # @param Q Normalization factor for amount of dropped pheromone
    def add_pheromone_routes(self, routes, q):
        for r in routes:
            self.add_pheromone_route(r, q)

    # Evaporate pheromone
    # @param rho evaporation factor
    def evaporate(self, rho):
        # Iterate over all tiles in the maze
        for x in range(self.width):
            for y in range(self.length):
                # Multiply the pheromone level by the evaporation factor
                self.pheromones[x][y] *= rho
        return

    # Width getter
    # @return width of the maze
    def get_width(self):
        return self.width

    # Length getter
    # @return length of the maze
    def get_length(self):
        return self.length

    # Returns the amount of pheromones on the neighbouring positions (N/S/E/W).
    # @param position The position to check the neighbours of.
    # @return the pheromones of the neighbouring positions.
    def get_surrounding_pheromone(self, position):
        x, y = position.x, position.y
        north, south, east, west = 0.0, 0.0, 0.0, 0.0
        if self.in_bounds((x - 1, y)):
            west = self.get_pheromone((x - 1, y))
        if self.in_bounds((x + 1, y)):
            east = self.get_pheromone((x + 1, y))
        if self.in_bounds((x, y + 1)):
            south = self.get_pheromone((x, y + 1))
        if self.in_bounds((x, y - 1)):
            north = self.get_pheromone((x, y - 1))

        return SurroundingPheromone(north, east, south, west)

    # Pheromone getter for a specific position. If the position is not in bounds returns 0
    # @param pos Position coordinate
    # @return pheromone at point
    def get_pheromone(self, pos):
        x, y = pos
        # x, y = pos.get_x(), pos.get_y()
        if not self.in_bounds(pos):
            return 0
        return self.pheromones[x][y]

    # Check whether a coordinate lies in the current maze.
    # @param position The position to be checked
    # @return Whether the position is in the current maze
    def in_bounds(self, position):
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.length
        # return position.x_between(0, self.width) and position.y_between(0, self.length)

    # Representation of Maze as defined by the input file format.
    # @return String representation
    def __str__(self):
        string = ""
        string += str(self.width)
        string += " "
        string += str(self.length)
        string += " \n"
        for y in range(self.length):
            for x in range(self.width):
                string += str(self.walls[x][y])
                string += " "
            string += "\n"
        return string

    # Method that builds a mze from a file
    # @param filePath Path to the file
    # @return A maze object with pheromones initialized to 0's inaccessible and 1's accessible.
    @staticmethod
    def create_maze(file_path):
        try:
            f = open(file_path, "r")
            lines = f.read().splitlines()
            dimensions = lines[0].split(" ")
            width = int(dimensions[0])
            length = int(dimensions[1])

            # make the maze_layout
            maze_layout = []
            for x in range(width):
                maze_layout.append([])

            for y in range(length):
                line = lines[y + 1].split(" ")
                for x in range(width):
                    if line[x] != "":
                        state = int(line[x])
                        maze_layout[x].append(state)
            print("Ready reading maze file " + file_path)
            return Maze(maze_layout, width, length)
        except FileNotFoundError:
            print("Error reading maze file " + file_path)
            traceback.print_exc()
            sys.exit()
