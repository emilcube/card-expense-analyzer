from telethon.sync import TelegramClient
import csv
import os

from config_reader import Config

def main_function(config):

    api_id = config.online_mode['api_id']
    api_hash = config.online_mode['api_hash']
    output_file = config.online_mode['raw_data_filename']
    session_name = config.online_mode['session_name']
    folder_data_path = config.folder_data_path # 'data'

    bot_username = 'HUMOcardbot' # official tg bot HUMO

    full_output_filepath = os.path.join(folder_data_path, output_file)

    client = TelegramClient(session_name, api_id, api_hash)

    def get_last_offset_id(file):
        """Извлекаем offset_id из последней строки файла CSV."""
        if not os.path.exists(file):
            return 0  # если файл не существует, начинаем с 0
        
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 1:
                return int(rows[-1][1])  # возвращаем offset_id последней записи
            else:
                return 0

    async def get_all_messages():
        await client.start()

        bot_entity = await client.get_entity(bot_username)

        # читаем последний сохраненный offset_id из файла
        last_offset_id = get_last_offset_id(full_output_filepath)

        all_messages = []

        # используем iter_messages для получения сообщений с определённого offset_id
        async for message in client.iter_messages(bot_entity, min_id=last_offset_id + 1):
            if message.message:
                all_messages.append(message)

        print(f"Total messages retrieved: {len(all_messages)}")

        # сортируем сообщения по возрастанию даты
        all_messages = sorted(all_messages, key=lambda x: x.date)

        with open(full_output_filepath, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # заголовки
            if file.tell() == 0:
                writer.writerow(["date", "offset_id", "message"])
            
            for message in all_messages:
                formatted_message = message.message.replace('\n', ' | ')
                writer.writerow([message.date, message.id, formatted_message])

        await client.disconnect()

    with client:
        client.loop.run_until_complete(get_all_messages())

if __name__ == "__main__":
    config = Config()
    main_function(config)