import bisect
import random
import math

# Example list of points
POINTS = []

# Indexes of the points
INDEXES = list(range(len(POINTS)))

# Calculate distance between two points
def distance_between(x1, x2, y1, y2):
    return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 3)

# Generate a random solution (a random sequence of indexes)
def random_solution():
    shuffled_indexes = list(range(len(POINTS)))
    random.shuffle(shuffled_indexes)
    
    # Ensure the solution returns to the starting point
    shuffled_indexes.append(shuffled_indexes[0])
    return shuffled_indexes

# Calculate the total distance of a solution
def fitness(solution):
    total_distance = 0
    for i in range(len(solution) - 1):
        current_index = solution[i]
        next_index = solution[i + 1]
        distance = distance_between(
            POINTS[current_index]['x'], POINTS[next_index]['x'],
            POINTS[current_index]['y'], POINTS[next_index]['y']
        )
        total_distance += distance
    return round(total_distance, 3)

# Print the result in a formatted way
def print_result(solution):
    for i, city in enumerate(solution):
        if i < len(solution) - 1:
            print(city, end=" ⇢  ")
        else:
            print(city)
    total_distance = fitness(solution)
    print(f"Total Distance: {total_distance}")

# Greedy algorithm to find a solution starting from a specific point
def greedy_solution(starting_point):
    remaining_indexes = list(range(len(POINTS)))
    solution = [starting_point]
    
    while len(remaining_indexes) > 1:
        remaining_indexes.remove(starting_point)
        shortest_distance = float('inf')
        next_city = -1
        
        for i in remaining_indexes:
            distance = distance_between(
                POINTS[i]['x'], POINTS[starting_point]['x'],
                POINTS[i]['y'], POINTS[starting_point]['y']
            )
            if distance < shortest_distance:
                shortest_distance = distance
                next_city = i
        
        solution.append(next_city)
        starting_point = next_city
    solution.append(solution[0])
    return solution

# Find the best starting point
def find_the_best():
    shortest = float('inf')
    best_city = 0
    for i in range(len(POINTS)):
        distance = fitness(greedy_solution(i))
        if distance < shortest:
            shortest = distance
            best_city = i
    return best_city

# Find the avegrage result of 100 random solutions
def average_of_random(amount):
    total = 0
    for _ in range(amount):
        random_sol = random_solution()
        total += fitness(random_sol)         
    return round(total / amount, 3)      

# Genetic algorithm
def initial_population(size, greedy_ratio):
    population = []
    
    # How many there should be of greedy and random solutions
    size_greedy = int(size * greedy_ratio)
    size_random = size - size_greedy
    
    for _ in range(size_greedy):
        starting_point = random.choice(INDEXES)
        population.append(greedy_solution(starting_point))
        
    for _ in range(size_random):
        population.append(random_solution())
        
    random.shuffle(population)
    return population

def population_info(population):
    size = len(population)
    # Find the best, worst and average distance
    best_distance =  float('inf')
    worst_distance =  float('-inf')
    total_distance = 0
    for solution in population:
        distance = fitness(solution)
        total_distance += distance
        if distance < best_distance:
            best_distance = distance
        if distance > worst_distance:
            worst_distance = distance
    average_distance = round(total_distance / size, 3)
    print(f"Population size: {size}")
    print(f"Best distance: {best_distance}")
    print(f"Worst distance: {worst_distance}")
    print(f"Average distance: {average_distance}")
    
def tournament(population, tournament_size):
    # Take a random sample out of population 
    contestants = random.sample(population, tournament_size)
    
    best_distance = float("inf")
    winner = []
    
    # Determine the best one out of the sample
    for contestant in contestants:
       distance = fitness(contestant)
       if  distance < best_distance:
           best_distance = distance
           winner = contestant
    return winner 

def elite_selection(population, elite_size):
    elite = []
    for solution in population:
        solution_fitness = fitness(solution)
        
        # If there is no initial elite
        if len(elite) < elite_size:
            elite.append((solution, solution_fitness))
        else:
            # Find the worst solution currently in elite
            longest_in_elite = max(elite, key=lambda x:x[1])
            
            # If current solution is better than the one in elite - replace it
            if solution_fitness < longest_in_elite[1]:
                index_of_longest = elite.index(longest_in_elite)
                elite[index_of_longest] = (solution, solution_fitness)
                
    # return only solutions with no distances
    return [x[0] for x in elite]

def roulette_selection(population):
    # Calculate fitness for each solution
    distances = [fitness(solution) for solution in population]
    distance_of_all = sum(distances)
    
    # Calculate cumulative probabilities in one step
    cumulative_distances = []
    cumulative_sum = 0
    for distance in distances:
        cumulative_sum += distance / distance_of_all
        cumulative_distances.append(cumulative_sum)
    
    # Use binary search for faster selection
    rand = random.random()
    index = bisect.bisect_left(cumulative_distances, rand)
    return population[index]

def ordered_crossover(parent1,  parent2):
    # Remove last city since it's the same as the first
    parent1 = parent1[:-1]
    parent2 = parent2[:-1]
    
    # Make a list of the same size as parents
    offspring = [None] * len(parent1)
    
    # Take a random slice from parent 1
    start_position = random.randint(0, len(parent1) - 1)
    end_position = random.randint(0, len(parent1) - 1)
    if start_position > end_position:
        start_position, end_position = end_position, start_position
    sub_parent1 = parent1[start_position:end_position]
    
    # Take all the numbers from parent 2 that were not taken yet
    sub_parent2 = [x for x in parent2 if x not in sub_parent1]
    
    # Set numbers from parent 1 in the same position in offspring
    offspring[start_position:end_position] = sub_parent1
    
    # Fill up all the gaps with numbers from parent 2
    index = 0
    for i in range(len(offspring)):
        if offspring[i] is None:
            if index < len(sub_parent2):
                offspring[i] = sub_parent2[index] 
                index += 1 
                
    offspring.append(offspring[0])
    return offspring

def partially_matched_crossover(parent1, parent2):
    # Remove the last city
    parent1 = parent1[:-1]
    parent2 = parent2[:-1]
    
    # Create an empty offspring
    offspring = [None] * len(parent1)
    
    # Randomly select crossover points
    start, end = sorted(random.sample(range(len(parent1)), 2))
    
    # Copy the subsection from Parent 1 to the offspring
    offspring[start:end] = parent1[start:end]
    
    # Create mappings for the crossover segment
    mapping = {parent1[i]: parent2[i] for i in range(start, end)}
    
    # Fill the remaining positions
    for i in range(len(parent2)):
        if offspring[i] is None:
            value = parent2[i]
            while value in mapping and value in offspring:
                value = mapping[value]
            offspring[i] = value
    
    # Re-add the first city
    offspring.append(offspring[0])
    
    return offspring

def cycle_crossover(parent1, parent2):
    # Remove last city (usually a dummy city to complete the tour)
    parent1 = parent1[:-1]
    parent2 = parent2[:-1]
    
    # Initialize offspring with None
    offspring = [None] * len(parent1)
    
    # Mark positions to visit
    visited = [False] * len(parent1)
    
    # Cycle crossover
    start = random.randint(0, len(parent1) - 1)  # Start point for the cycle
    cycle_start = start
    
    while None in offspring:  # Continue until all positions are filled
        current = cycle_start
        # Follow the cycle until we return to the start
        while not visited[current]:
            visited[current] = True
            # Place the element from parent1 in the offspring
            offspring[current] = parent1[current]
            # Move to the corresponding position in Parent 2
            current = parent2.index(parent1[current])
        
        # If any positions remain unfilled, swap to Parent 2
        for i in range(len(offspring)):
            if offspring[i] is None:
                offspring[i] = parent2[i]

    # Re-add the first city to complete the loop
    offspring.append(offspring[0])

    return offspring

def mutation_swap(mutation_probability, child):
    solution = child.copy()
    if random.random() <= mutation_probability:
        # Get two random cities in the solution
        first_city_index = random.randint(1, len(solution) - 2)
        second_city_index = random.randint(1, len(solution) - 2)
        first_city = solution[first_city_index]
        second_city = solution[second_city_index]
        
        # Swap those two cities places
        solution[first_city_index] = second_city
        solution[second_city_index] = first_city
    return solution

import random

def mutation_inversion(mutation_probability, child):
    solution = child.copy()
    if random.random() <= mutation_probability:
        # Get two random cities in the solution
        first_index = random.randint(1, len(solution) - 2)
        last_index = random.randint(1, len(solution) - 2)

        # Ensure first_index is less than last_index
        if first_index > last_index:
            first_index, last_index = last_index, first_index

        # Invert the range
        solution[first_index:last_index] = solution[first_index:last_index][::-1]
    return solution

def select_parents(population, roulette, tournament_size):
    if roulette:
        return random.sample([roulette_selection(population) for _ in range(2)], 2)
    return random.sample([tournament(population, tournament_size) for _ in range(2)], 2)

def create_n_epochs(initial_population, crossover, number_of_epochs, inversion, mutation_probability, roulette, tournament_size, elitism, elite_size):
    n = 1
    population = initial_population
    
    print(f"Epoch {n}")
    population_info(population)
    
    while n < number_of_epochs:
        new_population = []
        existing_individuals = set(new_population)
        
        if elitism:
            elite = elite_selection(population, elite_size)
            new_population.extend(elite)
            existing_individuals.update(tuple(ind) for ind in elite)
            
        while len(new_population) < len(population):
            # Select parents
            parent1, parent2 = select_parents(population, roulette, tournament_size)
            
            # Perform chosen crossover
            match crossover:
                case 1:  
                    child = ordered_crossover(parent1, parent2)
                case 2:  
                    child = partially_matched_crossover(parent1, parent2)
                case 3:  
                    child = cycle_crossover(parent1, parent2)
            
            # Apply chosen mutation
            if inversion:
                mutated_child = mutation_inversion(mutation_probability, child)
            else:
                mutated_child = mutation_swap(mutation_probability, child)
            
            # Add to the new population
            if tuple(mutated_child) not in existing_individuals:
                new_population.append(mutated_child)
                existing_individuals.add(tuple(mutated_child))
        
        # Update for the next epoch
        population = new_population
        n += 1
        
        print(f"\nEpoch {n}")
        population_info(population)
        
    return population



population = initial_population(50, 0.2)
last_population = create_n_epochs(population, 1, 10, True, 0.2, False, 5, True, 2)