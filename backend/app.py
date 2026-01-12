import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'collector'))

from flask import Flask, render_template
from routes import weather

app = Flask(__name__)

app.register_blueprint(weather.bp, url_prefix='/weather')


@app.route('/')
def index():
    return render_template('weather.html')


if __name__ == '__main__':
    app.run(debug=True)
