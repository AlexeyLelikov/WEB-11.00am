import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, session, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash


# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts = dbase.getPostAnonce())

@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
        if not res:
            flash('Ошибка добавления статьи', category = 'error')
        else:
            flash('Статья добавлена успешно', category='success')

    return render_template('add_post.html', menu = dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

@app.route("/login")
def login():
    return render_template('login.html', menu=dbase.getMenu(), title= "Авторизация")

@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop("_flashes", None)
        if request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form["name"],
                                request.form["email"],
                                hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
    return render_template('register.html', menu=dbase.getMenu(), title= "Регистрация")

if __name__ == "__main__":
    app.run(debug=True)
