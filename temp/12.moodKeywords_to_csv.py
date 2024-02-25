import csv

from pymongo import MongoClient

client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['restaurant']

documents_with_mood_keywords = collection.find({'$or': [
    {'moodKeywords': {'$exists': True, '$not': {'$size': 0}}},
    {'tempMood': {'$exists': True, '$type': 'array', '$not': {'$size': 0}}}
]})

# 결과를 담을 리스트 초기화
result_list = []

# 각 도큐먼트에서 '_id'와 'name' 컬럼 값을 추출하여 리스트에 추가
for document in documents_with_mood_keywords:
    _id = document['_id']
    name = document['name']
    address = document['address']

    if 'moodKeywords' in document and len(document['moodKeywords']) > 0:
        # moodKeywords가 존재하면 최대 두 번째 요소까지만 추가
        mood_keywords = document.get('moodKeywords')[:2]
    else:
        # moodKeywords가 존재하지 않을 때만 tempMood 추가
        if 'tempMood' in document and len(document['tempMood']) > 0:
            mood_keywords = document.get('tempMood')[:2]

    if mood_keywords:
        # 결과 리스트에 추가
        result_list.append({'_id': _id, 'name': name, 'address': address, 'moodKeywords': mood_keywords})

# 결과를 CSV 파일로 저장
csv_file_path = 'address_added.csv'
fieldnames = ['_id', 'name', 'address', 'moodKeywords']
with open(csv_file_path, mode='w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # CSV 파일 헤더 작성
    writer.writeheader()

    # 결과 리스트를 CSV 파일에 쓰기
    writer.writerows(result_list)

print(f"Results saved to {csv_file_path}")
