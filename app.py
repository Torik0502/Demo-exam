from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.secret_key = 'secretkey2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# таблица пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    fio = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)


# валидация
def valid_login(login):
    return re.match(r'^[a-zA-Z0-9]{6,}$', login) is not None

def valid_password(password):
    return len(password) >= 8

def valid_phone(phone):
    return re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone) is not None

def valid_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        fio = request.form['fio']
        phone = request.form['phone']
        email = request.form['email']
        
        if not valid_login(login):
            error = 'Логин: 6+ символов, только латиница и цифры'
        elif not valid_password(password):
            error = 'Пароль: 8+ символов'
        elif not valid_phone(phone):
            error = 'Телефон: формат 8(999)123-45-67'
        elif not valid_email(email):
            error = 'Неверный формат email'
        elif User.query.filter_by(login=login).first():
            error = 'Логин уже занят'
        else:
            user = User(login=login, password=password, fio=fio, phone=phone, email=email)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        # вход в админку
        if login == 'Admin26' and password == 'Demo20':
            session['admin'] = True
            return redirect(url_for('admin'))
        
        user = User.query.filter_by(login=login, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            error = 'Неверный логин или пароль'
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


#заглушка для админки
@app.route('/admin')
def admin():
    return "<h1>Админ-панель в разработке</h1>"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)