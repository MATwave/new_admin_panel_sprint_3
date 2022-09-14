import dotenv
import os

def return_dsl() -> dict:
    '''
    Возвращает словарь DSN (Data Source Name) для подключения к БД
    '''
    dotenv.load_dotenv()
    dsn = {'psql': {'dbname': os.environ.get('POSTGRES_DB'),
                    'user': os.environ.get('POSTGRES_USER'),
                    'password': os.environ.get('POSTGRES_PASSWORD'),
                    'host': os.environ.get('DB_HOST'),
                    'port': os.environ.get('DB_PORT')},

           'es': {'host': os.environ.get('ELASTIC_HOST')
                  }
           }

    return dsn