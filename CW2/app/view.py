from flask import Blueprint, render_template, request, flash, jsonify, redirect,url_for
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from datetime import datetime
from .database import User, Music
import json
import pymysql
import sqlite3 as sql
import hashlib

view = Blueprint('view', __name__)


@view.route('/profile/<name>', methods=['POST', 'GET'])
def user(name):
    user = User.query.filter_by(id=name).first()

    followers = user.followers.all()
    followed = user.followed.all()

    user_ = current_user.followed.filter_by(followed_id = name).first()
    if user_ is None:
        is_following = False
    else:
        is_following = True

    musics = user.likelist.all()
    if user.id != current_user.id:
        status = 0
    else:
        status = 1
    return render_template('profile.html', is_following = is_following,status = status,followed=followed, user=current_user, view_user = user,musics=musics, followers=followers)


@view.route('/', methods=['POST', 'GET'])
def base():
    # courses = student.courses.all()
    return render_template('base.html', user=current_user)


@view.route('/all', methods=['POST', 'GET'])
def show_all_music():
    con = sql.connect("/Users/lee/PycharmProjects/CW2/app/Database.db")

    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from music")

    rows = cur.fetchall()
    user = current_user

    music = Music.query.all()
    return render_template('all_music.html', u=music, user=current_user)


@view.route('/all/<int:id>', methods=["POST", "GET"])
def add_to_favorite(id):

    music = Music.query.filter_by(id=id).first()
    current_user.likelist.append(music)
    db.session.commit()
    
    return redirect(url_for("view.show_all_music"))
    # return render_template("all_music.html", user=current_user)


@view.route('/follow/<username>')
def follow_sb(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash("The user does not exit!", category="f")
    if current_user.is_following(user):
        flash("You've already followed this user!", category="f")
    current_user.follow(user)
    db.session.commit()
    flash("You are now following %s." % username, category="t")
    # return redirect(url_for('profile'),user=current_user,view_user = user)
    return redirect(url_for("view.user",name = user.id))
    # return render_template("profile.html", user=current_user,view_user = user)

@view.route('/unfollow/<username>')
def unfollow_sb(username):
    user = User.query.filter_by(name=username).first()
    if user is None:
        flash("The user does not exit!", category="f")
    current_user.unfollow(user)
    db.session.commit()
    flash("取消了对该用户的关注")

    return redirect(url_for("view.user",name = user.id))
    # return render_template("profile.html", user=current_user,view_user = user,is_following = is_following)


@view.route('/allusers',methods=["POST", "GET"])
def show_all_users():
    users = User.query.all()
    return render_template("all_users.html",user = current_user,all_users=users)

# @view.route('/portrait',methods=["POST", "GET"])
# def add_portrait():

