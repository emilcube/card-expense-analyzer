import os
import pandas as pd
import re

from config_reader import Config

def convert_balance(value):
    if pd.isna(value):
        return None
    value = str(value).replace('.', '').replace(',', '.')
    return float(value)

def convert_to_datetime(time_str):
    return pd.to_datetime(time_str, format="%H:%M %d.%m.%Y")

def main_function(config):

    folder_data_path = folder_data_path = config.folder_data_path # 'data'
    parsed_data_filename = folder_data_path = config.parsed_data_filename
    raw_data_filename = config.online_mode['raw_data_filename']

    #full_input_filepath = f"{folder_data_path}/{raw_data_filename}"
    full_input_filepath = os.path.join(folder_data_path, raw_data_filename)

    #output_file = f'{folder_data_path}/{parsed_data_filename}'
    full_output_filepath = os.path.join(folder_data_path, parsed_data_filename)

    df = pd.read_csv(full_input_filepath)
    df['message'] = df['message'].str.strip()

    #pattern = r"(🎉 Пополнение|💸 Оплата)\s*\|\s*(➕|➖)\s*([\d,.]+ UZS)\s*\|\s*📍\s*([^|]+)\s*\|\s*💳\s*([^\|]+)\s*\|\s*🕓\s*([^|]+)\s*\|\s*💰\s*([\d,.]+ UZS)"
    #pattern = r"(🎉 Пополнение|💸 Оплата)\s*\|\s*(➕|➖)\s*([\d,.]+) UZS\s*\|\s*📍\s*([^|]+)\s*\|\s*💳\s*([^\|]+)\s*\|\s*🕓\s*([^|]+)\s*\|\s*💰\s*([\d,.]+) UZS"
    pattern = r"(🎉|💸)\s*\S+\s*\|\s*(➕|➖)\s*([\d,.]+) UZS\s*\|\s*📍\s*([^|]+)\s*\|\s*💳\s*([^\|]+)\s*\|\s*🕓\s*([^|]+)\s*\|\s*💰\s*([\d,.]+) UZS"


    # #skip
    # skip = "💸 Операция | ➖ 50.000,00 UZS | 📍 XXXX | 💳 HUMOCARD *9999 | 🕓 22:21 17.07.2021 | 💰 108.100,51 UZS"
    # # pass
    # passs =  "💸 Оплата | ➖ 600,00 UZS | 📍 XXXX | 💳 HUMOCARD *9999 | 🕓 21:21 16.07.2021 | 💰 321.321,51 UZS"

    # match = re.fullmatch(pattern, skip)
    # if match:
    #     print("The string matches the pattern.")
    # else:
    #     print("The string does not match the pattern.")
    # exit(666)

    extracted_data = df['message'].str.extract(pattern)
    filtered_data = extracted_data.dropna()

    if not filtered_data.empty:
        df_filtered = df.loc[filtered_data.index].join(filtered_data)

        df_filtered['transaction_type'] = df_filtered[0].apply(lambda x: 1 if x == '🎉' else 0)

        # renaming
        df_filtered.columns = ['date', 'offset_id', 'message', '_type', '_sign', 'amount', 'location', 'card', 'time', 'balance', 'transaction_type']

        df_filtered = df_filtered.drop(columns=['_type', '_sign', 'message'])

        df_filtered = df_filtered.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        df_filtered['amount'] = df_filtered['amount'].apply(convert_balance)
        df_filtered['balance'] = df_filtered['balance'].apply(convert_balance)

        df_filtered['time'] = df_filtered['time'].apply(convert_to_datetime)
        
        df_filtered['date'] = pd.to_datetime(df['date'])
        df_filtered['date'] = df_filtered['date'] + pd.Timedelta(hours=5)
        df_filtered['date'] = df_filtered['date'].dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        df_filtered = df_filtered.rename(columns={'date': 'tg_message_time', 'time': 'transaction_time'})

        #print(df_filtered.head())
        df_filtered.to_csv(full_output_filepath, index=False, encoding='utf-8')
    else:
        print("there is no message with that template")

if __name__ == "__main__":
    config = Config()
    main_function(config)