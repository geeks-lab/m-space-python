import pandas as pd
from pymongo import MongoClient

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@mujuck.f8uwpet.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['review']

# MongoDB에서 데이터 조회
cursor = collection.find({}, {'_id': 0})  # _id 필드는 제외하고 조회합니다.

# 조회된 데이터를 DataFrame으로 변환
df = pd.DataFrame(list(cursor))

# DataFrame을 CSV 파일로 저장
df.to_csv('restaurant_data2.csv', index=False, encoding='utf-8')

# 결과 출력
print("CSV 파일로 저장되었습니다.")
