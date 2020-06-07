from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import Tfidf, Cna
import calendar

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


app.url_map.strict_slashes = False


@app.route('/login', methods=['post'])
def login():
    if request.method == 'POST':
        host = '127.0.0.1'
        client = MongoClient(host, 27017)
        db = client.recruit
        user = db.user
        email = request.get_json()['email']
        password = request.get_json()['password']
        doc = user.find_one({'email': email})
        if doc is not None:
            if doc['password'] == password:
                return jsonify({'status': True})  # 登录成功
        else:
            return jsonify({'status': False})
    return jsonify({'status': False})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        host = '127.0.0.1'  # 你的ip地址
        client = MongoClient(host, 27017)  # 建立客户端对象
        db = client.recruit  # 连接recruit数据库
        user = db.user  # 使用user集合，没有则自动创建
        form = request.get_json()['form']
        if user.find_one({'email': form['email']}) is None:
            user.insert_one(form)
            return jsonify({'status': True})  # 注册成功
        else:
            return jsonify({'status': False})  # 插入不成功，已经存在
    else:
        return jsonify({'status': False})


@app.route('/index', methods=['GET'])  # 测试跨域
def index():
    return jsonify('pong!')


@app.route('/search', methods=['GET', 'POST'])
def search():
    job = request.get_json()['job']
    region = request.get_json()['region']
    time = request.get_json()['range']
    time1 = time[0]
    time2 = time[1]
    time1 = time1[:time1.rfind('/') + 1] + '1'
    year = int(time2[:4])
    month = int(time2[5:time2.rfind('/')])
    monthRange = calendar.monthrange(year, month)[1]
    time2 = time2[:time2.rfind('/') + 1] + str(monthRange)
    res1 = Tfidf.result(job, region, time1, time2)
    res2 = Cna.result(region, time1, time2)
    print(res2['link'])
    return jsonify({'word_cloud': res1['word_cloud'], 'range': ''+time1+'-'+time2, 'count': res1['count'],
                    'fliterNode': res2['fliterNode'], 'count_all': res2['count_all'], 'link': res2['link']})


if __name__ == '__main__':
    app.run()

