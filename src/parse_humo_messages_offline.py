import os
import json
from datetime import datetime
import pandas as pd
import re

from config_reader import Config, PROJECT_ROOT

def parse_card_and_time(input_str):
    parts = input_str.split('\n')
    card = parts[1].strip()  # Get the card information
    card = card.split(' ', 1)[1]

    time_str = parts[2].strip()  # Get the time information
    # remove the emoji (🕓) and any extra spaces
    time_str = time_str.split(' ', 1)[1]  # Splitting on the first space to remove emoji
    time_obj = datetime.strptime(time_str, "%H:%M %d.%m.%Y")
    formatted_time = time_obj.strftime("%Y-%m-%d %H:%M:%S")

    return card, formatted_time

def parse_currency_string(currency_str):
    # remove any non-numeric characters except for commas and periods
    numeric_str = ''.join(c for c in currency_str if c.isdigit() or c in ',.')
    
    # replace the last comma with a dot to match the float format
    if ',' in numeric_str:
        numeric_str = numeric_str.replace('.', '', numeric_str.rfind(','))
        numeric_str = numeric_str.replace(',', '.')
    return float(numeric_str)

def extract_message_info(message):
    transaction_type = None
    amount = None
    location = None
    card = None
    time = None
    balance = None

    try:
        # validation
        if (not isinstance(message, list) or
            len(message) != 9 or message[0] not in ("💸 ", "🎉 ") or message[4] != "\n📍 " or message[2] not in ("\n➖ ", "\n➕ ") or
            not isinstance(message[1], dict) or not isinstance(message[3], dict) or not isinstance(message[5], dict) or not isinstance(message[7], dict)
            ):
            return transaction_type, amount, location, card, time, balance

        transaction_type = 1 if message[1]['text'] == "Пополнение" else 0
        amount = parse_currency_string(message[3]['text'])
        location = message[5]['text']
        card, time = parse_card_and_time(message[6])
        balance = parse_currency_string(message[7]['text'])

    except (ValueError, KeyError, IndexError, TypeError) as e:
        print(f"Error extracting message info: {e}")
        return transaction_type, amount, location, card, time, balance

    return transaction_type, amount, location, card, time, balance

def convert_datetime_format(original_datetime_str):
    datetime_obj = datetime.strptime(original_datetime_str, "%Y-%m-%dT%H:%M:%S")
    formatted_datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime_str

def main_function(config):
    folder_data_path = config.folder_data_path
    parsed_data_filename = config.parsed_data_filename
    messages_file_filepath = config.offline_mode['messages_file_filepath']

    #PROJECT_ROOT
    full_input_filepath = os.path.join(PROJECT_ROOT, messages_file_filepath)
    #print(full_input_filepath)

    #output_file = f'{folder_data_path}/{parsed_data_filename}'
    full_output_filepath = os.path.join(folder_data_path, parsed_data_filename)

    with open(full_input_filepath, "r", encoding='utf-8') as file: # messages_file_filepath
        data_raw = json.load(file)

    parsed_data = []

    data = data_raw['messages']

    for entry in data:
        
        if not entry['text']:
            continue

        message_info = extract_message_info(entry['text'])
        card = message_info[3]
        if card is None:
            continue
        parsed_data.append({
            'tg_message_time': convert_datetime_format(entry['date']),
            'offset_id': entry['id'],
            'amount': message_info[1],
            'location': message_info[2],
            'card': message_info[3],
            'transaction_time': message_info[4],
            'balance': message_info[5],
            'transaction_type': message_info[0],
        })

    df_filtered = pd.DataFrame(parsed_data)

    df_filtered.to_csv(full_output_filepath, index=False, encoding='utf-8')

if __name__ == "__main__":
    config = Config()
    main_function(config)