from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import jsonify


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if 'roles' not in claims or 'Admin' not in claims['roles']:
            return jsonify(msg="Access denied: Administrator access is required to proceed."), 403
        return fn(*args, **kwargs)
    return wrapper
