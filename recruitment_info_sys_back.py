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
    #print(res2['link'])
    return jsonify({'word_cloud': res1['word_cloud'], 'range': ''+time1+'-'+time2, 'count': res1['count'],
                    'fliterNode': res2['fliterNode'], 'count_all': res2['count_all'], 'link': res2['link']})


@app.route('/mark', methods=['GET', 'POST'])
def mark():
    user = request.get_json()['user']
    toggle = request.get_json()['toggle']
    id = request.get_json()['id']
    markid = id
    host = '127.0.0.1'  # 你的ip地址
    client = MongoClient(host, 27017)  # 建立客户端对象
    db = client.recruit  # 连接recruit数据库
    bookmark = db.bookmark
    if user != '' and toggle is True and id is None:
        word_list = request.get_json()['word_list']
        count = request.get_json()['count']
        count_all = request.get_json()['count_all']
        fliterNode = request.get_json()['fliterNode']
        link = request.get_json()['link']
        job = request.get_json()['job']
        region = request.get_json()['region']
        markdate = request.get_json()['markdate'][2:]
        marktime = request.get_json()['marktime']
        time = request.get_json()['range']
        time1 = time[0]
        time2 = time[1]
        time1 = time1[:time1.rfind('/') + 1] + '1'
        year = int(time2[:4])
        month = int(time2[5:time2.rfind('/')])
        monthRange = calendar.monthrange(year, month)[1]
        time2 = time2[:time2.rfind('/') + 1] + str(monthRange)

        lastrecord = None
        for doc in bookmark.find({'user': user}).sort([('id', -1)]).limit(1):
            lastrecord = doc

        if lastrecord is not None:
            lastid = lastrecord['id']
            if lastid[:6] != markdate:
                markid = markdate + '01'
            else:
                if int(lastid[6:]) + 1 < 10:
                    temp = '0' + str((int(lastid[6:]) + 1))
                else:
                    temp = str(int(lastid[6:]) + 1)
                markid = markdate + temp
        else:
            markid = markdate + '01'
        bookmark.insert_one({'user': user, 'id': markid, 'word_list': word_list, 'count': count,
                             'count_all': count_all, 'fliterNode': fliterNode, 'link': link, 'job': job,
                             'region': region, 'range': time1 + '-' + time2, 'marktime': marktime, 'status': True})
    if user != '' and toggle is False and id is not None:
        bookmark.update_one({'user': user, 'id': id}, {"$set": {'status': False}})
    if user != '' and toggle is True and id is not None:
        bookmark.update_one({'user': user, 'id': id}, {"$set": {'status': True}})
    return jsonify({'id': markid})


@app.route('/get_bookmark', methods=['GET', 'POST'])
def get_bookmark():
    user = request.get_json()['user']
    marks = []
    host = '127.0.0.1'  # 你的ip地址
    client = MongoClient(host, 27017)  # 建立客户端对象
    db = client.recruit  # 连接recruit数据库
    bookmark = db.bookmark
    for doc in bookmark.find({'user': user, 'status': True}):
        marks.append({'markId': doc['id'], 'keyword': doc['region']+doc['job'], 'date_range': doc['range'],
                      'mark_time': doc['marktime']})
    return jsonify({'bookmark': marks})


@app.route('/read_mark', methods=['GET', 'POST'])
def read_mark():
    user = request.get_json()['user']
    id = request.get_json()['id']
    host = '127.0.0.1'  # 你的ip地址
    client = MongoClient(host, 27017)  # 建立客户端对象
    db = client.recruit  # 连接recruit数据库
    bookmark = db.bookmark
    res = bookmark.find_one({'user': user, 'id': id}, {"_id": 0})
    return jsonify({'result': res})


@app.route('/del_mark', methods=['GET', 'POST'])
def del_mark():
    user = request.get_json()['user']
    id = request.get_json()['id']
    host = '127.0.0.1'  # 你的ip地址
    client = MongoClient(host, 27017)  # 建立客户端对象
    db = client.recruit  # 连接recruit数据库
    bookmark = db.bookmark
    bookmark.update_one({'user': user, 'id': id}, {"$set": {'status': False}})
    return jsonify({'result': 'OK'})


if __name__ == '__main__':
    app.run()

