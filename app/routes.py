from app import app, db
from app.models import User, Post, Comment, Favorite
from app.utils import *
#from config import Config
from flask import jsonify, request, render_template
from flask_cors import cross_origin
import json
import requests
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from PRIVATE_API_KEY import PRIVATE_API_KEY

#logging dodać
#pytests dodać

app.secret_key = b'my-super-top-secret-key'


@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000)