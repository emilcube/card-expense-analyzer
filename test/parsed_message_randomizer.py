import json
import pandas as pd
import re
from datetime import datetime
import yaml
import os
import random

def load_data_from_csv(file_data_path):
    try:
        df = pd.read_csv(file_data_path)
        df['tg_message_time'] = pd.to_datetime(df['tg_message_time'], format='%Y-%m-%d %H:%M:%S')
        df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%Y-%m-%d %H:%M:%S')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=['card', 'tg_message_time', 'transaction_time', 'location', 'amount', 'transaction_type'])
        return df
    
def main_function():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    folder_data_path = config.get('folder_data_path')
    parsed_data_filename = config.get('parsed_data_filename')
    offline_mode = config.get('offline_mode', {})

    full_path = os.path.join(folder_data_path, parsed_data_filename)
    df = load_data_from_csv(full_path)
    
    df['transaction_type'] = [random.choice([0, 1]) for _ in range(len(df))]
    df['location'] = [random.choice(["OOO company1", "OOO company2", "OOO company3", "OOO company4", "OOO company5"]) for _ in range(len(df))]
    df['amount'] = [random.randint(1000, 100000) for _ in range(len(df))]
    df['card'] = [random.choice(["HUMOCARD *9999", "HUMOCARD *9991"]) for _ in range(len(df))]
    df['balance'] = 0
    df['offset_id'] = 0
    df.to_csv(full_path, index=False)
    print(df)

if __name__ == "__main__":
    main_function()