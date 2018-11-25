import jwt
from app import app, database
from flask import request, jsonify

db = database

def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        if 'Auth-Token' in request.headers:
            token = request.headers['Auth-Token']

        if not token:
            return jsonify({'message': 'Token is missing!'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = db.users.find_one({'username': data['username']})
        except:
            return jsonify({'message': 'Token is invalid!'})
        return f(current_user, *args, **kwargs)

    return decorated