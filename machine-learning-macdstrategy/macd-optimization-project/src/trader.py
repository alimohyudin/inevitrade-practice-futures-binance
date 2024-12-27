import backtrader as bt
from datetime import datetime, date, timedelta
from strategy.MACDStrategy import MACDStrategy
import itertools
from deap import base, creator, tools, algorithms
import random


def get_last_date_of_month(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_date = next_month - timedelta(days=1)
    return last_date


def run_strategy(params):
    cerebro = bt.Cerebro()
    strategy_params = {k: v for k, v in params.items() if k not in ['start_month', 'end_month']}
    cerebro.addstrategy(MACDStrategy, **strategy_params)

    data = bt.feeds.GenericCSVData(
        dataname='./src/data/BTCUSDT-3min-1year-2024.csv',
        dtformat='%m-%d-%YT%H:%M:%S.000Z',
        timeframe=bt.TimeFrame.Minutes,
        fromdate=datetime(2024, params['start_month'], 1),
        todate=datetime(2024, params['end_month'], get_last_date_of_month(2024, params['end_month']).day),
        compression=1,
        openinterest=-1,
    )
    cerebro.adddata(data)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.0)

    starting_cash = cerebro.broker.getvalue()
    cerebro.run()
    ending_cash = cerebro.broker.getvalue()

    profit = ending_cash - starting_cash
    return profit


def evaluate(individual):
    params = {
        'start_month': 10,
        'end_month': 12,
        'long_stoploss': individual[0],
        'long_takeprofit': individual[1],
        'short_stoploss': individual[2],
        'short_takeprofit': individual[3],
        'lookback_bars': individual[4],
    }
    profit = run_strategy(params)
    return profit,


def main():
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    # toolbox.register("attr_start_month", random.randint, 1, 11)  # Ensure start_month is between 1 and 11
    # toolbox.register("attr_end_month", lambda: random.randint(toolbox.attr_start_month() + 1, 12))  # Ensure end_month is greater than start_month
    toolbox.register("attr_long_stoploss", random.randint, 1, 10)
    toolbox.register("attr_long_takeprofit", random.randint, 1, 10)
    toolbox.register("attr_short_stoploss", random.randint, 1, 10)
    toolbox.register("attr_short_takeprofit", random.randint, 1, 10)
    toolbox.register("attr_lookback_bars", random.randint, 10, 100)

    toolbox.register("individual", tools.initCycle, creator.Individual,
                     (toolbox.attr_long_stoploss,
                      toolbox.attr_long_takeprofit, toolbox.attr_short_stoploss, toolbox.attr_short_takeprofit,
                      toolbox.attr_lookback_bars), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutPolynomialBounded, low=[1, 1, 1, 1, 10], up=[10, 10, 10, 10, 100], eta=0.1, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=50)
    ngen = 40
    cxpb = 0.5
    mutpb = 0.2

    algorithms.eaSimple(population, toolbox, cxpb, mutpb, ngen, stats=None, halloffame=None, verbose=True)

    best_individual = tools.selBest(population, k=1)[0]
    print(f"Best individual is: {best_individual}")
    print(f"With fitness: {best_individual.fitness.values[0]}")


if __name__ == '__main__':
    main()