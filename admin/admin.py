import sqlite3
from flask import Blueprint, Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
from Fdatabase import FDataBase
import datetime
import os
from secretdata import admin_name, admin_password
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


db = None


@admin.context_processor
def utility_processor():
    def time_to_date(time_):
        return datetime.datetime.utcfromtimestamp(time_).strftime('%Y-%m-%d')
    return dict(time_to_date=time_to_date)


@admin.before_request
def before_request():
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)

#{'url': './', 'title': 'Админ-панель'},

menu = [{'url': './list_messages', 'title': 'Сообщения'},
        {'url': './listpubs', 'title': 'Список статей'},
        {'url': './listusers', 'title': 'Список пользователей'},
        {'url': './add_post', 'title': 'Добавить пост'},
        {'url': 'logout', 'title': 'выйти'}]



@admin.route('/')
def index():
    if not is_logged():
        return redirect(url_for('.login'))
    return redirect(url_for('.listpubs'))


@admin.route('/login', methods=['POST', "GET"])
def login():
    if is_logged():
        return redirect(url_for('.index'))
    if request.method == 'POST':
        if request.form['user'] == admin_name and request.form['psw'] == admin_password:
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('Неверная пара логин/проль')

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=['POST', "GET"])
def logout():
    if not is_logged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login'))


@admin.route('/listpubs', methods=['POST', "GET"])
def listpubs():
    if not is_logged():
        return redirect(url_for('.login'))
    list = []
    resume = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list = cur.fetchall()
            cur.execute(f"SELECT text FROM resume LIMIT 1")
            resume = cur.fetchone()
        except sqlite3.Error as e:
            print('Ошибка получения статей из БД' + str(e))

        return render_template('admin/listpubs.html', title='Список статей', menu=menu, list=list, resume=resume)


@admin.route('/listusers')
def listusers():
    if not is_logged():
        return redirect(url_for('.login'))
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT id, name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print('Ошибка получения пользователей из БД' + str(e))

        return render_template('admin/listusers.html', title='Список пользователей', menu=menu, list=list)


@admin.route('/add_post', methods=['POST', "GET"])
def add_post():
    if not is_logged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            dbase = FDataBase(db)
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='succes')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('admin/add_post.html', title='Добавление поста', menu=menu)


@admin.route('/delete_post/<alias>', methods=['POST', 'GET'])
def delete_post(alias):
    if not is_logged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        print('POST')
        dbase = FDataBase(db)
        dbase.deletePost(alias)
    return redirect(url_for('.listpubs'))


@admin.route('/update_post/<alias>', methods=['POST', 'GET'])
def update_post(alias):
    if not is_logged():
        return redirect(url_for('.login'))
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    comments = dbase.showComments(alias)
    if not title:
        return redirect(url_for('.listpubs'))
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:

            alias = alias
            res = dbase.updatePost(alias, request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка редактирования статьи', category='error')
            else:
                flash('Статья редактирована успешно', category='success')
            return redirect(request.args.get('next') or url_for('admin.update_post', alias=alias))
        else:
            flash('Ошибка редактирования статьи', category='error')

    return render_template('admin/update_post.html', title='Редактирование поста', menu=menu, alias=alias, title_prev=title, text_prev=post, comments=comments )


@admin.route('/delete_user/<alias>', methods=['POST', 'GET'])
def delete_user(alias):
    if not is_logged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        dbase = FDataBase(db)
        dbase.deleteUser(alias)
    return redirect(url_for('.listusers'))


@admin.route('/activate_user/<alias>', methods=['POST', 'GET'])
def activate_user(alias):
    if not is_logged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        dbase = FDataBase(db)
        dbase.setUserActive(alias)
    return redirect(url_for('.listusers'))


@admin.route('/delete_comment/<alias>', methods=['POST', 'GET'])
def delete_comment(alias):
    if not is_logged():
        return redirect(url_for('.login'))
    if request.method == 'POST':
        dbase = FDataBase(db)
        dbase.deletecomment(alias)
    return redirect(request.args.get('next') or url_for('admin.update_post', alias=alias))


@admin.route('/update_resume', methods=['POST', 'GET'])
def update_resume():
    if not is_logged():
        return redirect(url_for('.login'))
    dbase = FDataBase(db)
    text, time = dbase.getresume()
    if request.method == 'POST':
        dbase = FDataBase(db)
        res = dbase.updateresume(request.form['text'])
        if not res:
            flash('Ошибка редактирования резюме', category='error')
        else:
            flash('Резюме редактировано успешно', category='success')
    return render_template('admin/update_resume.html', title='Редактирование резюме', menu=menu,  text_prev=text)


@admin.route('/list_messages')
def list_messages():
    if not is_logged():
        return redirect(url_for('.login'))
    list = []
    try:
        dbase = FDataBase(db)
        list = dbase.show_messages()
    except:
        print('ошибка получения сообщений')

    return render_template('admin/list_messages.html', title='Список сообщений', menu=menu, list=list)


@admin.route('/upload/<alias>', methods=['POST', "GET"])
def upload(alias):
    if request.method == 'POST':
        print('upload')
        if 'file' not in request.files:
            flash('Не могу прочитать файл', category='error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла', category='error')
            return redirect(request.url)
        if file:
            filename = file.filename
            base = 'static/images_html' #url_for('static', filename='images_html')

            folder = os.path.join(base, alias)
            folder = folder.replace('\\', '/')
            if not os.path.isdir(folder):
                os.mkdir(folder)
            file.save(os.path.join(folder, filename))
            return redirect(url_for('admin.update_post', alias=alias))
    return redirect(url_for('admin.update_post', alias=alias))