import json
from math import radians, sin, cos, sqrt, atan2
from flask import Flask, request, jsonify, render_template
import pandas as pd
import time

app = Flask(__name__)

# 读取城市数据
city_data = pd.read_csv('us-cities.csv')

review_data = pd.read_csv('newre.csv')

# 从数据库获取评论文本数据
# 每页城市数
cities_per_page = 50


@app.route('/')
def index():
    return render_template('index.html')

def haversine(lat1, lon1, lat2, lon2):
    # 将经纬度从度数转换为弧度
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine公式计算距离
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius_of_earth = 6371  # 地球半径（单位：公里）

    # 计算距离（单位：千米）
    distance = radius_of_earth * c

    return distance

def calculate_distances(target_city, target_state):
    # 查询城市距离并计算响应时间
    start_time = time.time()

    # 初始化结果列表
    city_distances = []

    # 获取目标城市的经纬度
    target_city_data = city_data[(city_data['city'] == target_city) & (city_data['state'] == target_state)]
    if not target_city_data.empty:
        target_lat = float(target_city_data['lat'])
        target_lng = float(target_city_data['lng'])

        # 计算目标城市与其他城市的距离并添加到列表中
        for _, city in city_data.iterrows():
            lat = float(city['lat'])
            lng = float(city['lng'])
            distance = haversine(target_lat, target_lng, lat, lng)
            city_distances.append(distance)

        # 按距离升序排序
        city_distances = sorted(city_distances)

    response_time = int((time.time() - start_time) * 1000)  # 计算响应时间（毫秒）
    return city_distances, response_time


def calculate_average_scores(target_city, target_state):
    # 计算平均评分和响应时间
    start_time = time.time()

    # 初始化结果列表
    city_scores = []

    # 获取目标城市的经纬度
    target_city_data = city_data[(city_data['city'] == target_city) & (city_data['state'] == target_state)]
    if not target_city_data.empty:
        target_lat = float(target_city_data['lat'])
        target_lng = float(target_city_data['lng'])

        # 计算目标城市与其他城市的距离和平均评分
        for _, city in city_data.iterrows():
            lat = float(city['lat'])
            lng = float(city['lng'])
            distance = haversine(target_lat, target_lng, lat, lng)

            # 过滤当前城市的评分数据
            city_reviews = review_data[review_data['city'] == city['city']]

            # 计算当前城市的平均评分
            average_score = city_reviews['score'].mean() if not city_reviews.empty else 0

            city_scores.append({'city': city['city'], 'distance': distance, 'average_score': average_score})

    # 按距离升序排序城市
    city_scores.sort(key=lambda x: x['distance'])

    response_time = int((time.time() - start_time) * 1000)  # 响应时间（毫秒）
    return city_scores[:cities_per_page], response_time

@app.route('/index_city', methods=['GET', 'POST'])
def index_city():
    if request.method == 'POST':
        city_name = request.form['city']
        state_name = request.form['state']

        # 计算城市距离
        distances, response_time = calculate_distances(city_name, state_name)

        # 将数据转换为JSON格式
        data = json.dumps({'distances': distances, 'response_time': response_time})
        return render_template('index_city.html', data=data)

    return render_template('index_city.html', data=None)


@app.route('/index_review', methods=['GET', 'POST'])
def index_review():
    if request.method == 'POST':
        city_name = request.form['city']
        state_name = request.form['state']

        # 计算平均评分
        scores, response_time = calculate_average_scores(city_name, state_name)

        # 将数据转换为JSON格式
        data = json.dumps({'scores': scores, 'response_time': response_time})
        return render_template('index_review.html', data=data)

    return render_template('index_review.html', data=None)



if __name__ == '__main__':
    app.run(debug=True)