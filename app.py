from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import re #для проверок логина и тд

app = Flask(__name__)
app.secret_key = 'secretkey2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#таблица пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    fio = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
#таблица заявок
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Новое')
    review = db.Column(db.Text, nullable=True)


#валидация
def valid_login(login):
    return re.match(r'^[a-zA-Z0-9]{6,}$', login) is not None

def valid_password(password):
    return len(password) >= 8

def valid_phone(phone):
    return re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone) is not None

def valid_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None

def valid_date(date):
    return re.match(r'^\d{2}\.\d{2}\.\d{4}$', date) is not None


#роуты страничек
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
            error = 'Пароль: минимум 8 символов'
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
        
        #вход в админку
        if login == 'Admin26' and password == 'Demo20':
            session['admin'] = True
            return redirect(url_for('admin'))
        
        #пользовательский вход
        user = User.query.filter_by(login=login, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('my'))
        else:
            error = 'Неверный логин или пароль'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    error = None
    if request.method == 'POST':
        course = request.form['course_name']
        date = request.form['start_date']
        payment = request.form['payment_method']
        
        if not valid_date(date):
            error = 'Неверный формат даты. ДД.ММ.ГГГГ'
        else:
            req = Request(
                user_id=session['user_id'],
                course_name=course,
                start_date=date,
                payment_method=payment,
                status='Новое'
            )
            db.session.add(req)
            db.session.commit()
            return redirect(url_for('my'))
    
    return render_template('create.html', error=error)

@app.route('/my')
def my():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    requests = Request.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_requests.html', requests=requests)

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    all_requests = Request.query.all()
    return render_template('admin.html', requests=all_requests)

@app.route('/status/<int:rid>/<status>')
def status(rid, status):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    req = Request.query.get(rid)
    if req:
        req.status = status
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/review/<int:rid>', methods=['GET', 'POST'])
def review(rid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    req = Request.query.get(rid)
    if not req or req.user_id != session['user_id']:
        return redirect(url_for('my'))
    
    if request.method == 'POST':
        req.review = request.form['review']
        db.session.commit()
        return redirect(url_for('my'))
    
    return render_template('review.html', req=req)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('База данных создана!')
    app.run(debug=True)