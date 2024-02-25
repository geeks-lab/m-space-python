import pandas as pd
from haversine import haversine, Unit

# CSV 파일 읽기
df = pd.read_csv('coordinates_added.csv')

# 주어진 문장
given_sentence = '서울 강남구 논현로175길 69 원영빌딩 1층'

# 주어진 문장의 처음 두 단어 추출
first_two_words = ' '.join(given_sentence.split()[:2])

# 'address' 컬럼에서 주어진 문장의 처음 두 단어로 시작하는 데이터 추출
filtered_data = df[df['address'].str.startswith(first_two_words, na=False)]

# 추출된 데이터의 모든 컬럼값을 딕셔너리로 저장
gu_rest_dict_list = filtered_data.to_dict(orient='records')
print(f'{first_two_words}에 있는 식당 수: ',len(gu_rest_dict_list))

# float로 형변환하는 함수
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

# 임의의 기준 식당 좌표
base_restaurant_coords = (37.5001716373021, 127.029070884291)

# 1km 이내에 있는 식당들을 저장할 리스트
nearby_restaurants = []

# coordinates 컬럼 값과 기준 식당 좌표 간의 거리 계산
for result_dict in gu_rest_dict_list:
    coord_str = result_dict.get('coordinates', '')
    if coord_str and coord_str.lower() != 'none':
        coords = [to_float(coord) for coord in coord_str.replace("'", "").strip('[]').split(', ')]
        if None not in coords:
            distance = haversine(base_restaurant_coords, (coords[1], coords[0]), unit=Unit.KILOMETERS)
        if distance <= 1:
            nearby_restaurants.append(result_dict)

num = 0

for nearby_restaurant in nearby_restaurants:
    print(nearby_restaurant)
    num += 1
print(f'{first_two_words}에 있는 1km 이내의 식당 수: {num}')
