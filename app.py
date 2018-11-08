from flask import Flask, jsonify, request, render_template
import random
import requests
from bs4 import BeautifulSoup

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import *

from sqlalchemy.sql.expression import func


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///movie'
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db.init_app(app)
migrate = Migrate(app,db)

@app.route('/')
def index():
    movies = Movie.query.all()
#    .order_by(Post.id.desc()).all()
    return render_template('index.html', movies=movies)


@app.route('/keyboard')   # 들어오는 규칙
def keyboard():
    keyboard = {
    "type" : "buttons",
    "buttons" : ["메뉴", "로또", "고양이", "영화", "영화저장"]
    }  # 딕셔너리이므로 JSON 형식으로 바꿔야 함

    return jsonify(keyboard)  # dictionary를 json으로 바꿈


@app.route('/message', methods=["POST"])
def message():
    user_msg = request.json['content']
    msg = "기본응답"  # 기본값으로 출력됨
    img_bool = False
    url = "기본 주소"
    
    if user_msg == "메뉴":  # 메뉴를 하나 골라 msg에 저장
        # 메뉴를 담은 리스트 만들기
        menu = ["20층", "양자강", "편의점"]

        # 그 중 하나를 랜덤하게 고르기
        pick = random.choice(menu)
        
        # msg 변수에 담기
        msg = pick

    elif user_msg == "로또":
        # 1~45가 들어간 숫자들 만들기
#        lotto = list()
#        for i in range(1, 46):
#            lotto.append(i)
        numbers = range(1, 46)
        
        # 그 중 6개 추첨하기
        pick = random.sample(numbers, 6)  # 리스트 형식
        
        # msg에 6개 숫자 넣기
        msg = str(sorted(pick))  # 텍스트 형식으로 바꿔주어야 한다
    
    elif user_msg == "고양이":
        img_bool = True
        cat_api = 'https://api.thecatapi.com/v1/images/search?mime_types=jpg'    # 기본값으로 json 형식으로 가져온다
        req = requests.get(cat_api).json()   # 요청을 보낸 상태
        
        # msg = url 정보를 담아서 출력
        cat_url = req[0]['url']
        url = cat_url  # 지역변수
        msg = "나만 고양이 사진 없어!!!" 
    
    elif user_msg == "영화":
        img_bool = True
        
        movie = Movie.query.order_by(func.random()).first()  # 랜덤하게 인덱스가 정렬됨
        msg = movie.title + ' / 평점: ' + str(movie.star) + '/ 예매율: ' + str(movie.vote)
        url = movie.img
        
    elif user_msg == "영화저장":
        
        db.session.query(Movie).delete()
        
        naver_movie = 'https://movie.naver.com/movie/running/current.nhn'
        req = requests.get(naver_movie).text
        soup = BeautifulSoup(req, 'html.parser')
        
        title_list = soup.select('dt.tit > a') 
        star_list = soup.select('a > span.num')
        vote_list = soup.select('div.star_t1 > span.num')
        img_url_list = soup.select('div.thumb > a > img')
        
        movies = {}
        for i in range(0, 10):
            movies[i] = {
                'title': title_list[i].text,
                'star': star_list[i].text,
                'vote': vote_list[i].text,
                'url': img_url_list[i]['src']
            }
        for i in range(0, 10):
            movie = Movie(title_list[i].text,
                        star_list[i].text,
                        vote_list[i].text,
                        img_url_list[i]['src']
                    )
            db.session.add(movie)
            db.session.commit()
        msg = "저장완료"
        
        
#    print(user_msg)  # 서버의 console 창에 사용자가 입력한 메시지가 출력됨
#    return user_msg

    # 이미지 없는 버전
    return_dict = {
        'message': {
            'text': msg
        },
        'keyboard': {
            "type" : "buttons",
            "buttons" : ["로또", "메뉴", "고양이", "영화", "영화저장"]
        }  # 처음의 메뉴와 입력 후의 메뉴가 다르다
    }
    
    # 이미지 있는 버전
    return_img_dict = {
        'message': {
            'text': msg,
            'photo' : {
                "url" : url,
                "width" : 720,
                "height" : 630
            }
        },
        'keyboard': {
            "type" : "buttons",
            "buttons" : ["로또", "메뉴", "고양이", "영화", "영화저장"]
        }  # 처음의 메뉴와 입력 후의 메뉴가 다르다
    }
    
    if img_bool:
        return jsonify(return_img_dict)
    else:
        return jsonify(return_dict)
