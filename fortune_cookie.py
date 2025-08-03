import random

# 행운 등급별 확률 가중치, grade, 각각의 상황 단어 딕셔너리를 포함한 리스트
fortune_data = {
    "worst": {
        "probability": 0.05,
        "grade": 1,
        "event": [
            {"word": "최악의 상황이", "score": 1},
            {"word": "중대한 실수가", "score": 2},
            {"word": "예상치 못한 사고가", "score": 2}
        ],
        "consequence": [
            {"word": "큰 손실이 발생할 가능성이 높습니다", "score": 2},
            {"word": "심각한 문제가 생길 수 있습니다", "score": 1},
            {"word": "매우 위험한 상황이 될 수 있습니다", "score": 2}
        ],
        "advice": [
            {"word": "모든 결정을 다시 검토하세요", "score": 2},   
            {"word": "무리한 행동을 피하세요", "score": 2},
            {"word": "신중하게 대처하세요", "score": 1}
        ]
    },
    "bad": {
        "probability": 0.15,
        "grade": 3,
        "event": [
            {"word": "작은 사고가", "score": 3},
            {"word": "계획 변경이", "score": 4},
            {"word": "불편한 대화가", "score": 4}
        ],
        "consequence": [
            {"word": "예상보다 일이 지연될 수 있습니다", "score": 4},
            {"word": "어려운 상황이 이어질 것입니다", "score": 3},
            {"word": "조금 더 인내심이 필요합니다", "score": 4}
        ],
        "advice": [
            {"word": "차분한 태도를 유지하세요", "score": 3},
            {"word": "한 걸음 물러서서 보세요", "score": 4},
            {"word": "충동적인 결정을 피하세요", "score": 4}
        ]
    },
    "neutral": {
        "probability": 0.60,
        "grade": 5,
        "event": [
            {"word": "일상의 반복이", "score": 5},
            {"word": "특별한 변화 없을 것으로", "score": 6},
            {"word": "조용한 하루가 될 것으로", "score": 6}
        ],
        "consequence": [
            {"word": "크게 좋지도 나쁘지도 않습니다", "score": 5},
            {"word": "평범하게 하루를 마칠 수 있습니다", "score": 6},
            {"word": "기대 없이 보내면 편안할 것입니다", "score": 6}
        ],
        "advice": [
            {"word": "일상을 즐겨보세요", "score": 6},
            {"word": "새로운 도전을 준비하세요", "score": 5},
            {"word": "소소한 기쁨을 찾아보세요", "score": 5}
        ]
    },
    "good": {
        "probability": 0.15,
        "grade": 7,
        "event": [
            {"word": "기분 좋은 변화가", "score": 7},
            {"word": "좋은 사람을 만날 가능성이", "score": 8},
            {"word": "작은 행운이", "score": 7}
        ],
        "consequence": [
            {"word": "긍정적인 기운이 감돕니다", "score": 7},
            {"word": "좋은 일이 기대됩니다", "score": 8},
            {"word": "하루가 더 즐겁게 느껴질 것입니다", "score": 8}
        ],
        "advice": [
            {"word": "기회를 놓치지 마세요", "score": 8},
            {"word": "자신감을 가지세요", "score": 8},
            {"word": "오늘은 적극적으로 보내세요", "score": 7}
        ]
    },
    "best": {
        "probability": 0.05,
        "grade": 10,
        "event": [
            {"word": "큰 행운이", "score": 9},
            {"word": "꿈꾸던 기회가", "score": 10},
            {"word": "완벽한 하루가", "score": 10}
        ],
        "consequence": [
            {"word": "모든 것이 원하는 대로 흘러갈 것입니다", "score": 9},
            {"word": "인생 최고의 하루가 될 수 있습니다", "score": 9},
            {"word": "성공적인 결과를 기대할 수 있습니다", "score": 10}
        ],
        "advice": [
            {"word": "기회를 최대한 활용하세요", "score": 10},
            {"word": "행운을 믿고 도전하세요", "score": 10},
            {"word": "오늘을 즐기세요", "score": 9}
        ]
    }
}

sentence_pattern = "{event} 예상됩니다. {consequence}. {advice}."

def generate_fortune():
    selected_level = random.choices(
        list(fortune_data.keys()),
        weights=[level_info["probability"] for level_info in fortune_data.values()],
        k=1
    )[0]

    pattern = sentence_pattern
    total_score = 0

    for key in ["event", "consequence", "advice"]:
        chosen_word = random.choice(fortune_data[selected_level][key])
        pattern = pattern.replace(f"{{{key}}}", chosen_word["word"])
        total_score += chosen_word["score"]

    avg_score = total_score / 3
    return pattern, avg_score