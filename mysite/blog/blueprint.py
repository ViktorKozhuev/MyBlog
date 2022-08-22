from flask import Blueprint, g, render_template, abort, url_for, request, flash, redirect, session
import sqlite3
from flask_login import login_required, current_user
from Fdatabase import FDataBase
import datetime
from flask_paginate import Pagination, get_page_args, get_page_parameter
from forms import CommentForm

menu = [
        {'name': 'Блог', 'url': '/blog'},
        {'name': 'Обратная связь', 'url': '/contact'}, ]

blog = Blueprint('posts', __name__, template_folder='templates')


@blog.context_processor
def utility_processor():
    def time_to_date(time_):
        return datetime.datetime.utcfromtimestamp(time_).strftime('%Y-%m-%d')
    return dict(time_to_date=time_to_date)


db = None


@blog.before_request
def before_request():
    global db
    db = g.get('link_db')


@blog.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


@blog.route('/')
def index():
    list = []
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 3
    # print(page)
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url, time FROM posts ORDER BY time DESC LIMIT {(page-1)*per_page}, {per_page}")
            list = cur.fetchall()
            cur.execute("SELECT count(id) as count FROM posts")
            total = cur.fetchall()
        except sqlite3.Error as e:
            print('Ошибка получения статей из БД' + str(e))

    pagination = Pagination(page=page, total=total[0]['count'],  record_name='users', per_page=per_page)
    return render_template('blog/index_1.html', menu=menu, posts=list, pagination=pagination)


@blog.route("/post/<alias>", methods=['POST', 'GET'])
def showPost(alias):
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    comments = dbase.showComments(alias)
    if not title:
        abort(404)
    form = CommentForm()
    try:
        user_id = current_user.get_id()
        post_url = alias
        # print(user_id)
        if current_user.is_authenticated:
            if form.validate_on_submit():
                dbase.addComment(user_id, post_url, form.text.data)
                flash('Комментарий добавлен', category='success')
                return redirect(request.args.get('next') or url_for('posts.showPost', alias=alias))
    except:
        flash('Комментарий не добавлен', category='error')
    return render_template('blog/post.html', menu=menu, title=title, post=post, form=form, comments=comments)

