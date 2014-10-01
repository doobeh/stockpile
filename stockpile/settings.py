class Config(object):
    SECRET_KEY = 'SHH!'
    STORES = {
    '001': 'Graceway IGA',
    '002': 'Wholesale',
    '003': 'Graceway Gourmet',
    }

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    CACHE_TYPE = 'simple'


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://sales:margin@10.0.0.10/sales'
    SQLALCHEMY_ECHO = True
    CACHE_TYPE = 'null'
    WTF_CSRF_ENABLED = True
