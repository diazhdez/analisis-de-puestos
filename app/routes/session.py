from flask import Blueprint, current_app, redirect, url_for, flash, session, request
import pymysql
import bcrypt

session_routes = Blueprint('session', __name__)

# Obtener la conexión a la base de datos
connection = current_app.get_db_connection()


@session_routes.route('/login/', methods=['POST'])
def login():
    connection = current_app.get_db_connection()
    try:
        email = request.form['email']
        password = request.form['password']

        with connection.cursor() as cursor:
            # Buscar en la tabla de admin
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            login_admin = cursor.fetchone()
            if login_admin and password:
                session['email'] = email
                return redirect(url_for('admin.admin'))

        with connection.cursor() as cursor:
            # Buscar en la tabla de users
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            login_user = cursor.fetchone()
            if login_user and bcrypt.checkpw(password.encode('utf-8'), login_user['password']):
                session['email'] = email
                return redirect(url_for('user.user'))

        flash('Correo o contraseña incorrectos')
        return redirect(url_for('main.index'))
    except pymysql.MySQLError as err:
        print(f"Error al iniciar sesión: {err.args[0]}, {err.args[1]}")
        flash('Hubo un error al iniciar sesión. Inténtalo de nuevo.')
        return redirect(url_for('main.index'))


# Ruta para cerrar sesión
@session_routes.route('/logout/')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('main.index'))
