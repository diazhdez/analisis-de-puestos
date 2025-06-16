from flask import Flask, g
import pymysql
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de la conexión a la base de datos usando la URL
    db_params = Config.get_db_params()

    def get_db_connection():
        if 'db' not in g:
            g.db = pymysql.connect(
                host=db_params['host'],
                user=db_params['user'],
                password=db_params['password'],
                db=db_params['database'],
                port=db_params['port'],
                cursorclass=pymysql.cursors.DictCursor
            )
        return g.db

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            try:
                db.close()
            except pymysql.MySQLError as e:
                print(f"Error al cerrar la conexión: {e}")

    app.get_db_connection = get_db_connection

    with app.app_context():
        # Importa y registra los Blueprints
        from app.routes.main import main_routes
        from app.routes.user import user_routes
        from app.routes.admin import admin_routes
        from app.routes.session import session_routes
        from app.routes.errors import errors

        app.register_blueprint(main_routes)
        app.register_blueprint(user_routes)
        app.register_blueprint(admin_routes)
        app.register_blueprint(session_routes)
        app.register_blueprint(errors)

    return app
