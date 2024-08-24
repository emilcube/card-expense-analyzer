import os
import yaml

#PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # src
#CONFIG_PATH = os.path.join(PROJECT_ROOT, '..', 'config.yaml') # go back

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # CardExpenseAnalyzer
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.yaml')  # Теперь правильный путь к config.yaml

class Config:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.is_online_mode_getting_tg_messages = False
        self.folder_data_path = ''
        self.parsed_data_filename = ''

        self.dash_host = ''
        self.dash_port = 0
        self.dash_debug_mode = True

        self.online_mode = {
            'api_id': '',
            'api_hash': '',
            'session_name': '',
            'raw_data_filename': ''
        }

        self.offline_mode = {
            'messages_file_filepath': ''
        }

        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)

        self.is_online_mode_getting_tg_messages = config.get('is_online_mode_getting_tg_messages', self.is_online_mode_getting_tg_messages)
        self.folder_data_path = config.get('folder_data_path', self.folder_data_path)
        self.parsed_data_filename = config.get('parsed_data_filename', self.parsed_data_filename)

        self.dash_host = config.get('dash_host', self.dash_host)
        self.dash_port = config.get('dash_port', self.dash_port)
        self.dash_debug_mode = config.get('dash_debug_mode', self.dash_debug_mode)

        self.online_mode.update(config.get('online_mode', {}))
        self.offline_mode.update(config.get('offline_mode', {}))

        if not os.path.isabs(self.folder_data_path):
            # 'data' ===> c:\...\Desktop\CardExpenseAnalyzer\data
            self.folder_data_path = os.path.join(PROJECT_ROOT, self.folder_data_path)
            #print(self.folder_data_path)

        if not os.path.exists(self.folder_data_path):
            os.makedirs(self.folder_data_path)

    def __repr__(self):
        return (f"Config(is_online_mode_getting_tg_messages={self.is_online_mode_getting_tg_messages}, "
                f"folder_data_path='{self.folder_data_path}', parsed_data_filename='{self.parsed_data_filename}', "
                f"online_mode={self.online_mode}, offline_mode={self.offline_mode})")

if __name__ == "__main__":
    # from config_reader import CONFIG_PATH, Config
    # from config_reader import Config
    config = Config()

    print(PROJECT_ROOT)
    print(CONFIG_PATH)

    #print(config.is_online_mode_getting_tg_messages)
    #print(config.folder_data_path)
    #print(config.online_mode['api_id'])
    #print(config.offline_mode['messages_file_filepath'])

    #print(config)
