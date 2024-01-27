import configparser


class Configuration:
    config = configparser.ConfigParser()

    def __init__(self, configfile):
        self.config.read(configfile, encoding='UTF-8')

    def read(self, section, key):
        return self.config[section][key]
