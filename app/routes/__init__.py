from flask import Blueprint, jsonify
from app import app
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import check_and_delete_unconfirmed_users
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

routes = Blueprint('routes', __name__)
CORS(routes)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests, please try again later."), 429

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_delete_unconfirmed_users, 
                      trigger="interval",
                      hours=24)
    scheduler.start()

start_scheduler()