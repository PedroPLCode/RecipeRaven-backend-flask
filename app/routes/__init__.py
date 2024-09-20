from flask import Blueprint, jsonify, request
from app import app
from flask_cors import CORS
from flask_cors import cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import check_and_delete_unconfirmed_users
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

routes = Blueprint('routes', __name__)
CORS(routes)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

limiter.request_filter(lambda: request.path.startswith('/static'))

@app.errorhandler(429)
@cross_origin()
def ratelimit_handler(e):
    return jsonify({"msg": f"Too many requests, please try again later."}), 429

def start_scheduler():
    logging.info('Starting scheduller.')
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_delete_unconfirmed_users, 
                      trigger="interval",
                      hours=24)
    scheduler.start()

start_scheduler()