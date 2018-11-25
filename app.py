#!/usr/bin/env python
# -*- coding: utf-8 -*-
#! python2
from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
import jwt
import pymongo
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Th1s_a_S3cr3T_K3Y'
CORS(app, resources={r'/*': {'origins': '*'}})

mongo_client = pymongo.MongoClient('mongodb://admin:P455w0rd@dev-shard-00-00-bn3aa.mongodb.net:27017,dev-shard-00-01-bn3aa.mongodb.net:27017,dev-shard-00-02-bn3aa.mongodb.net:27017/test?ssl=true&replicaSet=Dev-shard-0&authSource=admin&retryWrites=true')
database = mongo_client.grama_mia

def get_current_id(db, para, increment_by=1):
    current_number = db.id_manager.find_one({'para': para})['current_number']
    db.id_manager.update_one({'para': para}, {'$inc': {'current_number': increment_by}})
    return current_number

def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        if 'Auth-Token' in request.headers:
            token = request.headers['Auth-Token']

        if not token:
            return jsonify({'message': 'Token is missing!'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = database.users.find_one({'username': data['username']})
        except:
            return jsonify({'message': 'Token is invalid!'})
        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/')
# @token_required
def home(current_user):
    return jsonify({'message': 'Hello World'})

@app.route('/create_user', methods=["POST", "OPTIONS"])
@cross_origin(origin='*')
def create_user():
    data = request.get_json(force=True)
    if 'username' in data and 'password' in data:
        data['password'] = generate_password_hash(data['password'])
        database.users.insert_one(data)
        return jsonify({'message': 'User Created', 'result': 'ok'})
    else:
        pass
    return jsonify({'message': 'Error creating user.', 'result': 'error'})


@app.route('/auth', methods=["POST", "OPTIONS"])
@cross_origin(origin='*')
def auth():
    data = request.get_json(force=True)
    if 'username' not in data or 'password' not in data:
        abort(400)
    user = database.users.find_one({'username': data['username']})
    if bool(user):
        if check_password_hash(user['password'], data['password']):
            token = jwt.encode({
                'username': data['username'],
            }, app.config['SECRET_KEY'])
            return jsonify({
                'token': token,
                'username': data['username'],
                'admin': user['admin']
            })
        else:
            return jsonify({
                'message': 'Password Incorrect.',
                'result': 'error'
            })
    else:
        return jsonify({
            'message': 'Username Incorrect.',
            'result': 'error'
        })
    return jsonify(data)

@app.route('/registro', methods=['POST', 'GET', 'OPTIONS'])
def registro():
    if request.method == 'OPTIONS':
        return 'ok', 200
    elif request.method == 'POST':
        data = request.get_json(force=True)
        data['id'] = get_current_id(database, 'registro')
        database.registro.insert_one(data)
        return jsonify({
            'result': 'ok',
            'message': 'Datos guardados.'
        })

    elif request.method == 'GET':
        registros = database.registro.find({}, {'_id': False})
        data = jsonify({
            'data': [x for x in registros],
            'total': registros.count()
        })
        return data

@app.route('/registro/update', methods=["POST", "OPTIONS"])
def update_registro():
    if request.method == 'OPTIONS':
        return 'ok', 200
    elif request.method == 'POST':
        data = request.get_json(force=True)
        database.registro.update_one({'id': int(data['id'])}, {'$set': data})
        docs = database.registro.find({}, {'_id': False})
        return jsonify({
            'result': 'ok',
            'data': [doc for doc in docs]
        })

@app.route('/registro/delete/<int:id>', methods=['GET', 'OPTIONS', 'DELETE'])
def delete_registro(id):
    result = database.registro.delete_one({'id': id})
    docs = database.registro.find({}, {'_id': False})
    return jsonify({
        'result': 'ok',
        'data': [doc for doc in docs],
        'id': id,
    })




if __name__ == "__main__":
    app.run(debug=True)