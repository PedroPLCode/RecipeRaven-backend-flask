from app import app
from flask import render_template

app.secret_key = b'my-super-top-secret-key'

@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)