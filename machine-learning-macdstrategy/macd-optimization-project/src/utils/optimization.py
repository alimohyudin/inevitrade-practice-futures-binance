def grid_search_optimization(param_grid, run_strategy):
    best_profit = float('-inf')
    best_params = None

    for params in param_grid:
        profit, _ = run_strategy(params)
        if profit > best_profit:
            best_profit = profit
            best_params = params

    return best_params, best_profit

def genetic_algorithm_optimization(param_grid, run_strategy, population_size=10, generations=5):
    import random

    def create_individual(param_grid):
        return random.choice(param_grid)

    def mutate(individual):
        mutation_rate = 0.1
        if random.random() < mutation_rate:
            return random.choice(param_grid)
        return individual

    population = [create_individual(param_grid) for _ in range(population_size)]
    
    for generation in range(generations):
        population = sorted(population, key=lambda x: run_strategy(x)[0], reverse=True)
        next_generation = population[:population_size // 2]

        while len(next_generation) < population_size:
            parent = random.choice(next_generation)
            child = mutate(parent)
            next_generation.append(child)

        population = next_generation

    best_individual = max(population, key=lambda x: run_strategy(x)[0])
    return best_individual, run_strategy(best_individual)[0]