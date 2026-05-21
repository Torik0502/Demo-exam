from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#заглушки
@app.route('/register')
def register():
    return "<h1>Страница регистрации в разработке</h1>"

@app.route('/login')
def login():
    return "<h1>Страница входа в разработке</h1>"

if __name__ == '__main__':
    app.run(debug=True)