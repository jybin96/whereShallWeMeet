from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.dbsparta

CORS(app)  # 통신 부분에서 cors 에러가 생겨 flask_cors 라이브러리를 설치한뒤에 cors오류 해결


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return redirect('http://localhost:5000/login')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# @app.route('/login')
# def login():
#     msg = request.args.get("msg")
#     return render_template('/page/sytw/login_page.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인<-login
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()  # 해싱
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:  # 로그인 성공
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify(
            {'result': 'success', 'token': token, 'username': result["username"], 'nickname': result["nick_name"]})
    # 찾지 못하면 로그인 실패
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원가입
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()  # 비밀번호 해싱
    nickname_receive = request.form['nickname_give']
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nick_name": nickname_receive,  # 닉네임

    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# id 중복검사
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 닉네임 중복검사
@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000, debug=True)
