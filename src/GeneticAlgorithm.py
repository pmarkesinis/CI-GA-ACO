import random
import statistics as stat
from TSPData import TSPData
import numpy as np

# TSP problem solver using genetic algorithms.
class GeneticAlgorithm:

    # Constructs a new 'genetic algorithm' object.
    # @param generations the amount of generations.
    # @param popSize the population size.
    def __init__(self, generations, pop_size, crossover_prob, mutation_prob, values=[]):
        self.generations = generations
        self.pop_size = pop_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.values = values
        values = []

    # Creates a hashmap of (coordinate, key) entry
    # product_map[ID] gives coordinates of the product with ID
    def create_map(self, product_locations):
        product_map = {}
        # Create a map (coordinate, key)
        for i, coords in enumerate(product_locations):
            product_map[i] = coords
        return product_map

    # Creates a population of pop_size amount of chromosomes
    # Each chromosome is of length num_products, order gives the path taken
    def create_population(self, product_map):
        population = []
        for i in range(self.pop_size):
            # A chromosome looks like [0,3,4,2,1] of keys
            # Coordinates can be retrieved using product_map[entry]
            chromosome = np.random.permutation(list(product_map.keys()))
            population.append(chromosome)
        return population

    # Calculates the total distance travelled on the path suggested by
    # the gene order of the chromosome
    def calculate_distance(self, chromosome, tsp_data):
        fitness = 0
        starts = np.array(tsp_data.start_distances)
        between = np.array(tsp_data.distances)
        ends = np.array(tsp_data.end_distances)
        for a in range(0, len(chromosome)):
            # If it's the first product, distance is from start to product
            # ElIf it's the last product, distance is from the product to end
            # Else, it's between 2 products
            if a == 0:
                fitness = fitness + starts[chromosome[a]]
            elif a == len(chromosome) - 1:
                fitness = fitness + ends[chromosome[a]]
            else:
                gene1 = chromosome[a - 1]
                gene2 = chromosome[a]
                fitness = fitness + between[gene1][gene2]
        return fitness

    # Input is the array of chromosomes
    # Output is an array of distances of the paths of the chromosomes
    def fitness_function(self, population, tsp_data):
        distances = []
        for i in range(len(population)):
            chromosome = population[i]
            fitness = self.calculate_distance(chromosome, tsp_data)
            distances.append(fitness)
        return distances

    # Converts the total distance suggested by the chromosome into a fitness ratio %
    # relative to other chromosomes
    def fitness_ratio(self, distances):
        ratios = []
        total = sum(distances)
        for i in range(len(distances)):
            distance = distances[i]
            ratio = 100 - ((distance / total) * 100)
            ratios.append(ratio)
        return ratios

    # Performs selection of chromosomes for the next generationusing the roulette wheel selection technique.
    # Selects 2 chromosomes from population with a probability proportional to their fitness score.
    def roulette_wheel_selection(self, population, ratios):
        random_number = random.uniform(0,1)
        selected_chromosomes = []

        current_ratio = 0
        index1 = 0
        index2 = 0
        for i in range(len(ratios)):
            current_slice = ratios[i] + current_ratio
            if random_number <= current_slice and index1 == 0:
                index1 = i
            elif random_number <= current_slice and index2 == 0:
                index2 = i
            else:
                current_ratio += ratios[i]
        selected_chromosomes.append(population[index1])
        selected_chromosomes.append(population[index2])
        return selected_chromosomes

    def crossover(self, a, b):
        assert len(a) == len(b), "AssertionFailed: Parent chromosomes do not have the same length."
        if random.random() <= self.crossover_prob:
            offspring_a = []
            offspring_b = []
            offspring_set_a = set()
            offspring_set_b = set()
            split_points = sorted(random.sample(range(1, len(a)), 2))
            for i in range(len(a)):
                # Copy values from parents while avoiding duplicates
                if i <= split_points[0] or i > split_points[1]:
                    if a[i] not in offspring_set_a:
                        offspring_a.append(a[i])
                        offspring_set_a.add(a[i])
                    if b[i] not in offspring_set_b:
                        offspring_b.append(b[i])
                        offspring_set_b.add(b[i])
                else:
                    if a[i] not in offspring_set_b:
                        offspring_b.append(a[i])
                        offspring_set_b.add(a[i])
                    if b[i] not in offspring_set_a:
                        offspring_a.append(b[i])
                        offspring_set_a.add(b[i])

            # If one offspring is shorter than the parents, add the missing values
            while len(offspring_a) < len(a):
                val = random.choice(a)
                if val not in offspring_set_a:
                    offspring_a.append(val)
                    offspring_set_a.add(val)
            while len(offspring_b) < len(b):
                val = random.choice(b)
                if val not in offspring_set_b:
                    offspring_b.append(val)
                    offspring_set_b.add(val)
            return [offspring_a, offspring_b]

    def mutation(self, chromosome):
        if random.random() <= self.mutation_prob:
            index1, index2 = random.sample(range(len(chromosome)), 2)
            chromosome[index1], chromosome[index2] = chromosome[index2], chromosome[index1]
            return chromosome
        else:
            return chromosome

    # This method should solve the TSP.
    # @param pd the TSP data.
    # @return the optimized product sequence.
    def solve_tsp(self, tsp_data):
        product_map = {}
        # Create a map (coordinate, key)
        for i, coords in enumerate(tsp_data.product_locations):
            product_map[i] = coords
        self.product_map = product_map
        # Create the population
        population = self.create_population(product_map)
        # For each generation
        for gen in range(self.generations):
            ratios = self.fitness_ratio(self.fitness_function(population, tsp_data))
            children = []

            # Add pop_size amount of children to population
            # For example, if population is 20 chromosomes, add 20 children = 40
            while len(population) < (self.pop_size * 2):
                selected_chromosomes = self.roulette_wheel_selection(population, ratios)
                a = selected_chromosomes[0]
                b = selected_chromosomes[1]
                offspring_chromosomes = self.crossover(a,b)

                # Mutate for the offspring_chromosomes that were just created
                if offspring_chromosomes is not None:
                    for j in range(len(offspring_chromosomes)):
                        chromosome = offspring_chromosomes[j]
                        offspring_chromosomes[j] = self.mutation(chromosome)
                    population.append(offspring_chromosomes[0])
                    children.append(offspring_chromosomes[0])
                    population.append(offspring_chromosomes[1])
                    children.append(offspring_chromosomes[1])

            # Select the new population
            new_population = []
            added = False

            # 20% of the new population will be the best ones of the set (parents, children)
            while len(new_population) < (0.2 * self.pop_size):
                distances = self.fitness_function(population, tsp_data)
                ratios = self.fitness_ratio(distances)
                if not added:
                    added = True
                best_chromosome = population[np.argmax(ratios)]
                population.pop(np.argmax(ratios))
                new_population.append(best_chromosome)

            # 80% of the new population will be the selected from children using roulette wheel selection
            while len(new_population) < self.pop_size:
                children_distances = self.fitness_function(children, tsp_data)
                children_ratios = self.fitness_ratio(children_distances)
                c1, c2 = self.roulette_wheel_selection(children, children_ratios)
                new_population.append(c1)
                if len(new_population) < self.pop_size:
                    new_population.append(c2)

            # In order to graph it, add the best value to distances
            population = new_population
            distances = self.fitness_function(population, tsp_data)
            self.values.append(min(distances))
            print("Generation", gen, "| Minimum distance:", min(distances))

        # After repeating for all generations find the best chromosome and return it
        distances = self.fitness_function(population, tsp_data)
        print("The model is built using the following population size:", len(population))
        print("The model reached the conclusion after", self.generations, "generations.")
        print("The result (most-optimal) is the following chromosome:", population[np.argmin(distances)])
        print("with minimum distance of ", distances[np.argmin(distances)], "steps.")
        return population[np.argmin(distances)]


