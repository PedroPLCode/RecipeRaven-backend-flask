from flask import Blueprint
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import check_and_delete_unconfirmed_users

routes = Blueprint('routes', __name__)
CORS(routes)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_delete_unconfirmed_users, trigger="interval", hours=24)
    scheduler.start()

start_scheduler()