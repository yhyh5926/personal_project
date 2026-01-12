import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'collector'))

from flask import Flask, render_template
from routes import weather,traffic

app = Flask(__name__)
weather.routes(app)
traffic.routes(app)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/traffic')
def traffic():
    return render_template('traffic.html')

if __name__ == '__main__':
    app.run(debug=True)
