from functools import wraps
from flask import abort
from flask_login import current_user


def perfil_requerido(*perfis):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.perfil not in perfis and current_user.perfil != "admin":
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return deco
