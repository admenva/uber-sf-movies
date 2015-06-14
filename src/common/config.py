import os
import yaml


def load_config():
    '''
    Loads the configuration file from common/config.yaml
    '''
    config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    with open(config_file_path, 'r') as config_file:
        return yaml.load(config_file)


config = load_config()
