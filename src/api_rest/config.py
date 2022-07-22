# Configuraciones necesarias para la API REST
class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'comechinga1'
    MYSQL_DB = 'challenge_payment_services'

config = {
    'development': DevelopmentConfig
}