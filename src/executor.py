from config_reader import Config
import get_humo_messages_online
import parse_humo_messages_online
import parse_humo_messages_offline

def main_function(config):
    #print(type(config.is_online_mode_getting_tg_messages))
    #print(config.is_online_mode_getting_tg_messages)

    if config.is_online_mode_getting_tg_messages:
        get_humo_messages_online.main_function(config)
        parse_humo_messages_online.main_function(config)
    else:
        parse_humo_messages_offline.main_function(config)

if __name__ == "__main__":
    config = Config()
    main_function(config)
