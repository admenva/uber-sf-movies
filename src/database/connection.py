from motor import MotorClient

from common.config import config


class MongoConnection(object):
    '''
    Creates an asynchronous connection to MongoDB using Motor. If no parameters are passed to the
    constructor, they are read from the config file in common/config.yaml
    '''

    def __init__(self, **kwargs):
        connection_info = config['mongo_connection']
        connection_info.update(**kwargs)

        connection_string = 'mongodb://{user}:{password}@{host}:{port}/{name}'.format(**connection_info)
        self._db = MotorClient(connection_string)[connection_info['name']]

    def get_db_client(self):
        return self._db


motor_client = MongoConnection().get_db_client()
