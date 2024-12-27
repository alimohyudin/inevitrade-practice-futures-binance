# MACD Optimization Project

This project implements a parameter optimization algorithm for the MACD trading strategy using historical data for the BTC/USDT pair. The goal is to enhance the performance of the strategy by fine-tuning its parameters based on 12 months of data from 2024.

## Project Structure

```
macd-optimization-project
├── src
│   ├── trader.py                # Main logic for running the MACD strategy
│   ├── strategy
│   │   └── MACDStrategy.py      # Implementation of the MACD trading strategy
│   ├── data
│   │   └── BTCUSDT-3min-1year-2024.csv  # Historical trading data
│   └── utils
│       └── optimization.py       # Functions for optimizing strategy parameters
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd macd-optimization-project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the MACD strategy with parameter optimization, execute the following command:

```
python src/trader.py
```

This will load the historical data, run the strategy with various parameter combinations, and output the results, including the best-performing parameters.

## Strategy Overview

The MACD (Moving Average Convergence Divergence) strategy is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price. The strategy generates buy and sell signals based on the crossover of these moving averages.

## Optimization Process

The optimization process involves testing different combinations of parameters for the MACD strategy to identify the set that yields the highest profit. This may include techniques such as grid search or genetic algorithms implemented in `src/utils/optimization.py`.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.