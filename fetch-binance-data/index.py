import os
import shutil
from datetime import datetime, timedelta
from binance.client import Client

# Replace with your Binance API key and secret
API_KEY = ''
API_SECRET = ''

client = Client(API_KEY, API_SECRET)

def clear_directory(output_folder, symbol):
    try:
        # Read the contents of the directory
        files = os.listdir(os.path.join(output_folder, symbol))

        # Iterate through each file and delete it
        for file in files:
            file_path = os.path.join(output_folder, symbol, file)

            # Check if it's a file and delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        print('Directory cleared successfully.')
    except Exception as err:
        print('Error clearing directory:', err)

def increment_date_to_end_of_month(start_date):
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    next_month = current_date.replace(day=28) + timedelta(days=4)  # this will never fail
    end_of_month = next_month - timedelta(days=next_month.day)
    remaining_days = (end_of_month - current_date).days + 1
    days_to_add = min(3, remaining_days)
    incremented_date = current_date + timedelta(days=days_to_add - 1)  # Subtract 1 to get the correct end date

    return incremented_date.strftime('%Y-%m-%d')

def fetch_kline_data_in_intervals(symbol, start_date, end_date, interval=Client.KLINE_INTERVAL_3MINUTE, output_folder='./data'):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    while start_date < end_date:
        next_date = increment_date_to_end_of_month(start_date.strftime('%Y-%m-%d'))
        next_date = datetime.strptime(next_date, '%Y-%m-%d')

        klines = client.get_historical_klines(symbol, interval, start_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'))

        # Save the data to a CSV file
        output_file = os.path.join(output_folder, symbol, f'{symbol}_{start_date.strftime("%Y-%m-%d")}_to_{next_date.strftime("%Y-%m-%d")}.csv')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            for kline in klines:
                f.write(','.join(map(str, kline)) + '\n')

        print(f"Fetched data from {start_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}")

        start_date = next_date + timedelta(days=1)

def myfetch(symbol, start_date, end_date):
    fetch_kline_data_in_intervals(symbol, start_date, end_date)

# Example usage
if __name__ == '__main__':
    output_folder = './data'
    symbol = 'BTCUSDT'
    start_date = '2024-01-01'
    end_date = '2024-02-01'

    clear_directory(output_folder, symbol)
    new_date = increment_date_to_end_of_month(start_date)
    print(f"New date: {new_date}")

    myfetch(symbol, start_date, end_date)