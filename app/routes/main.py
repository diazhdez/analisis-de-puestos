from flask import Blueprint, render_template, redirect, url_for, session
from app.routes.admin import get_admin
from app.routes.user import get_user

main_routes = Blueprint('main', __name__)


# Ruta principal
@main_routes.route('/')
def index():
    if 'email' in session:
        email = session['email']
        admin = get_admin(email)
        user = get_user(email)

        if admin:
            return redirect(url_for('admin.admin'))
            
        if user:
            return redirect(url_for('user.user'))
        
    else:
        return render_template('index.html')
