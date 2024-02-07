import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
import requests
from dotenv import load_dotenv
import os
import json

# .env 파일에서 환경 변수 로드
load_dotenv()

# TODO: csv 따로 저장~@!
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def convert_coords_to_address(latitude, longitude):
    url = f'https://dapi.kakao.com/v2/local/geo/coord2address.json?x={longitude}&y={latitude}'
    db_host = os.getenv("KAKAO_API_KEY")
    print('kakao api host: ', db_host)
    headers = {'Authorization': f'KakaoAK {db_host}'}
    response = requests.get(url, headers=headers)
    try:
        address = response.json()['documents'][0]['address']['address_name']
        print('address from kakao: ', address)
        return address
    except (KeyError, IndexError):
        print('KAKAO API request failed!')
        return None

# API
def api_restaurants_within_onek(base_coords):
    longitude = base_coords[0]
    latitude = base_coords[1]
    given_address = convert_coords_to_address(latitude, longitude)
    # convert_coords_to_address에서 반환된 값이 None인 경우에 대한 처리
    if given_address is None:
        print("주소를 찾을 수 없습니다.")
        return []

    print('주소:', given_address)

    df = pd.read_csv('/Users/finallyfinn/Desktop/projects/krafton/backend-python/app/assets/swapped_coordinates.csv')
    df['address'] = df['address'].fillna('')
    second_word = given_address.split()[1]  # '강남구'
    filtered_data = df[df['address'].apply(lambda x: len(x.split()) > 1 and x.split()[1] == second_word)]

    print('second_word: ', second_word)
    print('filtered_data: ', filtered_data)

    gu_rest_dict_list = filtered_data.to_dict(orient='records')
    print(f'{second_word}에 있는 식당 수: ', len(gu_rest_dict_list))

    nearby_restaurants = []

    for result_dict in gu_rest_dict_list:
        coord_str = result_dict.get('coordinates')  # 두번째 옵션은 디폴트값 만약 첫번째 없을시에
        if coord_str and coord_str.lower() != 'none':
            coords = [to_float(coord) for coord in coord_str.replace("'", "").strip('[]').split(', ')]
            if None not in coords:
                distance = haversine(base_coords, (coords[0], coords[1]), unit=Unit.KILOMETERS)
                if distance <= 1:
                    nearby_restaurants.append(result_dict)

    #print('nearby_res within 1km: ', nearby_restaurants)
    print(f' 1km 이내의 식당 수: {len(nearby_restaurants)}')
    return nearby_restaurants

