from flask import Blueprint
from flask_cors import CORS

routes = Blueprint('routes', __name__)
CORS(routes)