from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from datetime import datetime
import hashlib
ADMIN = 'sc19hcs@leeds'


class Permission:
    ANONYMOUS = 1
    NORMAL = 5
    ADD = 10


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        print("我们进入到了role的super方法")
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        print("我们进入到了inser_role方法")
        roles = {
            'User': [Permission.NORMAL],
            'Administrator': [Permission.NORMAL, Permission.ADD],
        }
        default_role = 'User'
        # print
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


favorites = db.Table('favorites',
                     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('music_id', db.Integer, db.ForeignKey('music.id'))
                     )


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    aid = db.Column(db.Integer, db.ForeignKey('author.id'))
    # category = db.Column(db.String(30))
    # description = db.Column(db.String(2000))


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    selected = db.Column(db.Integer)

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_name = db.Column(db.String(100), db.ForeignKey('users.name'))
    follower_name = db.Column(db.String(100), db.ForeignKey('users.name'))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    name = db.Column(db.String(64))
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(50))
    # real_avatar = db.Column(db.String(128), default = None)

    likelist = db.relationship('Music', secondary='favorites', backref=db.backref('users', lazy='dynamic'),
                               lazy='dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all,delete-orphan')

    def gravatar(self,size = 100, default = 'identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user,followed_name=user.name,follower_name = self.name)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def can(self, perm):
        print(self.role is not None)
        print(self.role.has_permission(perm))
        return self.role is not None and self.role.has_permission(perm)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                print("管理员")
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                print("普通用户")
                self.role = Role.query.filter_by(default=True).first()
                print(Role.query.filter_by(default=True).first())

    def newest(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

