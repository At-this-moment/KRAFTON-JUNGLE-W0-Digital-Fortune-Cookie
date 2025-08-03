from flask import Flask, jsonify, request, render_template, send_from_directory, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import random
import os
from datetime import datetime, timezone, timedelta
import jwt

# 날짜 형식 지정 (요일 포함)
weekday_dict = ["월", "화", "수", "목", "금", "토", "일"]

# 마지막 뽑은 날짜에 요일 추가
def format_date_with_weekday(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = weekday_dict[date_obj.weekday()]  # 요일 가져오기 (0=월요일)
    return f"{date_str} ({weekday})"

from datetime import datetime, timezone, timedelta

from fortune_cookie import generate_fortune

app = Flask(__name__) # (수정)

CORS(app)

# 🔹 JWT 설정 (서버 재부팅 후 기존 토큰을 무효화하기 위해 issued_at 사용)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 1시간 후 만료

jwt_manager = JWTManager(app) # (수정)

# 🔹 MongoDB 설정
mongo_host = os.getenv('MONGO_HOST')
mongo_port = int(os.getenv('MONGO_PORT'))
mongo_username = os.getenv('MONGO_USERNAME')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_db_name = os.getenv('MONGO_DB_NAME')

client = MongoClient(f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}", mongo_port)
db = client[mongo_db_name] # 환경 변수에서 가져온 DB 이름 사용

# 🔹 서버 재부팅 시 기존 로그인 무효화 (서버 시작 시간 저장)
server_start_time = datetime.now(timezone.utc)
print(f"[DEBUG] 서버 시작 시간: {server_start_time}")

### 회원가입 관련 API ###
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html', service_name = service_name)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    name = data.get('name')
    birthdate = data.get('birthdate')  # 생년월일 추가
    gender = data.get('gender')  # 성별 추가
    password = data.get('password')
    password_confirm = data.get('password_confirm')

    if not all([username, name, birthdate, gender, password, password_confirm]):
        return jsonify({"msg": "모든 필드를 입력해주세요."}), 400

    if password != password_confirm:
        return jsonify({"msg": "비밀번호가 일치하지 않습니다!"}), 400

    # 🔹 이름, 생년월일, 성별이 동일한 사용자가 있는지 확인 (중복 가입 방지)
    existing_user = db.users.find_one({"name": name, "birthdate": birthdate, "gender": gender})
    if existing_user:
        return jsonify({"msg": "이미 가입된 사용자입니다."}), 409

    # 🔹 아이디 중복 확인
    if db.users.find_one({"username": username}):
        return jsonify({"msg": "이미 존재하는 아이디입니다."}), 409

    hashed_password = generate_password_hash(password)

    user = {
        'username': username,
        'name': name,
        'birthdate': birthdate,
        'gender': gender,
        'password': hashed_password,
        'score': None,
    }

    try:
        db.users.insert_one(user)
    except Exception as e:
        return jsonify({"msg": "회원가입 중 오류가 발생했습니다."}), 500

    return jsonify({"msg": "회원가입이 완료되었습니다. 로그인해주세요!"}), 201


@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.json
    username = data.get('username')
    
    existing_user = db.users.find_one({"username": username})
    if existing_user:
        return jsonify({"msg": "이미 존재하는 아이디입니다."}), 409  
    return jsonify({"msg": "사용 가능한 아이디입니다."}), 200  


### 로그인 API ###
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "아이디와 비밀번호를 입력해주세요."}), 400

    user = db.users.find_one({"username": username})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({"msg": "아이디나 비밀번호가 잘못되었습니다."}), 401

    # 🔹 JWT 발급 시 "issued_at"을 timezone-aware로 변경
    issued_at = datetime.now(timezone.utc).timestamp()
    access_token = create_access_token(identity=username, expires_delta=timedelta(hours=1), additional_claims={"issued_at": issued_at})

    print(f"[DEBUG] JWT 발급 시간: {issued_at}")

    return jsonify({"msg": "로그인에 성공했습니다!", "access_token": access_token}), 200


### JWT 검증 시 서버가 재부팅되었는지 확인 ###
@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    claims = get_jwt_identity()
    token = request.headers.get("Authorization").split(" ")[1]
    jwt_data = decode_token(token)

    issued_at = datetime.fromtimestamp(jwt_data["iat"], timezone.utc)

    print(f"[DEBUG] 서버 시작 시간: {server_start_time}, 토큰 발급 시간: {issued_at}")

    # 🔹 서버가 재부팅된 경우 (issued_at이 서버 시작 시간보다 5초 이상 과거일 경우)
    if issued_at + timedelta(seconds=5) < server_start_time:
        print("[DEBUG] 서버가 재시작되었으므로 토큰을 무효화합니다.")
        return jsonify({"msg": "서버가 재시작되었습니다. 다시 로그인해주세요."}), 401

    return jsonify({"username": claims}), 200


### 포춘쿠키 페이지 API ###
@app.route('/fortune_page', methods=['GET'])
def fortune_page():
    return render_template('fortune.html', service_name = service_name)

@app.route('/fortune', methods=['GET'])
@jwt_required()
def fortune():
    current_user = get_jwt_identity()

    if not current_user:
        print("[DEBUG] JWT 토큰 오류 - 사용자가 인증되지 않음")
        return jsonify({"msg": "인증된 사용자가 아닙니다. 다시 로그인하세요."}), 401

    print(f"[DEBUG] 포춘쿠키 요청 - 사용자: {current_user}")

    # 🔹 현재 날짜 가져오기
    # today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    # (수정) UTC -> KST
    today_date = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d')

    # 🔹 사용자 정보 가져오기
    user = db.users.find_one({"username": current_user})

    if not user:
        print("[DEBUG] DB 오류 - 사용자를 찾을 수 없음")
        return jsonify({"msg": "사용자 정보를 찾을 수 없습니다."}), 404

    # 🔹 오늘 이미 포춘쿠키를 열었는지 확인
    if user.get("last_fortune_date") == today_date:
       return jsonify({"msg": "오늘의 포춘쿠키는 이미 열었습니다. 내일 다시 시도하세요!"}), 403

    # 🔹 포춘쿠키 생성
    message, score = generate_fortune()
    rounded_score = round(score, 1)

    past_scores = user.get("past_scores", [])
    past_scores.append(score)
    if len(past_scores) > 7:
        past_scores.pop(0)

    average_score = round(sum(past_scores) / len(past_scores), 1)
    last_score = round(score, 1)  # 🔹 소수점 한 자리까지만 반올림


    # 🔹 DB 업데이트: 점수 & 오늘 날짜 저장
    db.users.update_one(
        {"username": current_user},
        {"$set": {
            "score": score,
            "fortune_message": message,
            "past_scores": past_scores,
            "average_score": average_score,
            "last_fortune_date": today_date  # 🔹 오늘 날짜 저장
        }}
    )

    # 🔹 서버 콘솔에 로그 출력
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[포춘쿠키 기록] 사용자: {current_user}, 메시지: {message}, 점수: {score}, 획득 시간: {timestamp}")

    return jsonify({"message": message}), 200


# 마이페이지 HTML 파일을 렌더링하는 엔드포인트 (페이지 이동)
@app.route('/mypage', methods=['GET'])
def mypage_page():
    return render_template('mypage.html')

@app.route('/mypage/data', methods=['GET'])
@jwt_required()
def mypage_data():
    current_user = get_jwt_identity()

    # 🔹 사용자 정보 가져오기
    user = db.users.find_one({"username": current_user}, {"_id": 0, "password": 0})

    if not user:
        return jsonify({"msg": "사용자 정보를 찾을 수 없습니다."}), 404

    # 🔹 최근 7일간 점수
    past_scores = user.get("past_scores", [])
    last_7_scores = past_scores[-7:] if past_scores else [0] * 7  

    # 🔹 평균 점수 계산 (소수점 1자리까지 반올림)
    avg_score = round(sum(last_7_scores) / len(last_7_scores), 1) if last_7_scores else 0

    # 🔹 포춘쿠키 마지막 메시지 및 점수, 획득 날짜
    last_message = user.get("fortune_message", "기록 없음")
    last_score = round(user.get("score", 0), 1)
    last_date = user.get("last_fortune_date", "기록 없음")

    # 🔹 성별 변환 (남자, 여자, 기타)
    gender_map = {"male": "남자", "female": "여자"}
    gender = gender_map.get(user.get("gender", "").lower(), "기타")

    # 🔹 전체 사용자 점수 랭킹 계산
    all_users = list(db.users.find({}, {"username": 1, "average_score": 1, "_id": 0}).sort("average_score", -1))
    
    # 🔹 내 순위 계산
    total_users = len(all_users)
    my_rank = next((i + 1 for i, u in enumerate(all_users) if u["username"] == current_user), total_users)
    rank_percentage = round((my_rank / total_users) * 100, 1)  # 상위 % 계산

    # 🔹 TOP 3 랭킹 제공
    top_users = all_users[:3]

    return jsonify({
        "username": user["username"],
        "name": user["name"],
        "birthdate": user["birthdate"],
        "gender": gender,  # 🔹 성별 변환
        "average_score": avg_score,
        "past_scores": last_7_scores,
        "last_message": last_message,
        "last_score": last_score,
        "last_date": last_date,
        "rankings": top_users,  # 상위 3명 랭킹 제공
        "my_rank": my_rank,  # 내 랭킹
        "total_users": total_users,  # 전체 유저 수
        "rank_percentage": rank_percentage  # 내 순위 상위 % 
    }), 200


service_name = "Digital Fortune Cookie"

### 기본 라우트 ###
@app.route('/')
def home():
    token_receive = request.cookies.get('access_token')
    response = make_response(render_template('index.html', is_logged_in=False, service_name = service_name))

    if token_receive is None:
        return response
    
    try:
        decoded_token = jwt.decode(token_receive, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        user = db.users.find_one({"username": decoded_token['sub']})

		# 🔹 최근 7일간 점수
        past_scores = user.get("past_scores", [])
        last_7_scores = past_scores[-7:] if past_scores else [0] * 7  

        # 🔹 평균 점수 계산 (소수점 1자리까지 반올림)
        avg_score = round(sum(last_7_scores) / len(last_7_scores), 1) if last_7_scores else 0

        # 🔹 포춘쿠키 마지막 메시지 및 점수, 획득 날짜
        last_message = user.get("fortune_message", "기록 없음")
        try:
            last_score = round(user.get("score", 0), 1)
        except:
            last_score = 0
        last_date = user.get("last_fortune_date", "기록 없음")

        # 🔹 전체 사용자 점수 랭킹 계산
        all_users = list(db.users.find({}, {"username": 1, "average_score": 1, "name": 1, "_id": 0}).sort("average_score", -1))
    
        # 🔹 내 순위 계산
        total_users = len(all_users)
        my_rank = next((i + 1 for i, u in enumerate(all_users) if u["username"] == decoded_token['sub']), total_users)
        rank_percentage = round((my_rank / total_users) * 100, 1)  # 상위 % 계산

        # 🔹 TOP 3 랭킹 제공
        try:
            top_1st = all_users[0]['name']
        except:
            top_1st = "*"
        try:
            top_1st_score = all_users[0]['average_score']
        except:
            top_1st_score = 0
        try:
            top_2nd = all_users[1]['name']
        except:
            top_2nd = "*"
        try:
            top_2nd_score = all_users[1]['average_score']
        except:
            top_2nd_score = 0
        try:
            top_3rd = all_users[2]['name']
        except:
            top_3rd = "*"
        try:
            top_3rd_score = all_users[2]['average_score']
        except:
            top_3rd_score = 0

        # 🔹 현재 날짜 가져오기
        today_date = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d')
        if last_date == today_date:
            is_done_today = True
        else:
            is_done_today = False

        # jinja2를 사용한 서버 사이드 렌더링 (SSR)
        return render_template('index.html', service_name = service_name,
                                is_logged_in = True, is_done_today = is_done_today, my_name = user.get('name'), my_message = last_message,
                                rank_1st = top_1st, rank_2nd = top_2nd, rank_3rd = top_3rd,
                                point_1st = top_1st_score, point_2nd = top_2nd_score, point_3rd = top_3rd_score, my_rank = rank_percentage,
                                past_scores = last_7_scores, avg_score = avg_score, last_score = last_score
                            )
    except Exception as e:
        print(f"예외 발생: {e}")
        response.set_cookie('access_token', '', expires=0)
        return response

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


### 서버 실행 ###
if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)