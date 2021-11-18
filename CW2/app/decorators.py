
from functools import wraps
from flask import abort
from flask_login import current_user
from .database import Permission


def permissions_required(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permissions):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permissions_required(Permission.ADD)(f)
