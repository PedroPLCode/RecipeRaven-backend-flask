from app import app
from flask import render_template

@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")