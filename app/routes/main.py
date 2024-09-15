from app import app
from app.routes import limiter
from flask import render_template

@app.route('/', methods=['GET'])
@limiter.exempt
def show_info():
    return render_template("index.html")