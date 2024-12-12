import pandas as pd
import math
import random

def parse_tsp(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        
    # Start and end of coordinates
    start_index = lines.index("NODE_COORD_SECTION\n") + 1
    end_index = lines.index("EOF\n")
    
    # Extract coordinate lines
    data_lines = lines[start_index:end_index]
    
    # Separate data into parts
    data = []
    for line in data_lines:
        parts = line.strip().split()
        x = float(parts[1])
        y = float(parts[2])
        data.append([x, y])
    df = pd.DataFrame(data, columns=['x', 'y'])
    return df

def distance_between(x1, x2, y1, y2):
    result = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return round(result, 3)

def random_solution(indexes):
    random.shuffle(indexes)
    return indexes

def fitness(solution):
    # [9, 1, 4, 0, 10, 3, 7, 8, 6, 5, 2]
    total_distance = 0
    if len(solution) > 1:
        for i in range(len(solution) - 1):
            # Calculate indexes
            current_index = solution[i]
            next_index = solution[i + 1]
            
            # Calculate Distance
            distance = distance_between(
                df.iloc[current_index]['x'], df.iloc[next_index]['x'],
                df.iloc[current_index]['y'], df.iloc[next_index]['y']
            )
            total_distance += distance
    return round(total_distance, 3)

def print_result(solution):
    for n in solution:
        if solution.index(n) != (len(solution) - 1):
            print(n, end=" ⇢  ")
        else:
            print(n)
    total_distance = fitness(solution)
    print(f"Distance: {total_distance}")
    
def greedy_solution(starting_point):
    remaining_indexes = indexes.copy()
    solution = [starting_point]
    
    while len(remaining_indexes) > 1:
        remaining_indexes.remove(starting_point)   
        shortest_distance = float('inf')
        next_city = -1
        
        for i in remaining_indexes:
            distance = distance_between(
                df.iloc[i]['x'], df.iloc[starting_point]['x'],
                df.iloc[i]['y'], df.iloc[starting_point]['y']
                )
            if distance < shortest_distance:
                shortest_distance = distance
                next_city = i
                
        solution.append(next_city)
        starting_point = next_city 
    return solution
        
    
df = parse_tsp('berlin11.tsp')
indexes = df.index.to_list()

print(df)
res = distance_between(df.iloc[0]['x'], df.iloc[1]['x'], df.iloc[0]['y'], df.iloc[1]['y'])
print(res)

print_result(greedy_solution(9))