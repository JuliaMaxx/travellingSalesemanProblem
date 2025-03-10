import time
import random
import bisect
import config
from algorithms.algorithms import StopAlgorithmException, fitness
from algorithms.random_algorithm import random_solution
from algorithms.greedy_algorithm import greedy_solution

# Genetic algorithm
def genetic_solution(population_size, greedy_ratio, crossover, number_of_epochs, mutation, mutation_probability, selection, tournament_size, elitism, elite_size, socketio):
    try:
        n = 1
        population = initial_population(population_size, greedy_ratio, socketio)
        population_info(population, socketio, n)
        
        while n < number_of_epochs:
            # Pause / Resume / Stop
            if config.stop_event.is_set():
                return
            config.pause_event.wait()
            
            new_population = []
            existing_individuals = set(new_population)
            
            if elitism:
                elite = elite_selection(population, elite_size)
                new_population.extend(elite)
                existing_individuals.update(tuple(ind) for ind in elite)
                
            while len(new_population) < len(population):
                # Select parents
                parent1, parent2 = select_parents(population, selection, tournament_size)
                
                time.sleep(config.VISUALIZATION_DELAY)
                
                # Pause / Resume / Stop
                if config.stop_event.is_set():
                    return
                config.pause_event.wait()
                
                if not config.stop_event.is_set():
                    socketio.emit('update_lines', {'solution': parent1, 'points': config.POINTS, 'type':'parent'})
                socketio.emit('update_distance', {'distance': round(fitness(parent1) * 10, 3)})  
                
                    
                time.sleep(config.VISUALIZATION_DELAY)
                
                # Pause / Resume / Stop
                if config.stop_event.is_set():
                    return
                config.pause_event.wait()
                
                if not config.stop_event.is_set():
                    socketio.emit('update_lines', {'solution': parent2, 'points': config.POINTS, 'type':'parent'})
                socketio.emit('update_distance', {'distance': round(fitness(parent2) * 10, 3)})  
                
                # Pause / Resume / Stop
                if config.stop_event.is_set():
                    return
                config.pause_event.wait()
            
                # Perform chosen crossover
                match crossover:
                    case 1:  
                        child = ordered_crossover(parent1, parent2)
                    case 2:  
                        child = partially_matched_crossover(parent1, parent2)
                    case 3:  
                        child = cycle_crossover(parent1, parent2)     
                
                time.sleep(config.VISUALIZATION_DELAY)
                
                # Pause / Resume / Stop
                if config.stop_event.is_set():
                    return
                config.pause_event.wait()
                
                
                if not config.stop_event.is_set():
                    socketio.emit('update_lines', {'solution': child, 'points': config.POINTS, 'type':'crossover'})
                socketio.emit('update_distance', {'distance': round(fitness(child) * 10, 3)})  
                
                    
                # Apply chosen mutation
                match mutation:
                    case 1:
                        mutated_child = mutation_inversion(mutation_probability, child)
                    case 2:
                        mutated_child = mutation_swap(mutation_probability, child)
                        
                time.sleep(config.VISUALIZATION_DELAY)
                
                # Pause / Resume / Stop
                if config.stop_event.is_set():
                    return
                config.pause_event.wait()
                
                if not config.stop_event.is_set():
                    socketio.emit('update_lines', {'solution': mutated_child, 'points': config.POINTS, 'type':'mutation'})
                socketio.emit('update_distance', {'distance': round(fitness(mutated_child) * 10, 3)})  
                    
                # Add to the new population
                if tuple(mutated_child) not in existing_individuals:
                    new_population.append(mutated_child)
                    existing_individuals.add(tuple(mutated_child))
            # Update for the next epoch
            population = new_population
            n += 1
        
            best = population_info(population, socketio, n)
            
            time.sleep(config.VISUALIZATION_DELAY)
            
            # Pause / Resume / Stop
            if config.stop_event.is_set():
                return
            config.pause_event.wait()
            
            if not config.stop_event.is_set():
                socketio.emit('update_lines', {'solution': best, 'points': config.POINTS, 'type':'best'})
            socketio.emit('update_distance', {'distance': round(fitness(best) * 10, 3)})  
            
        socketio.emit('algorithm_finished', {})       
        return population
    except StopAlgorithmException:
        return


# Initial population creation
def initial_population(size, greedy_ratio, socketio):
    population = []
    additional = True
    
    # How many there should be of greedy and random solutions
    size_greedy = int(size * greedy_ratio)
    size_random = size - size_greedy
    
    for _ in range(size_greedy):
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        starting_point = random.choice(list(range(len(config.POINTS))))
        population.append(greedy_solution(starting_point, socketio, additional))
        
    for _ in range(size_random):
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        population.append(random_solution(socketio))
        
    random.shuffle(population)
    return population


# Information about an epoch
def population_info(population, socketio, n):
    size = len(population)
    
    # Initialize variables for the best, worst, and total distance
    best_distance = float('inf')
    worst_distance = float('-inf')
    total_distance = 0
    best_solution = None

    # Loop over the population
    for solution in population:
        # Pause / Resume / Stop 
        if config.stop_event.is_set():
            raise StopAlgorithmException()
        config.pause_event.wait()
        
        distance = fitness(solution)
        total_distance += distance

        # Track best and worst distances
        if distance < best_distance:
            best_distance = distance
            best_solution = solution
        if distance > worst_distance:
            worst_distance = distance

    # Calculate and round the average distance
    average_distance = total_distance / size if size else 0
    average_distance = round(average_distance, 3)
    socketio.emit('update_info', {'best': round(best_distance * 10, 3), 'worse': round(worst_distance * 10, 3), 'average': round(average_distance * 10, 3), 'epoch': n})
    # Return the best solution found
    return best_solution


# Selections
def tournament(population, tournament_size):
    # Pause / Resume / Stop
    if config.stop_event.is_set():
            raise StopAlgorithmException()
    config.pause_event.wait()
    
    # Take a random sample out of population 
    contestants = random.sample(population, tournament_size)
    
    best_distance = float("inf")
    winner = []
    
    # Determine the best one out of the sample
    for contestant in contestants:
       # Pause / Resume / Stop
       if config.stop_event.is_set():
            raise StopAlgorithmException()
       config.pause_event.wait()
         
       distance = fitness(contestant)
       if  distance < best_distance:
           best_distance = distance
           winner = contestant
    return winner 

def elite_selection(population, elite_size):
    elite = []
    for solution in population:
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
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
    # Pause / Resume / Stop
    if config.stop_event.is_set():
            raise StopAlgorithmException()
    config.pause_event.wait()
        
    # Calculate fitness for each solution
    distances = []
    for solution in population:
        # Pause / Resume / Stop
        if config.stop_event.is_set():
            raise StopAlgorithmException()
        config.pause_event.wait()
        distances.append(fitness(solution)) 
        
    distance_of_all = sum(distances)
    
    # Calculate cumulative probabilities in one step
    cumulative_distances = []
    cumulative_sum = 0
    for distance in distances:
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        cumulative_sum += distance / distance_of_all
        cumulative_distances.append(cumulative_sum)
    
    # Use binary search for faster selection
    rand = random.random()
    index = bisect.bisect_left(cumulative_distances, rand)
    return population[index]


# Crossovers
def ordered_crossover(parent1,  parent2):
    # Remove last city since it's the same as the first
    parent1 = parent1[:-1]
    parent2 = parent2[:-1]
    
    # Make a list of the same size as parents
    offspring = [None] * len(parent1)
    
    # Pause / Resume / Stop
    if config.stop_event.is_set():
        raise StopAlgorithmException()
    config.pause_event.wait()
        
    # Take a random slice from parent 1
    start_position = random.randint(0, len(parent1) - 1)
    end_position = random.randint(0, len(parent1) - 1)
    if start_position > end_position:
        start_position, end_position = end_position, start_position
    sub_parent1 = parent1[start_position:end_position]
    
    # Take all the numbers from parent 2 that were not taken yet
    sub_parent2 = [] 
    for x in parent2: 
        # Pause / Resume / Stop
        if config.stop_event.is_set():
            raise StopAlgorithmException()
        config.pause_event.wait()
        
        if x not in sub_parent1:  
            sub_parent2.append(x)
    
    # Set numbers from parent 1 in the same position in offspring
    offspring[start_position:end_position] = sub_parent1
    
    # Fill up all the gaps with numbers from parent 2
    index = 0
    for i in range(len(offspring)):
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
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
    mapping = {}  # Initialize an empty dictionary
    for i in range(start, end):
        # Pause / Resume / Stop
        if config.stop_event.is_set():
            raise StopAlgorithmException()
        config.pause_event.wait()
        mapping[parent1[i]] = parent2[i]
    
    # Fill the remaining positions
    for i in range(len(parent2)):
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        if offspring[i] is None:
            value = parent2[i]
            while value in mapping and value in offspring:
                # Pause / Resume / Stop
                if config.stop_event.is_set():
                    raise StopAlgorithmException()
                config.pause_event.wait()
                
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
        
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        # Follow the cycle until we return to the start
        while not visited[current]:
            # Pause / Resume / Stop
            if config.stop_event.is_set():
                    raise StopAlgorithmException()
            config.pause_event.wait()
            
            visited[current] = True
            # Place the element from parent1 in the offspring
            offspring[current] = parent1[current]
            # Move to the corresponding position in Parent 2
            current = parent2.index(parent1[current])
        
        # If any positions remain unfilled, swap to Parent 2
        for i in range(len(offspring)):
            # Pause / Resume / Stop
            if config.stop_event.is_set():
                raise StopAlgorithmException()
            config.pause_event.wait()
            
            if offspring[i] is None:
                offspring[i] = parent2[i]

    # Re-add the first city to complete the loop
    offspring.append(offspring[0])

    return offspring


# Mutation
def mutation_swap(mutation_probability, child):
    solution = child.copy()
    if random.random() <= mutation_probability:
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        # Get two random cities in the solution
        first_city_index = random.randint(1, len(solution) - 2)
        second_city_index = random.randint(1, len(solution) - 2)
        first_city = solution[first_city_index]
        second_city = solution[second_city_index]
        
        # Swap those two cities places
        solution[first_city_index] = second_city
        solution[second_city_index] = first_city
    return solution

def mutation_inversion(mutation_probability, child):
    solution = child.copy()
    if random.random() <= mutation_probability:
        # Pause / Resume / Stop
        if config.stop_event.is_set():
                raise StopAlgorithmException()
        config.pause_event.wait()
        
        # Get two random cities in the solution
        first_index = random.randint(1, len(solution) - 2)
        last_index = random.randint(1, len(solution) - 2)

        # Ensure first_index is less than last_index
        if first_index > last_index:
            first_index, last_index = last_index, first_index

        # Invert the range
        solution[first_index:last_index] = solution[first_index:last_index][::-1]
    return solution


# Parents selection
def select_parents(population, selection, tournament_size):
    # Pause / Resume / Stop
    if config.stop_event.is_set():
            raise StopAlgorithmException()
    config.pause_event.wait()
    
    if selection == 1:
        selections = []
        for _ in range(2):
            # Pause / Resume / Stop
            if config.stop_event.is_set():
                raise StopAlgorithmException()
            config.pause_event.wait()
            
            selections.append(roulette_selection(population))
        return random.sample(selections, 2)
    
    elif selection == 2:
        # Pause / Resume / Stop
        if config.stop_event.is_set():
            raise StopAlgorithmException()
        config.pause_event.wait()
        
        selections = []
        for _ in range(2):
            selections.append(tournament(population, tournament_size))
        return random.sample(selections, 2)