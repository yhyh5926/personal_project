import os
import sys

# ===== 경로 세팅 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, 'collector'))

from flask import Flask, render_template
from routes import weather, traffic, subway
from analyzer.weather_plotter import generate_weather_bar_plot, load_weather_df

app = Flask(__name__)

# ===== API 라우트 =====
weather.routes(app)
traffic.routes(app)
subway.routes(app)


# ===== 페이지 =====
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/weather')
def weather_page():
    df = load_weather_df()
    image_path = generate_weather_bar_plot(df)
    return render_template('weather.html', image_path=image_path)


@app.route('/traffic')
def traffic_page():
    return render_template('traffic.html')


@app.route('/subway')
def subway_page():
    return render_template('subway.html')


if __name__ == '__main__':
    app.run(debug=True)
