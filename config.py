import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql://root:TNNCAVqwzCkkTJWKwwhTjhzjKAuWDpMW@junction.proxy.rlwy.net:17227/railway')
    SECRET_KEY = os.getenv('SECRET_KEY', 'M0i1Xc$GfPw3Yz@2SbQ9lKpA5rJhDtE7')  # Usa una clave por defecto en caso de que no esté en .env

    @staticmethod
    def get_db_params():
        result = urlparse(Config.DATABASE_URL)
        return {
            'host': result.hostname,
            'port': result.port,
            'user': result.username,
            'password': result.password,
            'database': result.path[1:],  # Omitir el primer carácter que es '/'
        }
