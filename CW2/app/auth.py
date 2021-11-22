from flask import Blueprint
from flask import Blueprint, render_template, request, flash, Flask, redirect, url_for, current_app
from .database import *
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        name = user.name
        if user:
            if check_password_hash(user.password, password):
                flash("Login successfully!", category="t")
                login_user(user, remember=True)
                return redirect(url_for("view.user",name = user.id))
            else:
                flash("Wrong password", category="f")
        else:
            flash("User does not exist!", category="f")

    return render_template("login.html", user=current_user)


ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'png', 'jpg', 'jpeg'}
def file_allowed(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        default_potrait = "200326124155_1_900x600的副本.jpg"
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email does exist", category="f")
        elif password1 != password2:
            flash("The password do not match with each other", category="f")
        elif len(password1) < 6:
            flash("Password must be at least 6 characters", category="f")
        else:
            new = User(portrait = default_potrait,email=email, name=name,
                       password=generate_password_hash(password2))
            # role = Role(id = current_user.id)

            db.session.add(new)
            db.session.commit()
            # login_user(user, remember=True)
            flash("Create account successfully", category="t")
            return redirect("/")
    return render_template('register.html', user=current_user)


from .decorators import admin_required, permissions_required


@auth.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def for_admins_only():
    return render_template('test.html', user=current_user)


@auth.route('/moderate')
@login_required
@permissions_required(Permission.NORMAL)
def for_moderators_only():
    return render_template('test.html', user=current_user)


@auth.route('/add', methods=["GET", "POST"])
def add_music():
    if request.method == 'POST':
        name = request.form.get('name')
        author_name = request.form.get('author')
        author = Author.query.filter_by(name=author_name).first()
        print("我在这呢！")

        if author is None:

            print("没有这个作家啊")
            author_added = Author(name=author_name)
            db.session.add(author_added)
            db.session.commit()
            music = Music(name=name, aid=author_added.id, author=author_name)

        else:
            aid = author.id
            music = Music(name=name, aid=aid, author=author.name)
        db.session.add(music)
        db.session.commit()
    return render_template("add_music.html", user=current_user)

@auth.route('/add_author',methods=["GET", "POST"])
def add_author():
    # if db.session.query(User).filter_by(login='passport').count() < 1:
    if request.method == 'POST':
        name = request.form.get('name')
        if Author.query.filter_by(name = name).count() < 1:
            author = Author(name = name)
            db.session.add(author)
            db.session.commit()
        else:
            flash("The author is already added!",category="f")
    return render_template("add_authors.html",user=current_user)


@auth.route('/all_authors')
def show_all_authors():
    all_authors =  Author.query.all()
    return render_template("all_authors.html",authors = all_authors,user=current_user)
'''
用来更新用户登录信息
@auth.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.newest()
        if not current_user.cofirmed & request.endpoint & reque
'''
