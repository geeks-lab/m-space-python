import requests
import pandas as pd

KAKAO_API_KEY = 'd381c5185416bd1f0e1808d306540f57'

def get_coordinates(address):
    base_url = 'https://dapi.kakao.com/v2/local/search/address.json'
    params = {'query': address }

    headers = {
        'Authorization': f'KakaoAK {KAKAO_API_KEY}'
    }

    response = requests.get(base_url, params=params, headers=headers)
    result = response.json()

    if 'documents' in result and result['documents']:
        coordinates = result['documents'][0]['x'], result['documents'][0]['y']
        return coordinates
    else:
        return None

# CSV 파일에서 주소를 읽어와서 좌표를 구하고, 결과를 새로운 'coordinates' 컬럼에 추가합니다.
def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['coordinates'] = df['address'].apply(get_coordinates)

    # 'coordinates' 열에서 None인 경우를 처리하여 적절한 값으로 대체합니다.
    df['coordinates'] = df['coordinates'].apply(lambda coord: [None, None] if coord is None else list(coord))

    # 'coordinates' 컬럼을 풀어서 'x'와 'y'로 나눕니다.
    df[['x', 'y']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)

    # 'coordinates' 컬럼 및 중간 단계의 'x', 'y' 컬럼을 제거합니다.
    df = df.drop(columns=['x', 'y'])

    # 결과를 CSV 파일로 저장합니다.
    df.to_csv(output_csv, index=False)

# 사용 예시
input_csv_file = 'quarter4.csv'
output_csv_file = 'coordinates_added_quarter4.csv'
process_csv(input_csv_file, output_csv_file)