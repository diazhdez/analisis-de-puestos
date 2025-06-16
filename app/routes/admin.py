from flask import Blueprint, current_app, render_template, url_for, redirect, flash, session, request
import pymysql
import bcrypt

admin_routes = Blueprint('admin', __name__)

# Obtener la conexión a la base de datos
connection = current_app.get_db_connection()


# Función para obtener un administrador por su correo electrónico
def get_admin(email):
    connection = current_app.get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM admin WHERE email = %s", (email,))
                admin = cursor.fetchone()
                return admin
        except pymysql.MySQLError as err:
            print(f"Error al obtener administrador: {err.args[0]}, {err.args[1]}")
    return None


# Ruta para el administrador
@admin_routes.route('/admin/')
def admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            return render_template('admin.html', admin=admin)
    return redirect(url_for('main.index'))


# Ruta para registrar
@admin_routes.route('/admin/registro/')
def registro():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            return render_template('registro.html')
    else:
        return redirect(url_for('main.index'))


# Ruta para registrar a los usuarios
@admin_routes.route('/register_user/', methods=['POST', 'GET'])
def register_user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                connection = current_app.get_db_connection()
                try:
                    name = request.form['name']
                    email = request.form['email']
                    password = request.form['password']
                    phone = request.form['phone']

                    with connection.cursor() as cursor:
                        # Verificar si el Usuario ya existe en la base de datos
                        cursor.execute(
                            "SELECT * FROM user WHERE email = %s", (email,))
                        existing_user = cursor.fetchone()

                        if existing_user is None:
                            # Hash de la contraseña
                            hashpass = bcrypt.hashpw(
                                password.encode('utf-8'), bcrypt.gensalt())

                            # Insertar el nuevo Usuario en la base de datos
                            cursor.execute(
                                "INSERT INTO user (name, email, password, phone) VALUES (%s, %s, %s, %s)",
                                (name, email, hashpass, phone)
                            )
                            connection.commit()

                            flash('Se registró el Usuario correctamente')
                            return redirect(url_for('admin.registro'))
                        else:
                            flash('El correo ya está en uso')
                            return redirect(url_for('admin.registro'))
                except pymysql.MySQLError as err:
                    print(f"Error al registrar Usuario: {err.args[0]}, {err.args[1]}")
                    connection.rollback()
                finally:
                    connection.close()
        else:
            return redirect(url_for('main.index'))

    return redirect(url_for('main.index'))


# Ruta para registrar administradores
@admin_routes.route('/register_admin/', methods=['POST', 'GET'])
def register_admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                connection = current_app.get_db_connection()
                try:
                    name = request.form['name']
                    email = request.form['email']
                    password = request.form['password']
                    phone = request.form['phone']

                    with connection.cursor() as cursor:
                        # Verificar si el administrador ya existe en la base de datos
                        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
                        existing_admin = cursor.fetchone()

                        if existing_admin is None:
                            # Hash de la contraseña
                            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                            # Insertar el nuevo administrador en la base de datos
                            cursor.execute(
                                "INSERT INTO admin (name, email, password, phone) VALUES (%s, %s, %s, %s)",
                                (name, email, hashpass, phone)
                            )
                            connection.commit()

                            flash('Se registró el administrador correctamente')
                            return redirect(url_for('admin.registro'))
                        else:
                            flash('El correo ya está en uso')
                            return redirect(url_for('admin.registro'))
                except pymysql.MySQLError as err:
                    print(f"Error al registrar administrador: {err.args[0]}, {err.args[1]}")
                    connection.rollback()
                finally:
                    connection.close()
        else:
            return redirect(url_for('main.index'))

    return redirect(url_for('admin.registro'))


# Ruta para ver Usuarios
@admin_routes.route('/admin/listas/usuarios/')
def users():
    if 'email' in session:
        email = session['email']
        admin = get_admin(email)
        if admin:
            connection = current_app.get_db_connection()
            try:
                with connection.cursor() as cursor:

                    cursor.execute("SELECT * FROM user")

                    users = cursor.fetchall()

            except pymysql.MySQLError as err:
                print(f"Error al obtener usuarios: {err}")
            finally:
                cursor.close()
            
            return render_template('users.html', users=users)
    else:
        return redirect(url_for('main.index'))


# Ruta para eliminar un usuario
@admin_routes.route('/delete/user/<int:user_id>/', methods=['POST'])
def delete_user(user_id):
    connection = current_app.get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Eliminar CondicionesTrabajo relacionados con el usuario
            cursor.execute("""
                DELETE FROM condicionestrabajo 
                WHERE IdPerfil IN (
                    SELECT IdPerfil 
                    FROM perfilpuesto 
                    WHERE IdPuesto IN (
                        SELECT IdPuesto 
                        FROM puestos 
                        WHERE DepartamentoId IN (
                            SELECT IdDepartamento 
                            FROM departamento 
                            WHERE IdArea IN (
                                SELECT IdArea 
                                FROM areas 
                                WHERE id = %s
                            )
                        )
                    )
                )
            """, (user_id,))

            # Eliminar perfiles de puesto relacionados con el usuario
            cursor.execute("""
                DELETE FROM perfilpuesto 
                WHERE IdPuesto IN (
                    SELECT IdPuesto 
                    FROM puestos 
                    WHERE DepartamentoId IN (
                        SELECT IdDepartamento 
                        FROM departamento 
                        WHERE IdArea IN (
                            SELECT IdArea 
                            FROM areas 
                            WHERE id = %s
                        )
                    )
                )
            """, (user_id,))

            # Eliminar puestos relacionados con el usuario
            cursor.execute("""
                DELETE FROM puestos 
                WHERE DepartamentoId IN (
                    SELECT IdDepartamento 
                    FROM departamento 
                    WHERE IdArea IN (
                        SELECT IdArea 
                        FROM areas 
                        WHERE id = %s
                    )
                )
            """, (user_id,))

            # Eliminar departamentos relacionados con el usuario
            cursor.execute("""
                DELETE FROM departamento 
                WHERE IdArea IN (
                    SELECT IdArea 
                    FROM areas 
                    WHERE id = %s
                )
            """, (user_id,))

            # Eliminar el área
            cursor.execute("DELETE FROM areas WHERE id = %s", (user_id,))

            # Eliminar el usuario
            cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))

            connection.commit()
            flash('Usuario eliminado correctamente', 'success')
    except pymysql.MySQLError as err:
        print("Error al eliminar usuario:", err)
        connection.rollback()
        flash('Error al eliminar usuario', 'error')
    finally:
        connection.close()
    return redirect(url_for('admin.users'))


# Ruta para ver Administradores
@admin_routes.route('/admin/listas/administradores/')
def admins():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            # Obtener la conexión de la aplicación
            connection = current_app.get_db_connection()
            try:
                # Crear un cursor para realizar operaciones en la base de datos
                with connection.cursor() as cursor:
                    # Ejecutar la consulta para seleccionar todos los administradores
                    cursor.execute("SELECT * FROM admin")

                    # Obtener todos los resultados de la consulta
                    admins = cursor.fetchall()

            except pymysql.MySQLError as err:
                print(f"Error al obtener administradores: {err}")
            finally:
                connection.close()
            
            return render_template('admins.html', admins=admins)
    else:
        return redirect(url_for('main.index'))


# Ruta para eliminar un administrador
@admin_routes.route('/delete/admin/<int:admin_id>/', methods=['POST'])
def delete_admin(admin_id):
    connection = current_app.get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Consulta para eliminar el administrador por ID
            cursor.execute("DELETE FROM admin WHERE id = %s", (admin_id,))
            connection.commit()
            flash('Administrador eliminado correctamente', 'success')
    except pymysql.MySQLError as err:
        print("Error al eliminar administrador:", err)
        connection.rollback()
        flash('Error al eliminar administrador', 'error')
    finally:
        connection.close()
    return redirect(url_for('admin.admins'))

