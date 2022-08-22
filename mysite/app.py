from flask import Flask, render_template, g, url_for, redirect, request, flash, make_response
from blog.blueprint import blog
from admin.admin import admin
import sqlite3
import os
from Fdatabase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, MessageForm
from secretdata import secretkey

DATABASE = '/myblog.db'
DEBUG = False
SECRET_KEY = secretkey

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'myblog.db')))
app.register_blueprint(blog, url_prefix='/blog')
app.register_blueprint(admin, url_prefix='/admin')


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = 'success'

@login_manager.user_loader
def load_user(user_id):
    # print('load_user')
    return UserLogin().fromDB(user_id, dbase)



menu = [
        {'name': 'Блог', 'url': '/blog'},
        {'name': 'Обратная связь', 'url': '/contact'}, ]




def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.errorhandler(404)
def pagenotfound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


@app.route('/')
def index():
    text, time = dbase.getresume()
    return render_template('index.html', title='MyBlog', menu=menu, text=text )


@app.route("/contact", methods=['POST', "GET"])
@login_required
def contact():
    form = MessageForm()
    if form.validate_on_submit():
        try:
            user_id = current_user.get_id()
            if current_user.is_authenticated:
                if form.validate_on_submit():
                    dbase.add_message(user_id,  form.text.data)
                    flash('Сообщение отправлено ', category='success')

        except:
            flash('Сообщение не отправлено ', category='error')

    return render_template('contact.html', title="Обратная связь", menu=menu, form=form)


@app.errorhandler(404)
def pagenotfound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


@app.route('/login', methods=['POST', "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Неверная пара логин/пароль', 'error')
    return render_template('login.html', menu=menu, title='Авторизация', form=form)


@app.route('/register', methods=['POST', "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_ = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data,  hash_)
        if res:
            flash('Вы успешно зарегистрированы', 'success')
            return redirect(url_for('login'))
        else:
            flash('Ошибка добавления в БД', 'error')
    return render_template('register.html', menu=menu, title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=menu, title='Профиль')


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ''
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=['POST', "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash('Ошибка добавления аватара', 'error')
                    return redirect(url_for('profile'))
                flash('Аватар обновлен', 'success')
            except FileNotFoundError as e:
                flash('ошибка чтения файла', 'error')
        else:
            flash('ошибка обновления аватара', 'error')
    return redirect(url_for('profile'))


@app.route('/useridava/<id>')
def useridava(id):
    img = dbase.getusersavatar(id)
    if not img:
        try:
            with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), 'rb') as f:
                img = f.read()
        except FileNotFoundError as e:
            print('Не найден аватар по умолчанию: ' + str(e))
    if not img:
        return ''
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h




if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
